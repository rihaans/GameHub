# Game configuration settings
from enum import Enum

# Redis channels
GAME_ROOM_CHANNEL = 'game_rooms'
PLAYER_STATE_CHANNEL = 'player_states'
MATCHMAKING_CHANNEL = 'matchmaking'
GAME_STATE_CHANNEL = 'game_states'

# Game settings
MAX_PLAYERS_PER_ROOM = 4
MIN_PLAYERS_TO_START = 2
MATCHMAKING_TIMEOUT = 30  # seconds
GAME_ROUND_TIME = 60  # seconds

# Game states
class GameState(Enum):
    WAITING = "waiting"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

# Player states
class PlayerState(Enum):
    IDLE = "idle"
    MATCHMAKING = "matchmaking"
    IN_GAME = "in_game"
    READY = "ready"
    NOT_READY = "not_ready"