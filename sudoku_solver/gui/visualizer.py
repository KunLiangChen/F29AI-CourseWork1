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
    """
    step = pyqtSignal(object, object)      # (grid: np.ndarray, highlight: (r,c) or None)
    finished = pyqtSignal(bool, dict)

    def __init__(self, board, solver_cls, poll_interval=0.05):
        super().__init__()
        self.board = board
        self.solver_cls = solver_cls
        self._stop = threading.Event()
        self.poll_interval = poll_interval

    def run(self):
        """
        This method will be executed in a QThread.
        Strategy:
          - create solver
          - start solver.solve() in a separate thread (because it's blocking)
          - while solver thread alive: poll board.grid, detect changes, emit steps
          - when solver done: emit final
        """
        solver = self.solver_cls(self.board)
        last_snapshot = np.array(self.board.grid, copy=True)
        # start solver in a dedicated thread
        solver_thread = threading.Thread(target=solver.solve, daemon=True)
        solver_thread.start()

        # poll while solver running
        while solver_thread.is_alive() and not self._stop.is_set():
            current = np.array(self.board.grid, copy=True)
            if not np.array_equal(current, last_snapshot):
                # find one changed cell (prefer newly assigned)
                diff = (current != last_snapshot)
                coords = list(zip(*diff.nonzero()))
                highlight = coords[-1] if coords else None
                self.step.emit(current.copy(), highlight)
                last_snapshot = current
            time.sleep(self.poll_interval)

        # after finishing, ensure final snapshot emitted
        final = np.array(self.board.grid, copy=True)
        # compute final highlight as None
        self.step.emit(final.copy(), None)
        # get metrics if available
        metrics = solver.metrics.summary() if hasattr(solver, "metrics") else {}
        success = final.min() > 0
        self.finished.emit(success, metrics)

    def stop(self):
        self._stop.set()