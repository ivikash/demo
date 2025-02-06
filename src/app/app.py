"""FastAPI backend for 2048 game."""

import os
import sys
import logging
from pathlib import Path
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from pydantic import BaseModel

from .game import Game2048

load_dotenv()
stage = os.getenv("STAGE", "production")

try:
    if stage == "development":
        logger.remove()
        logger.add(sys.stderr, level="TRACE")
except Exception as e:
    logger.error(f"Error configuring logger for development: {e}")

config_path = Path(__file__).parent / "core" / "logging" / "logging_config.json"

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app = FastAPI(title="2048 Game API", debug=stage == "development")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Store active games
games = {}

class MoveRequest(BaseModel):
    direction: str
    game_id: str

@app.post("/game/new")
async def new_game():
    try:
        game = Game2048()
        game_id = str(uuid.uuid4())
        games[game_id] = game
        logger.info(f"New game created with ID: {game_id}")
        return {"game_id": game_id, "state": game.get_state()}
    except Exception as e:
        logger.error(f"Error creating new game: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/game/move")
async def make_move(move_request: MoveRequest) -> dict:
    """Make a move in the specified direction."""
    game_id = move_request.game_id
    logger.info(f"Received move request for game {game_id}: {move_request.direction}")
    if game_id not in games:
        logger.warning(f"Game not found: {game_id}")
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    try:
        moved = game.move(move_request.direction)
        state = game.get_state()
        if game.is_game_over():
            logger.info(f"Game {game_id} is over with final score {state['score']}")
        return {"moved": moved, "state": state}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/game/{game_id}")
async def get_game_state(game_id: str) -> dict:
    """Get the current state of a game."""
    logger.debug(f"Getting state for game {game_id}")
    if game_id not in games:
        logger.warning(f"Game not found: {game_id}")
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id].get_state()
