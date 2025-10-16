from enum import Enum

class GameType(Enum):
    TRIVIA = "trivia"
    WORD_CHAIN = "word_chain"
    TIC_TAC_TOE = "tic_tac_toe"
    NUMBER_GUESS = "number_guess"
    ROCK_PAPER_SCISSORS = "rock_paper_scissors"

class GameStatus(Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class PlayerAction(Enum):
    JOIN = "join"
    LEAVE = "leave"
    MOVE = "move"
    ANSWER = "answer"
    GUESS = "guess"
    CHOOSE = "choose"