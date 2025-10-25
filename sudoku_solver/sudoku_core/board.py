# sudoku_core/board.py

import numpy as np

class SudokuBoard:
    def __init__(self, grid=None):
        """
        grid: 9x9 list or numpy array, 0 represents empty cell
        """
        if grid is None:
            self.grid = np.zeros((9, 9), dtype=int)
        else:
            self.grid = np.array(grid, dtype=int)
        assert self.grid.shape == (9, 9), "Grid must be 9x9"

    def is_valid(self, row, col, num):
        "Check if num is valid in the row, col, and 3x3 box"
        if num in self.grid[row, :]: return False
        if num in self.grid[:, col]: return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        if num in self.grid[start_row:start_row+3, start_col:start_col+3]:
            return False
        return True

    def find_empty(self):
        "Return the row, col of the first empty cell, or None if none found"
        for r in range(9):
            for c in range(9):
                if self.grid[r, c] == 0:
                    return r, c
        return None

    def is_complete(self):
        "Check if the board is complete"
        return np.all(self.grid > 0)

    def set_value(self, row, col, num):
        self.grid[row, col] = num

    def clear_value(self, row, col):
        self.grid[row, col] = 0

    def __str__(self):
        "Return a string representation of the board"
        out = ""
        for i in range(9):
            row = " ".join(str(x) if x != 0 else "." for x in self.grid[i])
            out += row + "\n"
        return out
