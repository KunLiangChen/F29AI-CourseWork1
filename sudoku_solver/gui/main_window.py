# gui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QMessageBox
from PyQt5.QtCore import QThread, QTimer
from .board_widget import BoardWidget
from .control_panel import ControlPanel
from .visualizer import SolverWorker
from sudoku_core.csp_solver import CSPSolver
from sudoku_core.board import SudokuBoard
from utils.file_io import load_sudoku, save_sudoku
from utils.logger import get_logger
import numpy as np

logger = get_logger("MainWindow", None)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Solver — Dark Mode (Animated)")
        self.resize(1000, 800)
        self.worker_thread = None
        self.worker = None
        self._last_snapshot = np.zeros((9,9), dtype=int)
        self._highlight_timer = None

        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

        # board
        self.board_widget = BoardWidget(self)
    
        # control
        self.control = ControlPanel(self)

        # log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(180)
        # self.log_text.setStyleSheet("background: #111; color: #ccc;")

        # connect control signals
        self.control.load_btn.clicked.connect(self.on_load)
        self.control.save_btn.clicked.connect(self.on_save)
        self.control.solve_btn.clicked.connect(self.on_solve)
        self.control.reset_btn.clicked.connect(self.on_reset)
        self.control.quit_btn.clicked.connect(self.close)

        left_col.addWidget(self.board_widget)
        left_col.addWidget(self.log_text)

        right_col.addWidget(self.control)
        right_col.addStretch()

        main_layout.addLayout(left_col, 0)
        main_layout.addLayout(right_col, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def log(self, text: str):
        self.log_text.append(text)
        logger.info(text)

    def on_load(self):
        path = self.control.open_file_dialog()
        if not path:
            return
        try:
            board = load_sudoku(path)
            self.board_widget.set_grid(board.grid)
            self.log(f"Loaded: {path}")
            self.control.set_status("Loaded file.")
        except Exception as e:
            QMessageBox.warning(self, "Load error", str(e))
            self.log(f"Load failed: {e}")

    def on_save(self):
        path = self.control.save_file_dialog("solution.txt")
        if not path:
            return
        try:
            grid = self.board_widget.get_grid()
            save_sudoku(SudokuBoard(grid), path)
            self.log(f"Saved to: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Save error", str(e))
            self.log(f"Save failed: {e}")

    def on_reset(self):
        self.board_widget.clear()
        self.log("Board reset.")
        self.control.set_status("Ready")

    def on_solve(self):
        # read grid
        grid = self.board_widget.get_grid()
        # create SudokuBoard
        try:
            board = SudokuBoard(grid)
        except Exception as e:
            QMessageBox.warning(self, "Invalid board", str(e))
            return

        # clear previous steps log
        self.control.clear_steps_log()
        # self.control.add_step_log("=" * 50)
        self.control.add_step_log("Solving started...")
        # self.control.add_step_log("=" * 50)

        # disable UI controls while running
        self.control.solve_btn.setEnabled(False)
        self.control.load_btn.setEnabled(False)
        self.control.reset_btn.setEnabled(False)
        self.control.save_btn.setEnabled(False)
        self.control.set_status("Solving...")

        # prepare worker thread
        self.worker = SolverWorker(board, CSPSolver)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        # connect signals (skip on_step for direct result)
        self.worker_thread.started.connect(self.worker.run)
        # self.worker.step.connect(self.on_step)  
        self.worker.step_info.connect(self.on_step_info)  #
        self.worker.finished.connect(self.on_finished)
        # start thread
        self.worker_thread.start()
        self.log("Solver started (background).")

    def on_step(self, grid_snapshot, highlight):
        """
        Called frequently while solver runs.
        grid_snapshot: numpy array 9x9
        highlight: (r,c) or None for final
        """
        # update board widget with snapshot
        self.board_widget.show_grid_snapshot(grid_snapshot, highlight)
        # schedule clearing highlight after a short interval (depending on speed)
        if highlight:
            # use QTimer singleShot to restore style after delay
            delay = self.control.speed_slider.value()
            QTimer.singleShot(delay, lambda: self.board_widget.set_grid(grid_snapshot))
    
    def on_step_info(self, info_text: str):
        """Handle step information from solver worker."""
        self.control.add_step_log(info_text)

    def on_finished(self, success: bool, metrics: dict):
        # display final result
        final_grid = self.worker.board.grid if self.worker else None
        if final_grid is not None:
            self.board_widget.set_grid(final_grid)
        
        self.control.set_status("Finished" if success else "Finished (incomplete)")
        metrics_text = f"assignments={metrics.get('assignments')}, backtracks={metrics.get('backtracks')}, time={metrics.get('time'):.3f}s" if metrics.get('time') is not None else str(metrics)
        self.control.set_metrics_text(metrics_text)
        self.log(f"Solve finished. Success={success}. {metrics_text}")
        
        # Log final statistics
        # self.control.add_step_log("=" * 50)
        self.control.add_step_log("---Solving completed---")
        self.control.add_step_log(f"Success: {success}")
        self.control.add_step_log(f"Assignments: {metrics.get('assignments', 0)}")
        self.control.add_step_log(f"Backtracks: {metrics.get('backtracks', 0)}")
        self.control.add_step_log(f"Time: {metrics.get('time', 0):.4f}s")
        # self.control.add_step_log("=" * 50)
        
        # re-enable UI
        self.control.solve_btn.setEnabled(True)
        self.control.load_btn.setEnabled(True)
        self.control.reset_btn.setEnabled(True)
        self.control.save_btn.setEnabled(True)
        # cleanup worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
            self.worker = None
