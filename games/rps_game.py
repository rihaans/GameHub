from typing import Dict, Any, List
from .base_game import BaseGame
from .constants import GameStatus, PlayerAction

class RockPaperScissorsGame(BaseGame):
    def __init__(self, room_id: str):
        super().__init__(room_id, max_players=2)  # RPS is 2 player only
        self.moves: Dict[str, str] = {}
        self.rounds: List[Dict[str, Any]] = []
        self.max_rounds = 5

    def can_start(self) -> bool:
        return len(self.players) == 2 and self.are_all_players_ready()

    def handle_action(self, player_id: str, action: PlayerAction, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == PlayerAction.CHOOSE:
            return self._handle_move(player_id, data.get("move", "").lower())
        return {"error": "Invalid action"}

    def _handle_move(self, player_id: str, move: str) -> Dict[str, Any]:
        if self.status != GameStatus.IN_PROGRESS:
            return {"error": "Game not in progress"}

        if move not in ["rock", "paper", "scissors"]:
            return {"error": "Invalid move"}

        if player_id in self.moves:
            return {"error": "Already made a move this round"}

        self.moves[player_id] = move

        if len(self.moves) == 2:
            return self._resolve_round()

        return {"success": True, "waiting": True}

    def _resolve_round(self) -> Dict[str, Any]:
        players = list(self.players.keys())
        move1, move2 = self.moves[players[0]], self.moves[players[1]]
        
        winner = None
        if move1 != move2:
            if (
                (move1 == "rock" and move2 == "scissors") or
                (move1 == "paper" and move2 == "rock") or
                (move1 == "scissors" and move2 == "paper")
            ):
                winner = players[0]
                self.update_score(players[0], 1)
            else:
                winner = players[1]
                self.update_score(players[1], 1)

        # Record the round
        self.rounds.append({
            "moves": self.moves.copy(),
            "winner": winner
        })
        self.moves.clear()

        # Check if game should end
        scores = self.get_scores()
        max_score = max(scores.values())
        rounds_left = self.max_rounds - len(self.rounds)
        
        if max_score > self.max_rounds // 2 or rounds_left == 0:
            self.status = GameStatus.FINISHED
            self.winner = max(scores.items(), key=lambda x: x[1])[0]

        return {
            "success": True,
            "round_winner": winner,
            "game_finished": self.status == GameStatus.FINISHED
        }

    def get_state(self, player_id: str = None) -> Dict[str, Any]:
        state = {
            "status": self.status.value,
            "players": self.players,
            "scores": self.get_scores(),
            "current_round": len(self.rounds) + 1,
            "max_rounds": self.max_rounds,
            "rounds": self.rounds
        }

        if self.status == GameStatus.IN_PROGRESS:
            if player_id:
                state["made_move"] = player_id in self.moves
                if player_id in self.moves:
                    state["my_move"] = self.moves[player_id]
            state["waiting_for"] = [
                pid for pid in self.players.keys() 
                if pid not in self.moves
            ]

        if self.status == GameStatus.FINISHED:
            state["winner"] = self.winner
            state["winner_name"] = self.players[self.winner]["name"]

        return state