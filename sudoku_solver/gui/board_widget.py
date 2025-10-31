# gui/board_widget.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QItemDelegate, QLineEdit
from PyQt5.QtGui import QFont, QColor, QBrush, QPainter, QPen, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
import numpy as np

class DigitDelegate(QItemDelegate):
    """Delegate that restricts input to a single digit 1-9."""
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setMaxLength(1)
        validator = QRegExpValidator(QRegExp("^[1-9]$"), parent)
        editor.setValidator(validator)
        return editor

class BoardWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(9, 9, parent)
        self._init_ui()
        self._prev_grid = np.zeros((9,9), dtype=int)

    def _init_ui(self):
        self.setFixedSize(540, 540)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFont(QFont("Consolas", 18))
        self.setFocusPolicy(Qt.StrongFocus)
        # apply digit-only delegate for all cells
        self.setItemDelegate(DigitDelegate(self))
        for r in range(9):
            self.setRowHeight(r, 60)
            for c in range(9):
                self.setColumnWidth(c, 60)
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self.setItem(r, c, item)
        self._apply_grid_lines()

    def _apply_grid_lines(self):
        # keep thin cell borders via stylesheet; thicker 3x3 separators drawn in paintEvent
        self.setStyleSheet("""
        QTableWidget::item { border: 1px solid #333; color: #ddd; background: #222; }
        QTableWidget { gridline-color: #444; }
        """)

    def get_grid(self) -> np.ndarray:
        grid = np.zeros((9,9), dtype=int)
        for r in range(9):
            for c in range(9):
                txt = self.item(r, c).text().strip() if self.item(r, c) else ""
                if txt == "" or txt == ".":
                    grid[r, c] = 0
                else:
                    # accept only first digit in 1-9
                    val = 0
                    for ch in txt:
                        if ch in "123456789":
                            val = int(ch)
                            break
                    # only accept 1-9; anything else -> 0
                    if not (1 <= val <= 9):
                        val = 0
                    grid[r, c] = val
        return grid

    def set_grid(self, grid: np.ndarray):
        grid = np.array(grid, dtype=int)
        for r in range(9):
            for c in range(9):
                v = grid[r, c]
                text = "" if v == 0 else str(int(v))
                self.item(r, c).setText(text)

    def clear(self):
        for r in range(9):
            for c in range(9):
                self.item(r, c).setText("")

    def highlight_cell(self, r: int, c: int, temporary=True):
        """Highlight a single cell (used for animation)."""
        if not (0 <= r < 9 and 0 <= c < 9):
            return
        item = self.item(r, c)
        if item is None:
            return
        # apply bright background for a short time (caller handles timer)
        item.setBackground(QBrush(QColor(60, 120, 200)))
        item.setForeground(QBrush(QColor(255, 255, 255)))

    def mark_final(self, r: int, c: int):
        """Make final assigned cell style (a bit different)."""
        item = self.item(r, c)
        if item:
            item.setBackground(QBrush(QColor(20, 80, 20)))
            item.setForeground(QBrush(QColor(220, 255, 220)))

    def show_grid_snapshot(self, grid: np.ndarray, highlight=None):
        """
        Set grid to snapshot and optionally highlight (r,c) tuple.
        highlight: (r,c) or None
        """
        self.set_grid(grid)
        if highlight:
            r, c = highlight
            self.highlight_cell(r, c)

    def paintEvent(self, event):
        # 先由基类绘制表格与单元格
        super().paintEvent(event)

        # 在 viewport 上绘制粗线（不影响表头）
        painter = QPainter(self.viewport())
        pen = QPen(QColor(170, 170, 170))
        pen.setWidth(3)
        painter.setPen(pen)

        # 垂直粗线：在第 2 和 5 列之后绘制
        x = 0
        for c in range(9):
            x += self.columnWidth(c)
            if c in (2, 5):
                painter.drawLine(x, 0, x, self.viewport().height())

        # 水平粗线：在第 2 和 5 行之后绘制
        y = 0
        for r in range(9):
            y += self.rowHeight(r)
            if r in (2, 5):
                painter.drawLine(0, y, self.viewport().width(), y)

        painter.end()
