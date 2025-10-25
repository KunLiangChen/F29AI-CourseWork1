# tests/test_file_io.py
import os
import numpy as np
import pytest
from sudoku_core.board import SudokuBoard
from utils.file_io import load_sudoku, save_sudoku


def test_load_txt_file(tmp_path):
    file_path = tmp_path / "sudoku.txt"
    file_path.write_text(
        "5 3 0 0 7 0 0 0 0\n"
        "6 0 0 1 9 5 0 0 0\n"
        "0 9 8 0 0 0 0 6 0\n"
        "8 0 0 0 6 0 0 0 3\n"
        "4 0 0 8 0 3 0 0 1\n"
        "7 0 0 0 2 0 0 0 6\n"
        "0 6 0 0 0 0 2 8 0\n"
        "0 0 0 4 1 9 0 0 5\n"
        "0 0 0 0 8 0 0 7 9\n"
    )

    board = load_sudoku(str(file_path))
    assert isinstance(board, SudokuBoard)
    assert board.grid.shape == (9, 9)
    assert board.grid[0, 0] == 5
    assert board.grid[8, 8] == 9


def test_load_csv_file(tmp_path):
    file_path = tmp_path / "sudoku.csv"
    file_path.write_text(
        "5,3,0,0,7,0,0,0,0\n"
        "6,0,0,1,9,5,0,0,0\n"
        "0,9,8,0,0,0,0,6,0\n"
        "8,0,0,0,6,0,0,0,3\n"
        "4,0,0,8,0,3,0,0,1\n"
        "7,0,0,0,2,0,0,0,6\n"
        "0,6,0,0,0,0,2,8,0\n"
        "0,0,0,4,1,9,0,0,5\n"
        "0,0,0,0,8,0,0,7,9\n"
    )

    board = load_sudoku(str(file_path))
    assert isinstance(board, SudokuBoard)
    assert board.grid[1, 3] == 1
    assert board.grid[4, 4] == 0
    assert board.grid[8, 8] == 9


def test_save_and_reload_txt(tmp_path):
    grid = np.arange(81).reshape(9, 9)
    board = SudokuBoard(grid)
    file_path = tmp_path / "save_test.txt"

    save_sudoku(board, str(file_path))
    assert file_path.exists()

    reloaded = load_sudoku(str(file_path))
    np.testing.assert_array_equal(reloaded.grid, board.grid)


def test_save_and_reload_csv(tmp_path):
    grid = np.eye(9, dtype=int)
    board = SudokuBoard(grid)
    file_path = tmp_path / "save_test.csv"

    save_sudoku(board, str(file_path))
    assert file_path.exists()

    reloaded = load_sudoku(str(file_path))
    np.testing.assert_array_equal(reloaded.grid, board.grid)


def test_invalid_file_extension(tmp_path):
    bad_file = tmp_path / "invalid.json"
    bad_file.write_text("{}")

    with pytest.raises(ValueError):
        load_sudoku(str(bad_file))


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_sudoku("no_such_file.txt")


def test_invalid_row_length_txt(tmp_path):
    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("1 2 3 4 5\n6 7 8 9 0")
    with pytest.raises(ValueError):
        load_sudoku(str(bad_file))


def test_invalid_row_length_csv(tmp_path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text("1,2,3,4,5,6,7,8\n1,2,3,4,5,6,7,8")
    with pytest.raises(ValueError):
        load_sudoku(str(bad_file))
