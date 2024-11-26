"""FastAPI backend for 2048 game."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from .game import Game2048

load_dotenv()
stage = os.getenv("STAGE")

if stage == "development":
    logger.remove()
    logger.add(sys.stderr, level="TRACE")

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
async def new_game() -> dict:
    """Start a new game and return the initial state."""
    game = Game2048()
    game_id = str(len(games))
    games[game_id] = game
    return {"game_id": game_id, "state": game.get_state()}

@app.post("/game/move")
async def make_move(move_request: MoveRequest) -> dict:
    """Make a move in the specified direction."""
    game_id = move_request.game_id
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    try:
        moved = game.move(move_request.direction)
        return {"moved": moved, "state": game.get_state()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/game/{game_id}")
async def get_game_state(game_id: str) -> dict:
    """Get the current state of a game."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id].get_state()
