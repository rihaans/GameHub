from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import redis
import json
import uuid
from config import *

app = FastAPI()
app.mount('/static', StaticFiles(directory='web/static'), name='static')
templates = Jinja2Templates(directory='web/templates')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

connected = {}  # websocket -> player_id

async def redis_subscriber_loop(broadcast_queue: asyncio.Queue):
    pubsub = r.pubsub()
    pubsub.subscribe(GAME_STATE_CHANNEL)
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                data = json.loads(message['data'])
            except Exception:
                data = {'raw': message['data']}
            await broadcast_queue.put({'type': 'game_state', 'data': data})
        await asyncio.sleep(0.1)

@app.on_event('startup')
async def startup_event():
    app.state.broadcast_queue = asyncio.Queue()
    app.state.redis_task = asyncio.create_task(redis_subscriber_loop(app.state.broadcast_queue))

@app.on_event('shutdown')
async def shutdown_event():
    app.state.redis_task.cancel()

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    name = params.get('name', 'Player')
    player_id = str(uuid.uuid4())
    connected[websocket] = player_id
    # send welcome
    await websocket.send_text(json.dumps({'type': 'welcome', 'player_id': player_id, 'name': name}))

    try:
        while True:
            # check redis broadcast queue
            try:
                msg = app.state.broadcast_queue.get_nowait()
                # forward to all connected websockets
                for ws in list(connected.keys()):
                    try:
                        await ws.send_text(json.dumps(msg))
                    except Exception:
                        pass
            except asyncio.QueueEmpty:
                pass

            # check for client messages
            try:
                client_msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                await asyncio.sleep(0.05)
                continue

            try:
                data = json.loads(client_msg)
            except Exception:
                await websocket.send_text(json.dumps({'type': 'error', 'message': 'invalid json'}))
                continue

            # handle client messages: create/join/ready/action
            typ = data.get('type')
            if typ == 'create':
                game_type = data.get('game_type')
                # publish to join channel with player_name
                payload = {
                    'player_id': player_id,
                    'player_name': name,
                    'game_type': game_type
                }
                r.publish(GAME_JOIN_CHANNEL, json.dumps(payload))
            elif typ == 'join':
                payload = {
                    'room_id': data.get('room_id'),
                    'player_id': player_id,
                    'player_name': name
                }
                r.publish(GAME_JOIN_CHANNEL, json.dumps(payload))
            elif typ == 'ready':
                payload = {
                    'room_id': data.get('room_id'),
                    'player_id': player_id,
                    'ready': data.get('ready', True)
                }
                r.publish(GAME_READY_CHANNEL, json.dumps(payload))
            elif typ == 'action':
                payload = {
                    'room_id': data.get('room_id'),
                    'player_id': player_id,
                    'action': data.get('action'),
                    'data': data.get('data', {})
                }
                r.publish(GAME_ACTION_CHANNEL, json.dumps(payload))
            else:
                await websocket.send_text(json.dumps({'type': 'error', 'message': 'unknown message type'}))

    except WebSocketDisconnect:
        connected.pop(websocket, None)
    except Exception as e:
        connected.pop(websocket, None)
        try:
            await websocket.close()
        except Exception:
            pass

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('web.server:app', host='0.0.0.0', port=8000, reload=False)
