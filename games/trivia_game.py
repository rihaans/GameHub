import random
from typing import Dict, Any, List
from .base_game import BaseGame
from .constants import GameStatus, PlayerAction

class TriviaGame(BaseGame):
    def __init__(self, room_id: str, max_players: int = 4):
        super().__init__(room_id, max_players)
        self.questions = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct": "Paris"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": "Mars"
            },
            {
                "question": "What is the largest mammal in the world?",
                "options": ["African Elephant", "Blue Whale", "Giraffe", "Polar Bear"],
                "correct": "Blue Whale"
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["Van Gogh", "Da Vinci", "Picasso", "Rembrandt"],
                "correct": "Da Vinci"
            }
        ]
        self.current_question = 0
        self.answers: Dict[str, str] = {}

    def can_start(self) -> bool:
        return len(self.players) >= 2 and self.are_all_players_ready()

    def handle_action(self, player_id: str, action: PlayerAction, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == PlayerAction.ANSWER:
            return self._handle_answer(player_id, data.get("answer", ""))
        return {"error": "Invalid action"}

    def _handle_answer(self, player_id: str, answer: str) -> Dict[str, Any]:
        if self.status != GameStatus.IN_PROGRESS:
            return {"error": "Game not in progress"}

        if player_id in self.answers:
            return {"error": "Already answered"}

        self.answers[player_id] = answer
        current_q = self.questions[self.current_question]
        
        if answer == current_q["correct"]:
            self.update_score(player_id, 10)

        if len(self.answers) == len(self.players):
            self._advance_question()

        return {
            "success": True,
            "correct": answer == current_q["correct"],
            "points": 10 if answer == current_q["correct"] else 0
        }

    def _advance_question(self) -> None:
        self.answers.clear()
        self.current_question += 1
        
        if self.current_question >= len(self.questions):
            self.status = GameStatus.FINISHED
            scores = self.get_scores()
            self.winner = max(scores.items(), key=lambda x: x[1])[0]

    def get_state(self, player_id: str = None) -> Dict[str, Any]:
        state = {
            "status": self.status.value,
            "players": self.players,
            "scores": self.get_scores(),
            "current_question": self.current_question,
            "total_questions": len(self.questions)
        }

        if self.status == GameStatus.IN_PROGRESS:
            current_q = self.questions[self.current_question]
            state["question"] = {
                "text": current_q["question"],
                "options": current_q["options"]
            }
            if player_id:
                state["answered"] = player_id in self.answers

        if self.status == GameStatus.FINISHED:
            state["winner"] = self.winner
            state["winner_name"] = self.players[self.winner]["name"]

        return state