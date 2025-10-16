import random
from typing import Dict, Any, List
from .base_game import BaseGame
from .constants import GameStatus, PlayerAction

class WordChainGame(BaseGame):
    def __init__(self, room_id: str, max_players: int = 4):
        super().__init__(room_id, max_players)
        self.words_used = []
        self.current_letter = None
        self.round = 0
        self.time_limit = 30  # seconds per turn
        self.min_word_length = 3
        self.dictionary = set([
            "apple", "banana", "cat", "dog", "elephant", "fish", "giraffe",
            "house", "ice", "jacket", "king", "lion", "monkey", "nest",
            "orange", "penguin", "queen", "rabbit", "snake", "tiger",
            "umbrella", "violet", "whale", "xylophone", "yellow", "zebra"
        ])  # In a real implementation, this would be loaded from a file

    def can_start(self) -> bool:
        return len(self.players) >= 2 and self.are_all_players_ready()

    def start_game(self) -> None:
        if not self.can_start():
            return

        self.status = GameStatus.IN_PROGRESS
        player_ids = list(self.players.keys())
        self.current_turn = random.choice(player_ids)
        starting_words = [w for w in self.dictionary if len(w) >= self.min_word_length]
        self.current_letter = random.choice(starting_words)[0]

    def handle_action(self, player_id: str, action: PlayerAction, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == PlayerAction.MOVE:
            return self._handle_word(player_id, data.get("word", "").lower())
        return {"error": "Invalid action"}

    def _handle_word(self, player_id: str, word: str) -> Dict[str, Any]:
        if self.status != GameStatus.IN_PROGRESS:
            return {"error": "Game not in progress"}

        if player_id != self.current_turn:
            return {"error": "Not your turn"}

        if len(word) < self.min_word_length:
            return {"error": f"Word must be at least {self.min_word_length} characters"}

        if word in self.words_used:
            return {"error": "Word already used"}

        if not word.startswith(self.current_letter):
            return {"error": f"Word must start with '{self.current_letter}'"}

        if word not in self.dictionary:
            return {"error": "Word not in dictionary"}

        # Valid move
        self.words_used.append(word)
        self.current_letter = word[-1]
        self.update_score(player_id, len(word))
        self._next_turn()

        return {
            "success": True,
            "points": len(word),
            "next_letter": self.current_letter
        }

    def _next_turn(self) -> None:
        player_ids = list(self.players.keys())
        current_idx = player_ids.index(self.current_turn)
        next_idx = (current_idx + 1) % len(player_ids)
        self.current_turn = player_ids[next_idx]
        self.round += 1

        # Check if game should end
        available_words = [
            w for w in self.dictionary 
            if w.startswith(self.current_letter) 
            and w not in self.words_used
            and len(w) >= self.min_word_length
        ]

        if not available_words:
            self.status = GameStatus.FINISHED
            scores = self.get_scores()
            self.winner = max(scores.items(), key=lambda x: x[1])[0]

    def get_state(self, player_id: str = None) -> Dict[str, Any]:
        state = {
            "status": self.status.value,
            "players": self.players,
            "scores": self.get_scores(),
            "round": self.round,
            "words_used": self.words_used,
            "current_letter": self.current_letter,
            "current_turn": self.current_turn
        }

        if self.status == GameStatus.IN_PROGRESS:
            state["current_player_name"] = self.players[self.current_turn]["name"]
            if player_id:
                state["is_my_turn"] = player_id == self.current_turn

        if self.status == GameStatus.FINISHED:
            state["winner"] = self.winner
            state["winner_name"] = self.players[self.winner]["name"]

        return state