# tests/test_csp_solver.py

import os
import numpy as np
import pytest
from sudoku_core.board import SudokuBoard
from sudoku_core.csp_solver import CSPSolver

# ------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------

def is_valid_solution(board: SudokuBoard):
    """验证最终数独解是否合法"""
    grid = board.grid
    for i in range(9):
        row = grid[i, :]
        col = grid[:, i]
        if len(set(row)) != 9 or len(set(col)) != 9:
            return False

    # 检查每个 3x3 宫
    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            block = grid[r:r+3, c:c+3].flatten()
            if len(set(block)) != 9:
                return False
    return True


def load_board_from_file(path):
    """支持 txt 或 csv 文件"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        grid = np.loadtxt(path, delimiter=",", dtype=int)
    else:
        grid = np.loadtxt(path, dtype=int)
    return SudokuBoard(grid)


# ------------------------------------------------------------
# 测试用例
# ------------------------------------------------------------

def test_easy_sudoku():
    """测试一个简单数独能被快速解出"""
    # 构造一个简单可解的棋盘
    board = load_board_from_file("data/hard.txt")
    solver = CSPSolver(board, use_mrv=True, use_lcv=True, use_fc=True)
    solved = solver.solve()

    assert solved, "求解器未能找到解"
    assert board.is_complete(), "棋盘未填满"
    assert is_valid_solution(board), "最终解不满足数独约束"

    summary = solver.metrics.summary()
    assert summary["assignments"] > 0
    assert summary["time"] < 10, "简单题耗时过长"


def test_medium_or_hard_examples():
    """测试能正确加载文件并求解中等或困难题"""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    candidate_files = ["medium.csv", "hard.txt"]
    for fname in candidate_files:
        path = os.path.join(data_dir, fname)
        if not os.path.exists(path):
            pytest.skip(f"未找到样例文件 {fname}")

        board = load_board_from_file(path)
        solver = CSPSolver(board, use_mrv=True, use_lcv=True, use_fc=True)
        solved = solver.solve()

        assert solved, f"{fname} 未能解出"
        assert is_valid_solution(board), f"{fname} 结果不合法"


def test_different_configurations():
    """验证不同启发式配置下求解一致性"""
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
        assert solved, f"配置 {cfg} 未能解出"
        assert is_valid_solution(board)


def test_unsolvable_case():
    """故意构造无解的数独（两个相同数字在同一行）"""
    grid = [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],  # 重复的 '5'
    ] + [[0]*9 for _ in range(8)]

    board = SudokuBoard(grid)
    solver = CSPSolver(board)
    solved = solver.solve()

    # 理论上无法求解
    assert not solved, "无解数独不应被解出"

test_easy_sudoku()
