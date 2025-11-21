# gui/control_panel.py
"""
Control panel widget for the Sudoku Solver GUI.
Provides buttons for file operations, solving, and displaying solver metrics and step logs.
"""
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QCheckBox, QSlider, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from utils.file_io import load_sudoku, save_sudoku
from utils.logger import get_logger
import numpy as np

logger = get_logger("GUI", None)

class ControlPanel(QWidget):
    """
    Right-side control panel for the Sudoku Solver.
    Contains action buttons (Load, Save, Solve, Reset, Quit),
    status display, metrics display, and a step-by-step solver log.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def sizeHint(self):
        """
        Provide size hint to the layout manager.
        Tells the layout to allocate approximately 220 pixels width and 400 pixels height.
        """
        return QSize(220, 400)

    def _init_ui(self):
        """
        Initialize the control panel layout and widgets.
        Sets up:
        - Action buttons (Load, Save, Solve, Reset, Quit)
        - Status and metrics labels
        - Step-by-step solver log display area
        """
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create main action buttons with increased height for better usability
        self.load_btn = QPushButton("Load (.txt/.csv)")
        self.load_btn.setMinimumHeight(40)
        self.save_btn = QPushButton("Save")
        self.save_btn.setMinimumHeight(40)
        self.solve_btn = QPushButton("Solve")
        self.solve_btn.setMinimumHeight(40)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(40)
        self.quit_btn = QPushButton("Quit")
        self.quit_btn.setMinimumHeight(40)

        # Status display labels
        self.status_label = QLabel("Ready")
        self.metrics_label = QLabel("Metrics: -")
        
        # Step-by-step solver log area (scrollable text edit)
        # Shows detailed information about each solving step
        self.steps_log = QTextEdit()
        self.steps_log.setReadOnly(True)
        self.steps_log.setMinimumHeight(400)
        self.steps_log.setStyleSheet("background: #1a1a1a; color: #aaa; font-size: 20px;")

        # Arrange widgets in vertical layout
        layout.addWidget(self.load_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.quit_btn)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_label)
        layout.addWidget(self.metrics_label)
        layout.addWidget(QLabel("Solve Steps:"))
        # Stretch factor 1 allows steps_log to expand and fill available space
        layout.addWidget(self.steps_log, 1)

        self.setLayout(layout)

    def open_file_dialog(self):
        """
        Open a file selection dialog for loading Sudoku puzzles.
        
        Returns:
            str: Selected file path, or None if user cancels
        
        Accepts .txt and .csv file formats.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open Sudoku", "", "Sudoku files (*.txt *.csv)")
        return path if path else None

    def save_file_dialog(self, suggested_name="solution.txt"):
        """
        Open a file save dialog for exporting Sudoku solutions.
        
        Args:
            suggested_name (str): Default filename to suggest to user
        
        Returns:
            str: Selected save path, or None if user cancels
        
        Accepts .txt and .csv file formats.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Save Sudoku", suggested_name, "Sudoku files (*.txt *.csv)")
        return path if path else None

    def set_status(self, text: str):
        """
        Update the status label and log the message.
        
        Args:
            text (str): Status message to display and log
        """
        self.status_label.setText(text)
        logger.info(text)

    def set_metrics_text(self, text: str):
        """
        Update the metrics display label.
        
        Args:
            text (str): Metrics information to display (e.g., "assignments=123, backtracks=5")
        """
        self.metrics_label.setText(f"Metrics: {text}")
    
    def add_step_log(self, text: str):
        """
        Add a step log message to the scrollable steps log area.
        Automatically scrolls to the bottom to show the latest entry.
        
        Args:
            text (str): Step information text to append to the log
        """
        self.steps_log.append(text)
        # Auto-scroll to bottom to show the latest step
        scrollbar = self.steps_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_steps_log(self):
        """Clear all content from the steps log display."""
        self.steps_log.clear()
