# gui/control_panel.py
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QCheckBox, QSlider, QGroupBox)
from PyQt5.QtCore import Qt
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
        # buttons
        self.load_btn = QPushButton("Load (.txt/.csv)")
        self.save_btn = QPushButton("Save")
        self.solve_btn = QPushButton("Solve")
        self.reset_btn = QPushButton("Reset")
        self.quit_btn = QPushButton("Quit")
        # animation checkbox
        self.animate_checkbox = QCheckBox("Animate solving (step-by-step)")
        self.animate_checkbox.setChecked(True)
        # speed slider
        speed_box = QGroupBox("Animation speed")
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)   # ms
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(150)
        speed_layout.addWidget(QLabel("Fast"))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("Slow"))
        speed_box.setLayout(speed_layout)

        # status label
        self.status_label = QLabel("Ready")
        self.metrics_label = QLabel("Metrics: -")

        # pack
        layout.addWidget(self.load_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.solve_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.quit_btn)
        layout.addWidget(self.animate_checkbox)
        layout.addWidget(speed_box)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.metrics_label)

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
