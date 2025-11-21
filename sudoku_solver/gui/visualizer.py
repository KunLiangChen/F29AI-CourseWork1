# gui/visualizer.py
"""
Solver worker for background execution of the CSP solver.
Monitors solver progress and emits signals for UI updates.
"""
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import threading
import time
import numpy as np

class SolverWorker(QObject):
    """
    Worker that runs the Sudoku solver in a background thread.
    Polls the board state and step logs to detect progress,
    and emits signals for UI updates.
    
    Emitted signals:
        step: (grid: np.ndarray, highlight: (r,c) or None) - intermediate solving steps
        finished: (success: bool, metrics: dict) - solver completion
        step_info: (text: str) - detailed step information for logging
    """
    # Signal definitions for communicating with main thread
    step = pyqtSignal(object, object)      # (grid: np.ndarray, highlight: (r,c) or None)
    finished = pyqtSignal(bool, dict)      # (success: bool, metrics: dict)
    step_info = pyqtSignal(str)            # step information string

    def __init__(self, board, solver_cls):
        """
        Initialize the solver worker.
        
        Args:
            board (SudokuBoard): The puzzle board to solve
            solver_cls: The solver class (e.g., CSPSolver) to use for solving
        """
        super().__init__()
        self.board = board
        self.solver_cls = solver_cls
        # Event flag for gracefully stopping the worker
        self._stop = threading.Event()
        

    def run(self):
        """
        Main worker thread entry point.
        Strategy:
          1. Create an instance of the solver
          2. Start solver.solve() in a dedicated thread (blocking operation)
          3. While solver thread is running, poll the board state and step logs
          4. Detect grid changes and emit them as signals
          5. When solver completes, emit final result and metrics
        
        The polling approach allows the worker thread to remain responsive
        while the solver does its work in a separate thread.
        """
        # Create solver instance
        solver = self.solver_cls(self.board)
        # Keep a copy of the last seen grid state for change detection
        last_snapshot = np.array(self.board.grid, copy=True)
        last_step_count = 0
        
        # Start the blocking solver in a dedicated daemon thread
        # This prevents it from blocking the Qt worker thread
        solver_thread = threading.Thread(target=solver.solve, daemon=True)
        solver_thread.start()

        # Poll while solver is still running
        while solver_thread.is_alive() and not self._stop.is_set():
            # Get current grid state
            current = np.array(self.board.grid, copy=True)
            
            # Check for new step log entries (if solver tracks steps)
            if hasattr(solver, 'step_log'):
                current_step_count = len(solver.step_log)
                if current_step_count > last_step_count:
                    # Emit any new step information
                    for i in range(last_step_count, current_step_count):
                        step_msg = solver.step_log[i]
                        self.step_info.emit(step_msg)
                    last_step_count = current_step_count
            
            # Check for grid changes
            if not np.array_equal(current, last_snapshot):
                # Find the cell(s) that changed
                diff = (current != last_snapshot)
                coords = list(zip(*diff.nonzero()))
                # Highlight the most recently changed cell
                highlight = coords[-1] if coords else None
                # Emit grid snapshot and highlight signal
                self.step.emit(current.copy(), highlight)
                last_snapshot = current
            
            # Small delay to avoid busy waiting (10ms polling interval)
            time.sleep(0.01)

        # After solver finishes, emit the final snapshot
        final = np.array(self.board.grid, copy=True)
        self.step.emit(final.copy(), None)
        
        # Emit any remaining step log entries
        if hasattr(solver, 'step_log') and last_step_count < len(solver.step_log):
            for i in range(last_step_count, len(solver.step_log)):
                step_msg = solver.step_log[i]
                self.step_info.emit(step_msg)
        
        # Get solver metrics (if available)
        metrics = solver.metrics.summary() if hasattr(solver, "metrics") else {}
        # Check if puzzle is fully solved (no zeros remaining)
        success = final.min() > 0
        # Emit finished signal with success status and metrics
        self.finished.emit(success, metrics)

    def stop(self):
        """
        Request the worker to stop gracefully.
        Sets the stop event that the polling loop checks.
        """
        self._stop.set()