# 2048 Game API: A FastAPI Backend for the Classic 2048 Puzzle Game

The 2048 Game API is a robust backend implementation of the popular 2048 puzzle game using FastAPI. This project provides a RESTful API that allows clients to create new games, make moves, and retrieve game states, enabling the development of various front-end interfaces or game bots.

The API is built with Python and FastAPI, offering high performance and easy-to-use endpoints for game management. It includes features such as concurrent game handling, move validation, and game state tracking. The project is designed with a focus on code quality, incorporating linting, type checking, and automated testing to ensure reliability and maintainability.

## Repository Structure

```
.
├── lefthook.yml
├── README.md
├── src
│   ├── __init__.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── game.py
│   └── frontend
│       └── index.html
└── tests
    ├── __init__.py
    └── test_app.py
```

Key Files:
- `src/app/app.py`: Main FastAPI application file containing API routes and game logic integration.
- `src/app/game.py`: Implementation of the 2048 game logic.
- `tests/test_app.py`: Comprehensive test suite for the API endpoints and game functionality.
- `lefthook.yml`: Configuration file for the Lefthook Git hooks manager, setting up pre-commit checks.

## Usage Instructions

### Installation

Prerequisites:
- Python 3.7+
- Poetry (for dependency management)

To set up the project:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd 2048-game-api
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Activate the virtual environment:
   ```
   poetry shell
   ```

### Running the Application

To start the FastAPI server:

```
uvicorn src.app.app:app --reload
```

The API will be available at `http://localhost:8000`.

### API Endpoints

1. Create a new game:
   ```
   POST /game/new
   ```
   Response:
   ```json
   {
     "game_id": "uuid",
     "state": {
       "board": [[0, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]],
       "score": 0,
       "game_over": false
     }
   }
   ```

2. Make a move:
   ```
   POST /game/move
   ```
   Request body:
   ```json
   {
     "game_id": "uuid",
     "direction": "up"
   }
   ```
   Response:
   ```json
   {
     "moved": true,
     "state": {
       "board": [[2, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]],
       "score": 4,
       "game_over": false
     }
   }
   ```

3. Get game state:
   ```
   GET /game/{game_id}
   ```
   Response:
   ```json
   {
     "board": [[2, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]],
     "score": 4,
     "game_over": false
   }
   ```

### Testing

To run the test suite:

```
pytest
```

### Troubleshooting

1. Issue: API returns 404 for all requests
   - Ensure the server is running and you're using the correct URL.
   - Check if the `STAGE` environment variable is set correctly.

2. Issue: Unable to make moves
   - Verify that you're sending a valid `game_id` and `direction` in the request body.
   - Check if the game has ended (`game_over: true` in the state).

3. Issue: Unexpected game behavior
   - Enable debug mode by setting `STAGE=development` in your environment.
   - Check the server logs for detailed error messages.

For more detailed debugging:
- Set `STAGE=development` to enable verbose logging.
- Inspect the logs in `stderr` for trace-level information.

## Data Flow

The 2048 Game API follows a straightforward request-response flow:

1. Client initiates a request (new game, move, or get state).
2. FastAPI routes the request to the appropriate endpoint handler.
3. The handler interacts with the `Game2048` class to perform game operations.
4. The game state is updated and stored in memory.
5. The response is formatted and sent back to the client.

```
Client <-> FastAPI Router <-> Endpoint Handlers <-> Game2048 Class
  ^                                                     ^
  |                                                     |
  +---------------------Memory Storage------------------+
```

Note: The current implementation stores game states in memory, which may not be suitable for production environments with high concurrency or persistence requirements.