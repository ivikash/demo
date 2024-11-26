"""2048 game logic implementation."""
import random


class Game2048:
    def __init__(self, size: int = 4):
        self.size = size
        self.score = 0
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.add_new_tile()
        self.add_new_tile()
    
    def add_new_tile(self) -> None:
        """Add a new tile (2 or 4) to a random empty cell."""
        empty_cells = [
            (i, j) for i in range(self.size) 
            for j in range(self.size) if self.board[i][j] == 0
        ]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def is_game_over(self) -> bool:
        """Check if no moves are possible."""
        # Check for empty cells
        if any(0 in row for row in self.board):
            return False
        
        # Check for possible merges horizontally
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return False
        
        # Check for possible merges vertically
        for i in range(self.size - 1):
            for j in range(self.size):
                if self.board[i][j] == self.board[i + 1][j]:
                    return False
        
        return True

    def move(self, direction: str) -> bool:
        """Move tiles in the specified direction and merge if possible."""
        valid_directions = {'up', 'down', 'left', 'right'}
        if direction not in valid_directions:
            raise ValueError(f"Invalid direction. Must be one of {valid_directions}")

        # Store the initial state
        initial_state = [row[:] for row in self.board]
        
        # Transpose for up/down movements
        if direction in {'up', 'down'}:
            self.board = list(map(list, zip(*self.board, strict=False)))
        
        # Reverse for right/down movements
        if direction in {'right', 'down'}:
            self.board = [row[::-1] for row in self.board]

        # Move and merge
        moved = False
        for i in range(self.size):
            new_row = self._merge_row(self.board[i])
            if new_row != self.board[i]:
                moved = True
            self.board[i] = new_row

        # Reverse back for right/down movements
        if direction in {'right', 'down'}:
            self.board = [row[::-1] for row in self.board]
        
        # Transpose back for up/down movements
        if direction in {'up', 'down'}:
            self.board = list(map(list, zip(*self.board, strict=False)))

        # Add new tile if the board changed
        if moved:
            self.add_new_tile()

        return moved

    def _merge_row(self, row: list[int]) -> list[int]:
        """Merge tiles in a row."""
        # Remove zeros and collect non-zero values
        new_row = [x for x in row if x != 0]
        
        # Merge adjacent equal values
        i = 0
        while i < len(new_row) - 1:
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                self.score += new_row[i]
                new_row.pop(i + 1)
            i += 1
        
        # Pad with zeros to maintain row size
        return new_row + [0] * (self.size - len(new_row))

    def get_state(self) -> dict:
        """Return the current game state."""
        return {
            "board": self.board,
            "score": self.score,
            "game_over": self.is_game_over()
        }