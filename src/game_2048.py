#!/usr/bin/env python3

import random
import sys
from typing import List, Optional, Tuple
import readchar

class Game2048:
    def __init__(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self) -> None:
        """Add a new tile (2 or 4) to a random empty cell."""
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = random.choices([2, 4], weights=[0.9, 0.1])[0]

    def merge(self, line: List[int]) -> Tuple[List[int], int]:
        """Merge a line of numbers, returning the new line and score gained."""
        # Remove zeros and create a new list
        nums = [n for n in line if n != 0]
        score = 0
        i = 0
        
        # Merge adjacent equal numbers
        while i < len(nums) - 1:
            if nums[i] == nums[i + 1]:
                nums[i] *= 2
                score += nums[i]
                nums.pop(i + 1)
            i += 1

        # Pad with zeros to maintain size
        nums.extend([0] * (4 - len(nums)))
        return nums, score

    def move(self, direction: str) -> bool:
        """Move tiles in the specified direction. Return True if the board changed."""
        original_board = [row[:] for row in self.board]
        
        if direction in ['left', 'right']:
            for i in range(4):
                line = self.board[i][:]
                if direction == 'right':
                    line.reverse()
                line, score = self.merge(line)
                if direction == 'right':
                    line.reverse()
                self.board[i] = line
                self.score += score
                
        elif direction in ['up', 'down']:
            for j in range(4):
                line = [self.board[i][j] for i in range(4)]
                if direction == 'down':
                    line.reverse()
                line, score = self.merge(line)
                if direction == 'down':
                    line.reverse()
                for i in range(4):
                    self.board[i][j] = line[i]
                self.score += score

        return self.board != original_board

    def is_game_over(self) -> bool:
        """Check if no moves are possible."""
        # Check for empty cells
        if any(0 in row for row in self.board):
            return False

        # Check for possible merges
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # Check right neighbor
                if j < 3 and current == self.board[i][j + 1]:
                    return False
                # Check bottom neighbor
                if i < 3 and current == self.board[i + 1][j]:
                    return False
        return True

    def print_board(self) -> None:
        """Print the current game board."""
        print(f"\nScore: {self.score}\n")
        print("┌───────┬───────┬───────┬───────┐")
        for i, row in enumerate(self.board):
            print("│", end=" ")
            for num in row:
                if num == 0:
                    print("      │", end=" ")
                else:
                    print(f"{num:^5} │", end=" ")
            print()
            if i < 3:
                print("├───────┼───────┼───────┼───────┤")
        print("└───────┴───────┴───────┴───────┘")

def main():
    """Main game loop."""
    game = Game2048()
    
    # Key mappings
    key_actions = {
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right'
    }
    
    print("\n2048 Game")
    print("Use W/A/S/D to move tiles")
    print("Press Q to quit\n")
    
    while True:
        game.print_board()
        
        # Get user input
        key = readchar.readchar().lower()
        
        if key == 'q':
            print("\nGame Over! Final score:", game.score)
            break
            
        if key in key_actions:
            direction = key_actions[key]
            if game.move(direction):
                game.add_new_tile()
                
            if game.is_game_over():
                game.print_board()
                print("\nGame Over! No more moves possible.")
                print("Final score:", game.score)
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
        sys.exit(0)