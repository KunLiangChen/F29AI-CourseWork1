# gui/control_panel.py
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QCheckBox, QSlider, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from utils.file_io import load_sudoku, save_sudoku
from utils.logger import get_logger
import numpy as np

logger = get_logger("GUI", None)

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def sizeHint(self):
        """Tell the layout manager this widget prefers a certain size."""
        return QSize(220, 400)

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # buttons
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

        # status label
        self.status_label = QLabel("Ready")
        self.metrics_label = QLabel("Metrics: -")
        
        # steps log area (scrollable)
        self.steps_log = QTextEdit()
        self.steps_log.setReadOnly(True)
        self.steps_log.setMinimumHeight(400)
        self.steps_log.setStyleSheet("background: #1a1a1a; color: #aaa; font-size: 20px;")

        # pack
        layout.addWidget(self.load_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.quit_btn)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_label)
        layout.addWidget(self.metrics_label)
        layout.addWidget(QLabel("Solve Steps:"))
        layout.addWidget(self.steps_log, 1)  # 伸缩因子为1，自动扩展

        self.setLayout(layout)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Sudoku", "", "Sudoku files (*.txt *.csv)")
        return path if path else None

    def save_file_dialog(self, suggested_name="solution.txt"):
        path, _ = QFileDialog.getSaveFileName(self, "Save Sudoku", suggested_name, "Sudoku files (*.txt *.csv)")
        return path if path else None

    def set_status(self, text: str):
        self.status_label.setText(text)
        logger.info(text)

    def set_metrics_text(self, text: str):
        self.metrics_label.setText(f"Metrics: {text}")
    
    def add_step_log(self, text: str):
        """Add a step log message to the scrollable area."""
        self.steps_log.append(text)
        # Auto-scroll to bottom
        scrollbar = self.steps_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_steps_log(self):
        """Clear the steps log."""
        self.steps_log.clear()
