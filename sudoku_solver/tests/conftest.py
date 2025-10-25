import sys
import os

# 计算项目根目录 (sudoku_solver) 的绝对路径
# os.path.abspath(__file__) -> /path/to/sudoku_solver/tests/conftest.py
# os.path.dirname(...)      -> /path/to/sudoku_solver/tests
# os.path.dirname(...)      -> /path/to/sudoku_solver  <-- 这就是你需要的根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将根目录插入到 sys.path 的最前面
if project_root not in sys.path:
    sys.path.insert(0, project_root)