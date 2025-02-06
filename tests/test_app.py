import os
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.app.app import app

from fastapi import HTTPException
from src.app.app import app, Game2048
from src.app.app import app, MoveRequest
from src.app.app import app, MoveRequest, games
from src.app.app import app, games
from src.app.app import app, games, Game2048
from src.app.game import Game2048
import concurrent.futures


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)



def test_get_game_state_edge_case_large_game_id(test_client):
    """
    Test get_game_state with a very large game ID.
    """
    large_id = "9" * 1000  # A string of 1000 nines
    response = test_client.get(f"/game/{large_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_get_game_state_empty_game_id(test_client):
    """
    Test get_game_state with an empty game ID.
    """
    response = test_client.get("/game/")
    assert response.status_code == 404


def test_get_game_state_exception_handling(test_client):
    """
    Test exception handling in get_game_state.
    """
    response = test_client.get("/game/nonexistent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_get_game_state_existing_game(test_client):
    """
    Test get_game_state when the game_id exists in games.
    """
    # Create a new game and add it to the games dictionary
    game = Game2048()
    game_id = "test_game_id"
    games[game_id] = game

    # Get the state of the existing game
    response = test_client.get(f"/game/{game_id}")

    # Assert that the response status code is 200
    assert response.status_code == 200
    # Assert that the response contains the expected game state
    expected_state = game.get_state()
    assert response.json() == expected_state

    # Clean up
    games.pop(game_id)


def test_get_game_state_incorrect_type(test_client):
    """
    Test get_game_state with an incorrect type for game ID.
    """
    response = test_client.get("/game/3.14")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_get_game_state_invalid_game_id(test_client):
    """
    Test get_game_state with an invalid game ID.
    """
    response = test_client.get("/game/invalid_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_get_game_state_non_existent_game(test_client):
    """
    Test get_game_state with a non-existent game ID.
    """
    response = test_client.get("/game/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_get_game_state_nonexistent_game(test_client):
    """
    Test get_game_state when the game_id does not exist in games.
    """
    # Ensure the games dictionary is empty
    games.clear()

    # Attempt to get the state of a non-existent game
    response = test_client.get("/game/nonexistent_id")

    # Assert that the response status code is 404
    assert response.status_code == 404
    # Assert that the response contains the expected error message
    assert response.json() == {"detail": "Game not found"}


def test_make_move_game_not_found(test_client):
    """
    Test make_move when the game_id does not exist in games.
    Expect a 404 HTTP exception with "Game not found" detail.
    """
    move_request = MoveRequest(direction="up", game_id="nonexistent_game_id")
    response = test_client.post("/game/move", json=move_request.dict())
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_make_move_game_over(test_client):
    """Test make_move when the game is over."""
    # Create a new game
    response = test_client.post("/game/new")
    game_id = response.json()["game_id"]

    # Mock the game to be in a game over state
    with patch.dict(games, {game_id: Game2048()}):
        games[game_id].board = [[2, 4, 8, 16],
                                [4, 8, 16, 32],
                                [8, 16, 32, 64],
                                [16, 32, 64, 128]]
        games[game_id].add_new_tile = lambda: None  # Prevent new tile from being added

        response = test_client.post("/game/move", json={"game_id": game_id, "direction": "up"})
        assert response.status_code == 200
        assert response.json()["moved"] == False
        assert response.json()["state"]["game_over"] == True


def test_make_move_invalid_direction(test_client):
    """Test make_move with an invalid direction."""
    # Create a new game
    response = test_client.post("/game/new")
    game_id = response.json()["game_id"]

    # Attempt to make a move with an invalid direction
    response = test_client.post("/game/move", json={"game_id": game_id, "direction": "invalid"})
    assert response.status_code == 400
    assert "Invalid direction" in response.json()["detail"]


def test_make_move_invalid_direction_type(test_client):
    """Test make_move with an invalid direction type."""
    # Create a new game
    response = test_client.post("/game/new")
    game_id = response.json()["game_id"]

    response = test_client.post("/game/move", json={"game_id": game_id, "direction": 123})
    assert response.status_code == 422


def test_make_move_invalid_game_id_type(test_client):
    """Test make_move with an invalid game ID type."""
    response = test_client.post("/game/move", json={"game_id": 123, "direction": "up"})
    assert response.status_code == 422


def test_make_move_missing_direction(test_client):
    """Test make_move with a missing direction."""
    # Create a new game
    response = test_client.post("/game/new")
    game_id = response.json()["game_id"]

    response = test_client.post("/game/move", json={"game_id": game_id})
    assert response.status_code == 422


def test_make_move_missing_game_id(test_client):
    """Test make_move with a missing game ID."""
    response = test_client.post("/game/move", json={"direction": "up"})
    assert response.status_code == 422


def test_make_move_nonexistent_game(test_client):
    """Test make_move with a non-existent game ID."""
    response = test_client.post("/game/move", json={"game_id": "nonexistent", "direction": "up"})
    assert response.status_code == 404
    assert "Game not found" in response.json()["detail"]


def test_make_move_valid_game():
    """
    Test making a valid move in an existing game.
    """
    client = TestClient(app)

    # Create a new game
    response = client.post("/game/new")
    assert response.status_code == 200
    game_data = response.json()
    game_id = game_data["game_id"]

    # Make a move
    move_request = MoveRequest(direction="right", game_id=game_id)
    response = client.post("/game/move", json=move_request.dict())
    
    assert response.status_code == 200
    move_data = response.json()
    
    assert "moved" in move_data
    assert isinstance(move_data["moved"], bool)
    assert "state" in move_data
    assert isinstance(move_data["state"], dict)
    assert "board" in move_data["state"]
    assert "score" in move_data["state"]
    assert "game_over" in move_data["state"]

    # Clean up
    del games[game_id]


def test_new_game_concurrent_requests(test_client):
    """
    Test that concurrent requests to create new games are handled correctly.
    """

    def create_game():
        return test_client.post("/game/new")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_game) for _ in range(100)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]

    game_ids = [response.json()["game_id"] for response in responses]
    assert len(set(game_ids)) == 100


def test_new_game_creates_game_and_returns_initial_state(test_client):
    """
    Test that new_game() creates a new game, assigns a game_id, and returns the initial state.
    """
    response = test_client.post("/game/new")
    assert response.status_code == 200
    
    data = response.json()
    assert "game_id" in data
    assert "state" in data
    
    state = data["state"]
    assert "board" in state
    assert "score" in state
    assert "game_over" in state
    
    assert len(state["board"]) == 4
    assert all(len(row) == 4 for row in state["board"])
    assert state["score"] == 0
    assert state["game_over"] is False
    
    # Check that the board has exactly two non-zero tiles
    non_zero_tiles = sum(tile != 0 for row in state["board"] for tile in row)
    assert non_zero_tiles == 2


@patch("src.app.app.Game2048")
def test_new_game_exception_handling(mock_game_2048, test_client):
    """
    Test that exceptions during game creation are handled properly.
    """
    # Setup the mock to raise an exception
    mock_game_2048.side_effect = Exception("Game creation failed")
    
    # Make the request and verify the error response
    response = test_client.post("/game/new")
    
    # Assert that the response indicates an error
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

def test_new_game_initial_state(test_client):
    """
    Test that the initial state of a new game is correct.
    """
    response = test_client.post("/game/new")
    data = response.json()
    state = data["state"]
    
    assert state["score"] == 0
    assert state["game_over"] == False
    assert len(state["board"]) == 4
    assert len(state["board"][0]) == 4
    
    # Check that the board has exactly two non-zero tiles
    non_zero_tiles = sum(tile != 0 for row in state["board"] for tile in row)
    assert non_zero_tiles == 2


def test_new_game_memory_leak(test_client):
    """
    Test that creating many new games doesn't cause a memory leak.
    """
    initial_game_count = len(games)
    for _ in range(1000):
        test_client.post("/game/new")
    
    assert len(games) == initial_game_count + 1000


def test_new_game_success(test_client):
    """
    Test that a new game is created successfully with the correct response format.
    """
    response = test_client.post("/game/new")
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "state" in data
    assert isinstance(data["state"], dict)
    assert "board" in data["state"]
    assert "score" in data["state"]
    assert "game_over" in data["state"]


def test_new_game_unique_ids(test_client):
    """
    Test that multiple new games created have unique game IDs.
    """
    response1 = test_client.post("/game/new")
    response2 = test_client.post("/game/new")
    
    assert response1.json()["game_id"] != response2.json()["game_id"]


def test_make_move_negative_cases(test_client):
    """
    Test negative cases for the make_move function.
    """
    # Test with non-existent game ID
    move_request = MoveRequest(direction="up", game_id="nonexistent_id")
    response = test_client.post("/game/move", json=move_request.dict())
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}

    # Test with invalid direction
    response = test_client.post("/game/new")
    game_id = response.json()["game_id"]
    move_request = MoveRequest(direction="invalid", game_id=game_id)
    response = test_client.post("/game/move", json=move_request.dict())
    assert response.status_code == 400
    assert "Invalid direction" in response.json()["detail"]

    # Test with missing direction
    response = test_client.post("/game/move", json={"game_id": game_id})
    assert response.status_code == 422

    # Test with missing game_id
    response = test_client.post("/game/move", json={"direction": "up"})
    assert response.status_code == 422

    # Clean up
    del games[game_id]
