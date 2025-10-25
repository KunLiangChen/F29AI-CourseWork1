# utils/file_io.py
import os
import csv
import numpy as np
from sudoku_core.board import SudokuBoard

def load_sudoku(file_path: str) -> SudokuBoard:
    """
    Load a Sudoku puzzle from .txt or .csv file.
    Returns a SudokuBoard instance.

    Supports:
        - .txt : space- or comma-separated numbers, '.' or '0' for empty cells
        - .csv : comma-separated values
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        grid = _load_txt(file_path)
    elif ext == ".csv":
        grid = _load_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")

    return SudokuBoard(grid)

def _load_txt(file_path):
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:  # skip blank lines
                continue
            parts = [x for x in line.replace(",", " ").split() if x]
            row = []
            for x in parts:
                if x in {".", "0"}:
                    row.append(0)
                else:
                    row.append(int(x))
            if len(row) != 9:
                raise ValueError(f"Invalid row length in {file_path}: {line}")
            rows.append(row)
    if len(rows) != 9:
        raise ValueError(f"Expected 9 rows in {file_path}, got {len(rows)}")
    return np.array(rows, dtype=int)

def _load_csv(file_path):
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            values = []
            for x in row:
                x = x.strip()
                if x in {".", "0", ""}:
                    values.append(0)
                else:
                    values.append(int(x))
            if len(values) != 9:
                raise ValueError(f"Invalid CSV row length: {row}")
            rows.append(values)
    if len(rows) != 9:
        raise ValueError(f"Expected 9 rows, got {len(rows)}")
    return np.array(rows, dtype=int)

def save_sudoku(board: SudokuBoard, file_path: str):
    """
    Save SudokuBoard to a .txt or .csv file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    grid = board.grid
    if ext == ".txt":
        with open(file_path, "w", encoding="utf-8") as f:
            for row in grid:
                f.write(" ".join(str(x) for x in row) + "\n")
    elif ext == ".csv":
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(grid)
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")
