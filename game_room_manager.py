import redis
import json
import time
import uuid
from game_config import *
from config import REDIS_HOST, REDIS_PORT

class GameRoom:
    def __init__(self, room_id, game_type, max_players=MAX_PLAYERS_PER_ROOM):
        self.room_id = room_id
        self.game_type = game_type
        self.max_players = max_players
        self.players = {}  # player_id: {name, state, score}
        self.state = GameState.WAITING
        self.scores = {}
        self.start_time = None

    def to_json(self):
        return {
            'room_id': self.room_id,
            'game_type': self.game_type,
            'players': self.players,
            'state': self.state.value,
            'scores': self.scores,
            'start_time': self.start_time
        }

class GameRoomManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            decode_responses=True
        )
        self.rooms = {}  # room_id: GameRoom
        self.player_room_map = {}  # player_id: room_id

    def create_room(self, game_type):
        room_id = str(uuid.uuid4())
        room = GameRoom(room_id, game_type)
        self.rooms[room_id] = room
        self._broadcast_room_update(room)
        return room_id

    def join_room(self, room_id, player_id, player_name):
        if room_id not in self.rooms:
            return False, "Room not found"
        
        room = self.rooms[room_id]
        if len(room.players) >= room.max_players:
            return False, "Room is full"
        
        room.players[player_id] = {
            'name': player_name,
            'state': PlayerState.NOT_READY.value,
            'score': 0
        }
        self.player_room_map[player_id] = room_id
        self._broadcast_room_update(room)
        return True, "Joined successfully"

    def leave_room(self, player_id):
        if player_id not in self.player_room_map:
            return False, "Player not in any room"
        
        room_id = self.player_room_map[player_id]
        room = self.rooms[room_id]
        del room.players[player_id]
        del self.player_room_map[player_id]
        
        if len(room.players) == 0:
            del self.rooms[room_id]
        else:
            self._broadcast_room_update(room)
        return True, "Left successfully"

    def update_player_state(self, player_id, new_state):
        if player_id not in self.player_room_map:
            return False, "Player not in any room"
        
        room_id = self.player_room_map[player_id]
        room = self.rooms[room_id]
        room.players[player_id]['state'] = new_state.value
        
        # Check if all players are ready
        if all(p['state'] == PlayerState.READY.value for p in room.players.values()):
            if len(room.players) >= MIN_PLAYERS_TO_START:
                self._start_game(room)
        
        self._broadcast_room_update(room)
        return True, "State updated"

    def update_score(self, player_id, score_delta):
        if player_id not in self.player_room_map:
            return False, "Player not in any room"
        
        room_id = self.player_room_map[player_id]
        room = self.rooms[room_id]
        room.players[player_id]['score'] += score_delta
        self._broadcast_room_update(room)
        return True, "Score updated"

    def _start_game(self, room):
        room.state = GameState.IN_PROGRESS
        room.start_time = time.time()
        self._broadcast_room_update(room)

    def _broadcast_room_update(self, room):
        self.redis.publish(GAME_STATE_CHANNEL, json.dumps(room.to_json()))

    def run(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe([MATCHMAKING_CHANNEL, PLAYER_STATE_CHANNEL])
        
        print("🎮 Game Room Manager is running...")
        
        for message in pubsub.listen():
            if message['type'] != 'message':
                continue
                
            data = json.loads(message['data'])
            channel = message['channel']
            
            if channel == MATCHMAKING_CHANNEL:
                self._handle_matchmaking(data)
            elif channel == PLAYER_STATE_CHANNEL:
                self._handle_player_state(data)

    def _handle_matchmaking(self, data):
        action = data.get('action')
        player_id = data.get('player_id')
        
        if action == 'create':
            room_id = self.create_room(data.get('game_type'))
            success, msg = self.join_room(room_id, player_id, data.get('player_name'))
        elif action == 'join':
            success, msg = self.join_room(data.get('room_id'), player_id, data.get('player_name'))
        elif action == 'leave':
            success, msg = self.leave_room(player_id)

    def _handle_player_state(self, data):
        player_id = data.get('player_id')
        new_state = PlayerState(data.get('state'))
        self.update_player_state(player_id, new_state)

if __name__ == '__main__':
    manager = GameRoomManager()
    manager.run()