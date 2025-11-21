# tests/test_csp_solver.py

import os
import numpy as np
import pytest
from sudoku_core.board import SudokuBoard
from sudoku_core.csp_solver import CSPSolver



def is_valid_solution(board: SudokuBoard):

    grid = board.grid
    for i in range(9):
        row = grid[i, :]
        col = grid[:, i]
        if len(set(row)) != 9 or len(set(col)) != 9:
            return False


    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            block = grid[r:r+3, c:c+3].flatten()
            if len(set(block)) != 9:
                return False
    return True


def load_board_from_file(path):

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        grid = np.loadtxt(path, delimiter=",", dtype=int)
    else:
        grid = np.loadtxt(path, dtype=int)
    return SudokuBoard(grid)




def test_easy_sudoku(tmp_path):

    board = load_board_from_file("data/easy.txt")
    solver = CSPSolver(board, use_mrv=True, use_lcv=True, use_fc=True)
    solved = solver.solve()

    assert solved, "The solver failed to find a solution"
    assert board.is_complete(), "The board is not filled."
    assert is_valid_solution(board), "The final solution does not satisfy the Sudoku constraints"

    summary = solver.metrics.summary()
    assert summary["assignments"] > 0
    assert summary["time"] < 10, "Simple questions take too long"


def test_medium_or_hard_examples():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    candidate_files = ["medium.csv", "hard.txt"]
    for fname in candidate_files:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            pytest.skip(f"Not found {fname}")

        board = load_board_from_file(path)
        solver = CSPSolver(board, use_mrv=True, use_lcv=True, use_fc=True)
        solved = solver.solve()

        assert solved, f"{fname} can't solve"
        assert is_valid_solution(board), f"{fname} not valid"


def test_different_configurations():
    grid = [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ]
    configs = [
        dict(use_mrv=False, use_lcv=False, use_fc=False),
        dict(use_mrv=True, use_lcv=False, use_fc=False),
        dict(use_mrv=True, use_lcv=True, use_fc=True),
        dict(use_mrv=True, use_lcv=True, use_fc=True, use_ac3=True),
    ]

    for cfg in configs:
        board = SudokuBoard(grid)
        solver = CSPSolver(board, **cfg)
        solved = solver.solve()
        assert solved, f" {cfg} not solved"
        assert is_valid_solution(board)


def test_unsolvable_case():

    grid = [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],  
    ] + [[0]*9 for _ in range(8)]

    board = SudokuBoard(grid)
    solver = CSPSolver(board)
    solved = solver.solve()

    
    assert not solved, "Unsolvable sudoku should not be solved"
  
