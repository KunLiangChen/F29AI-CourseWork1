# gui/visualizer.py
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import threading
import time
import numpy as np

class SolverWorker(QObject):
    """
    Worker that runs solver in a background thread and polls board snapshots.
    Emits:
      step(grid_snapshot, (r,c) or None)  -> intermediate steps
      finished(success: bool, metrics: dict) -> when solver is done
      step_info(str) -> step information for logging
    """
    step = pyqtSignal(object, object)      # (grid: np.ndarray, highlight: (r,c) or None)
    finished = pyqtSignal(bool, dict)
    step_info = pyqtSignal(str)            # step information string

    def __init__(self, board, solver_cls):
        super().__init__()
        self.board = board
        self.solver_cls = solver_cls
        self._stop = threading.Event()
        

    def run(self):
        """
        This method will be executed in a QThread.
        Strategy:
          - create solver
          - start solver.solve() in a separate thread (because it's blocking)
          - while solver thread alive: poll board.grid and step_log, detect changes
          - when solver done: emit final
        """
        solver = self.solver_cls(self.board)
        last_snapshot = np.array(self.board.grid, copy=True)
        last_step_count = 0
        
        # start solver in a dedicated thread
        solver_thread = threading.Thread(target=solver.solve, daemon=True)
        solver_thread.start()

        # poll while solver running
        while solver_thread.is_alive() and not self._stop.is_set():
            current = np.array(self.board.grid, copy=True)
            
            # Check for new steps in the log
            if hasattr(solver, 'step_log'):
                current_step_count = len(solver.step_log)
                if current_step_count > last_step_count:
                    
                    for i in range(last_step_count, current_step_count):
                        step_msg = solver.step_log[i]
                        self.step_info.emit(step_msg)
                    last_step_count = current_step_count
            
            if not np.array_equal(current, last_snapshot):
                # find one changed cell (prefer newly assigned)
                diff = (current != last_snapshot)
                coords = list(zip(*diff.nonzero()))
                highlight = coords[-1] if coords else None
                self.step.emit(current.copy(), highlight)
                last_snapshot = current
            
            time.sleep(0.01)  # Small delay to avoid busy waiting

        # after finishing, ensure final snapshot emitted
        final = np.array(self.board.grid, copy=True)
        # compute final highlight as None
        self.step.emit(final.copy(), None)
        
        # emit any remaining steps
        if hasattr(solver, 'step_log') and last_step_count < len(solver.step_log):
            for i in range(last_step_count, len(solver.step_log)):
                step_msg = solver.step_log[i]
                self.step_info.emit(step_msg)
        
        # get metrics if available
        metrics = solver.metrics.summary() if hasattr(solver, "metrics") else {}
        success = final.min() > 0
        self.finished.emit(success, metrics)

    def stop(self):
        self._stop.set()