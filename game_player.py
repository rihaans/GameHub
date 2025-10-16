import redis
import json
import uuid
import time
import sys
from game_config import *
from config import REDIS_HOST, REDIS_PORT

class GamePlayer:
    def __init__(self, name):
        self.player_id = str(uuid.uuid4())
        self.name = name
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        self.current_room = None
        self.state = PlayerState.IDLE
        
    def create_game(self, game_type):
        message = {
            'action': 'create',
            'player_id': self.player_id,
            'player_name': self.name,
            'game_type': game_type
        }
        self.redis.publish(MATCHMAKING_CHANNEL, json.dumps(message))
        
    def join_game(self, room_id):
        message = {
            'action': 'join',
            'player_id': self.player_id,
            'player_name': self.name,
            'room_id': room_id
        }
        self.redis.publish(MATCHMAKING_CHANNEL, json.dumps(message))
        self.current_room = room_id
        
    def leave_game(self):
        if not self.current_room:
            return
            
        message = {
            'action': 'leave',
            'player_id': self.player_id
        }
        self.redis.publish(MATCHMAKING_CHANNEL, json.dumps(message))
        self.current_room = None
        
    def set_ready(self, is_ready=True):
        if not self.current_room:
            return
            
        new_state = PlayerState.READY if is_ready else PlayerState.NOT_READY
        message = {
            'player_id': self.player_id,
            'state': new_state.value
        }
        self.redis.publish(PLAYER_STATE_CHANNEL, json.dumps(message))
        
    def submit_score(self, score):
        if not self.current_room:
            return
            
        message = {
            'player_id': self.player_id,
            'score': score
        }
        self.redis.publish(PLAYER_STATE_CHANNEL, json.dumps(message))
        
    def monitor_game_state(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(GAME_STATE_CHANNEL)
        
        print(f"🎮 Player {self.name} ({self.player_id}) is active...")
        
        for message in pubsub.listen():
            if message['type'] != 'message':
                continue
                
            game_state = json.loads(message['data'])
            if self.current_room and game_state['room_id'] == self.current_room:
                self._handle_game_update(game_state)
                
    def _handle_game_update(self, game_state):
        state = GameState(game_state['state'])
        players = game_state['players']
        
        # Print game state update
        print(f"\n📊 Game Room Update:")
        print(f"State: {state.value}")
        print("Players:")
        for pid, pdata in players.items():
            status = "👑 " if pid == self.player_id else "👤 "
            print(f"{status}{pdata['name']} - Status: {pdata['state']} - Score: {pdata['score']}")
            
        if state == GameState.IN_PROGRESS:
            print("🎮 Game is in progress!")
            
def main():
    if len(sys.argv) < 2:
        print("Please provide player name as argument")
        sys.exit(1)
        
    player_name = sys.argv[1]
    player = GamePlayer(player_name)
    
    # Simple command menu
    print("\nCommands:")
    print("1. Create new game room")
    print("2. Join existing room")
    print("3. Toggle ready status")
    print("4. Leave room")
    print("5. Submit score (test)")
    print("q. Quit")
    
    try:
        while True:
            cmd = input("\nEnter command: ").strip()
            
            if cmd == '1':
                game_type = input("Enter game type: ")
                player.create_game(game_type)
            elif cmd == '2':
                room_id = input("Enter room ID: ")
                player.join_game(room_id)
            elif cmd == '3':
                player.set_ready()
            elif cmd == '4':
                player.leave_game()
            elif cmd == '5':
                score = int(input("Enter score: "))
                player.submit_score(score)
            elif cmd.lower() == 'q':
                break
            
            # Monitor game state for a short while after each command
            pubsub = player.redis.pubsub()
            pubsub.subscribe(GAME_STATE_CHANNEL)
            timeout = time.time() + 2  # Monitor for 2 seconds
            
            while time.time() < timeout:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    game_state = json.loads(message['data'])
                    if player.current_room and game_state['room_id'] == player.current_room:
                        player._handle_game_update(game_state)
                time.sleep(0.1)
            
            pubsub.unsubscribe()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        player.leave_game()

if __name__ == '__main__':
    main()