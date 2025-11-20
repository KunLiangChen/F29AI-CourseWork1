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
        button_group = QGroupBox("Operations")
        button_layout = QVBoxLayout(button_group)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.solve_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.quit_btn)
        # status label
        self.status_label = QLabel("Ready")
        self.metrics_label = QLabel("Metrics: -")
        status_group = QGroupBox("Status & Metrics")
        status_layout = QVBoxLayout(status_group)
        self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #60A5FA;") # 突出显示状态
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.metrics_label)
        # steps log area (scrollable)
        # self.steps_log = QTextEdit()
        # self.steps_log.setReadOnly(True)
        # self.steps_log.setMinimumHeight(800)
        # self.steps_log.setStyleSheet("background: #1a1a1a; color: #aaa; font-size: 20px;")
        log_group = QGroupBox("Solve Steps Log")
        log_layout = QVBoxLayout(log_group)

        self.steps_log = QTextEdit()
        self.steps_log.setReadOnly(True)
        self.steps_log.setMinimumHeight(300)
        self.steps_log.setStyleSheet("background: #1a1a1a; color: #aaa; font-size: 16px; border: none;")

        # 使用styles.qss中的QTextEdit样式，这里不需要额外设置

        log_layout.addWidget(self.steps_log)
        layout.addWidget(log_group, 1) # 伸缩因子为1
        # pack
        layout.addWidget(button_group)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(status_group)

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
