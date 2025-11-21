# gui/main_window.py
"""
Main window for the Sudoku Solver GUI application.
Orchestrates the board display, control panel, and solver thread management.
Provides file I/O and user interaction handling.
"""
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
    """
    Main application window for the Sudoku Solver.
    Manages:
    - Board display and input
    - Control panel and user actions
    - Solver thread and progress visualization
    - File I/O operations
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Solver — Dark Mode (Animated)")
        self.resize(1100, 800)
        # Thread and worker for background solving
        self.worker_thread = None
        self.worker = None
        # State tracking for solving visualization
        self._last_snapshot = np.zeros((9,9), dtype=int)
        self._highlight_timer = None

        self._init_ui()

    def _init_ui(self):
        """
        Initialize the main window UI layout.
        Creates:
        - Left column: Board widget and log area
        - Right column: Control panel
        - Connects control signals to action handlers
        """
        central = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

        # Create the 9x9 Sudoku board widget
        self.board_widget = BoardWidget(self)

        # Create the control panel (buttons, status, metrics, logs)
        self.control = ControlPanel(self)

        # Create log area for general application messages
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(180)
        self.log_text.setStyleSheet("background: #111; color: #ccc;")

        # Connect control panel button signals to handler methods
        self.control.load_btn.clicked.connect(self.on_load)
        self.control.save_btn.clicked.connect(self.on_save)
        self.control.solve_btn.clicked.connect(self.on_solve)
        self.control.reset_btn.clicked.connect(self.on_reset)
        self.control.quit_btn.clicked.connect(self.close)

        # Arrange left column: board on top, log area below
        left_col.addWidget(self.board_widget)
        left_col.addWidget(self.log_text)

        # Arrange right column: control panel with stretch at bottom
        right_col.addWidget(self.control)
        right_col.addStretch()

        # Add both columns to main layout
        main_layout.addLayout(left_col, 0)
        main_layout.addLayout(right_col, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def log(self, text: str):
        """
        Log a message to both the UI log area and application logger.
        
        Args:
            text (str): Message to log
        """
        self.log_text.append(text)
        logger.info(text)

    def on_load(self):
        """
        Handle the Load button click.
        Opens a file dialog, loads a Sudoku puzzle, and displays it on the board.
        Shows error dialog if loading fails.
        """
        path = self.control.open_file_dialog()
        if not path:
            return
        try:
            # Load puzzle from file
            board = load_sudoku(path)
            # Display loaded puzzle on the board
            self.board_widget.set_grid(board.grid)
            self.log(f"Loaded: {path}")
            self.control.set_status("Loaded file.")
        except Exception as e:
            QMessageBox.warning(self, "Load error", str(e))
            self.log(f"Load failed: {e}")

    def on_save(self):
        """
        Handle the Save button click.
        Opens a file save dialog and exports the current board state to file.
        Shows error dialog if saving fails.
        """
        path = self.control.save_file_dialog("solution.txt")
        if not path:
            return
        try:
            # Get current board state
            grid = self.board_widget.get_grid()
            # Save to file
            save_sudoku(SudokuBoard(grid), path)
            self.log(f"Saved to: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Save error", str(e))
            self.log(f"Save failed: {e}")

    def on_reset(self):
        """
        Handle the Reset button click.
        Clears all cells from the board and resets status.
        """
        self.board_widget.clear()
        self.log("Board reset.")
        self.control.set_status("Ready")

    def on_solve(self):
        """
        Handle the Solve button click.
        Initiates the solving process in a background thread.
        - Validates the input grid
        - Clears the previous step log
        - Disables UI controls during solving
        - Starts a worker thread to run the CSP solver
        - Updates the board with progress as the solver runs
        """
        # Extract grid from board UI
        grid = self.board_widget.get_grid()
        # Create SudokuBoard from grid with validation
        try:
            board = SudokuBoard(grid)
        except Exception as e:
            QMessageBox.warning(self, "Invalid board", str(e))
            return

        # Clear previous steps log
        self.control.clear_steps_log()
        self.control.add_step_log("Solving started...")

        # Disable UI controls while solver is running
        self.control.solve_btn.setEnabled(False)
        self.control.load_btn.setEnabled(False)
        self.control.reset_btn.setEnabled(False)
        self.control.save_btn.setEnabled(False)
        self.control.set_status("Solving...")

        # Create solver worker and thread
        # The worker runs the solver in a separate thread to keep UI responsive
        self.worker = SolverWorker(board, CSPSolver)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect worker signals to handler methods
        self.worker_thread.started.connect(self.worker.run)
        self.worker.step_info.connect(self.on_step_info)
        self.worker.finished.connect(self.on_finished)
        
        # Start the solver thread
        self.worker_thread.start()
        self.log("Solver started (background).")

    def on_step(self, grid_snapshot, highlight):
        """
        Handle intermediate solving step (currently not connected).
        This method can be used to animate the solving process by showing
        the board state as it changes during solving.
        
        Args:
            grid_snapshot (numpy.ndarray): 9x9 grid state at this step
            highlight (tuple or None): (row, col) to highlight, or None
        """
        # Update board widget with current solver state
        self.board_widget.show_grid_snapshot(grid_snapshot, highlight)
        # Schedule clearing highlight after a short interval
        if highlight:
            # Use QTimer to restore style after a delay
            delay = self.control.speed_slider.value() if hasattr(self.control, 'speed_slider') else 100
            QTimer.singleShot(delay, lambda: self.board_widget.set_grid(grid_snapshot))
    
    def on_step_info(self, info_text: str):
        """
        Handle step information from the solver worker.
        Adds detailed step logs to the control panel.
        
        Args:
            info_text (str): Descriptive text about the current solving step
        """
        self.control.add_step_log(info_text)

    def on_finished(self, success: bool, metrics: dict):
        """
        Handle solver completion.
        Displays final result, metrics, and re-enables UI controls.
        
        Args:
            success (bool): True if puzzle was completely solved
            metrics (dict): Solver metrics (assignments, backtracks, time, etc.)
        """
        # Display final solved grid on board
        final_grid = self.worker.board.grid if self.worker else None
        if final_grid is not None:
            self.board_widget.set_grid(final_grid)
        
        # Update status and metrics display
        self.control.set_status("Finished" if success else "Finished (incomplete)")
        metrics_text = f"assignments={metrics.get('assignments')}, backtracks={metrics.get('backtracks')}, time={metrics.get('time'):.3f}s" if metrics.get('time') is not None else str(metrics)
        self.control.set_metrics_text(metrics_text)
        self.log(f"Solve finished. Success={success}. {metrics_text}")
        
        # Re-enable UI controls for next operation
        self.control.solve_btn.setEnabled(True)
        self.control.load_btn.setEnabled(True)
        self.control.reset_btn.setEnabled(True)
        self.control.save_btn.setEnabled(True)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
            self.worker = None
