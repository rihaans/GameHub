from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .constants import GameStatus, PlayerAction

class BaseGame(ABC):
    def __init__(self, room_id: str, max_players: int = 4):
        self.room_id = room_id
        self.max_players = max_players
        self.players: Dict[str, Dict[str, Any]] = {}
        self.status = GameStatus.WAITING
        self.current_turn: str = None
        self.winner: str = None
        self.game_data: Dict[str, Any] = {}

    @abstractmethod
    def can_start(self) -> bool:
        """Check if the game can start with current players."""
        pass

    @abstractmethod
    def handle_action(self, player_id: str, action: PlayerAction, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a player's action and return the result."""
        pass

    @abstractmethod
    def get_state(self, player_id: str = None) -> Dict[str, Any]:
        """Get the current game state, optionally filtered for specific player."""
        pass

    def add_player(self, player_id: str, player_name: str) -> bool:
        """Add a player to the game."""
        if len(self.players) >= self.max_players:
            return False
        self.players[player_id] = {
            "name": player_name,
            "score": 0,
            "ready": False
        }
        return True

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False

    def set_player_ready(self, player_id: str, ready: bool = True) -> None:
        """Set player's ready status."""
        if player_id in self.players:
            self.players[player_id]["ready"] = ready

    def are_all_players_ready(self) -> bool:
        """Check if all players are ready."""
        return all(player["ready"] for player in self.players.values())

    def update_score(self, player_id: str, points: int) -> None:
        """Update a player's score."""
        if player_id in self.players:
            self.players[player_id]["score"] += points

    def get_scores(self) -> Dict[str, int]:
        """Get all players' scores."""
        return {pid: data["score"] for pid, data in self.players.items()}