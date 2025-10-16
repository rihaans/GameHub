from typing import Optional
from .constants import GameType
from .base_game import BaseGame
from .trivia_game import TriviaGame
from .word_chain_game import WordChainGame
from .rps_game import RockPaperScissorsGame

class GameFactory:
    @staticmethod
    def create_game(game_type: str, room_id: str) -> Optional[BaseGame]:
        try:
            game_type = GameType(game_type.lower())
        except ValueError:
            return None

        if game_type == GameType.TRIVIA:
            return TriviaGame(room_id)
        elif game_type == GameType.WORD_CHAIN:
            return WordChainGame(room_id)
        elif game_type == GameType.ROCK_PAPER_SCISSORS:
            return RockPaperScissorsGame(room_id)
            
        return None