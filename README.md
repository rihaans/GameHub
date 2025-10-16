# GameHub - Redis-Powered Multiplayer Game Framework

A real-time multiplayer game framework built with Python and Redis, using the pub/sub pattern for seamless game state synchronization and player interactions.

## 🎮 Features

- **Multiple Game Types:**

  - Trivia Quiz
  - Word Chain
  - Rock Paper Scissors
  - Easily extensible for new games

- **Real-time Multiplayer:**

  - Instant state synchronization
  - Player join/leave handling
  - Ready system for game start
  - Turn-based game support

- **Game Room Management:**
  - Create/join game rooms
  - Player state tracking
  - Score management
  - Game state broadcasting

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Redis server (Memurai for Windows)
- Required Python packages:

```bash
pip install -r requirements.txt
```

### Running the Games

1. Start Redis server (Memurai on Windows)

2. Start the game room manager:

```bash
python game_room_manager.py
```

3. Start player clients (in separate terminals):

```bash
python game_player.py PlayerName
```

## 🎲 Available Games

### 1. Trivia Quiz

- Multiplayer quiz game
- Multiple choice questions
- Points for correct answers
- Real-time score tracking

### 2. Word Chain

- Take turns making words
- Each word must start with the last letter of the previous word
- Points based on word length
- Built-in dictionary validation

### 3. Rock Paper Scissors

- Classic 2-player game
- Best of 5 rounds
- Real-time move resolution
- Complete match history

## 🏗 Project Structure

```
GameHub/
├── games/                      # Game implementations
│   ├── __init__.py
│   ├── base_game.py           # Base game class
│   ├── constants.py           # Game enums and constants
│   ├── game_factory.py        # Game instance creator
│   ├── trivia_game.py        # Trivia game implementation
│   ├── word_chain_game.py    # Word chain game implementation
│   └── rps_game.py           # Rock Paper Scissors implementation
├── config.py                  # Redis and channel configuration
├── game_room_manager.py       # Game room and state manager
├── game_player.py            # Player client implementation
└── requirements.txt          # Project dependencies
```

## 🎯 Game Actions

### Trivia Game

```python
# Answer a question
action: "answer"
data: {"answer": "Paris"}
```

### Word Chain Game

```python
# Submit a word
action: "move"
data: {"word": "elephant"}
```

### Rock Paper Scissors

```python
# Make a move
action: "choose"
data: {"move": "rock"}
```

## 🔧 Adding New Games

1. Create a new game class extending `BaseGame`
2. Implement required methods:
   - `can_start()`
   - `handle_action()`
   - `get_state()`
3. Add game type to `GameType` enum
4. Register game in `GameFactory`

## 📝 License

MIT License - feel free to use and modify for your own projects!

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add new games
- Improve existing games
- Fix bugs
- Enhance documentation
