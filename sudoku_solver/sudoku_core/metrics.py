# sudoku_core/metrics.py
"""
Metrics Module
--------------
Tracks performance statistics during the CSP Sudoku solving process:
- Total solving time
- Number of recursive calls
- Number of backtracks
- Whether the solution was successful
"""

import time

class Metrics:
    def __init__(self):
        self.assignments = 0
        self.backtracks = 0
        self.start_time = None
        self.end_time = None
    def start(self):
        self.start_time = time.time()
    def stop(self):
        self.end_time = time.time()
    def record_assignment(self):
        self.assignments += 1
    def record_backtrack(self):
        self.backtracks += 1
    def summary(self):
        return {
            "assignments": self.assignments,
            "backtracks": self.backtracks,
            "time": (self.end_time - self.start_time) if self.start_time and self.end_time else None
        }
