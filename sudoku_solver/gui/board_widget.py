# gui/board_widget.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QItemDelegate, QLineEdit,QHeaderView
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
        self._initial_grid = np.zeros((9,9), dtype=int)
    def _init_ui(self):
        self.setFixedSize(723, 723)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setVisible(False)
        self.setFont(QFont("Consolas", 18))
        self.setFocusPolicy(Qt.StrongFocus)
        # apply digit-only delegate for all cells
        self.setItemDelegate(DigitDelegate(self))
        for r in range(9):
            self.setRowHeight(r, 80)
            for c in range(9):
                self.setColumnWidth(c, 80)
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self.setItem(r, c, item)
        self._apply_grid_lines()

    def _apply_grid_lines(self):
        # keep thin cell borders via stylesheet; thicker 3x3 separators drawn in paintEvent
        self.setStyleSheet("""
            QTableWidget::item { border: 1px solid #3B4A6B; } /* 和按钮边框颜色一致 */
            QTableWidget { gridline-color: #3B4A6B; } 
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

    def capture_initial_state(self, grid: np.ndarray):
        self._initial_grid = np.where(grid != 0, grid, 0).copy()
        self.set_grid(grid)

    def set_grid(self, grid: np.ndarray):
        grid = np.array(grid, dtype=int)
        font = QFont("Consolas", 18)
        bold_font = QFont("Consolas", 18, QFont.Bold) # 粗体用于初始值

        for r in range(9):
            for c in range(9):
                item = self.item(r, c)
                v = grid[r, c]
                text = "" if v == 0 else str(int(v))

                # 初始值 (Fixed)
                if self._initial_grid[r, c] != 0:
                    item.setText(text)
                    item.setFont(bold_font)
                    item.setForeground(QBrush(QColor("#FFFFFF"))) # 初始值用纯白
                    item.setBackground(QBrush(QColor("#222233"))) # 深蓝灰色背景
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # 不可编辑
                # 求解器/用户填入的值 (Editable)
                else:
                    item.setText(text)
                    item.setFont(font)
                    item.setForeground(QBrush(QColor("#4CAF50"))) # 绿色字体
                    item.setBackground(QBrush(QColor("#1A1A2E"))) # 和主背景一致
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

    def clear(self):
        # 1. 重置初始网格状态为全零 (新增)
        self._initial_grid = np.zeros((9,9), dtype=int) 
        # 2. 清除所有单元格文本
        for r in range(9):
            for c in range(9):
                # 确保在清空文本后，恢复单元格的编辑权限和默认样式
                item = self.item(r, c)
                item.setText("")
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable) 
                

    def highlight_cell(self, r: int, c: int, temporary=True):
        """Highlight a single cell (used for animation)."""
        if not (0 <= r < 9 and 0 <= c < 9):
            return
        item = self.item(r, c)
        if item is None:
            return
        # apply bright background for a short time (caller handles timer)
        item.setBackground(QBrush(QColor("#FFD700"))) # 亮金色
        item.setForeground(QBrush(QColor("#1A1A2E"))) # 深色字体，高对比度

    def mark_final(self, r: int, c: int):
        """Make final assigned cell style (a bit different)."""
        item = self.item(r, c)
        if item:
            item.setBackground(QBrush(QColor("#4CAF50").darker(150))) # 略深的绿色
            item.setForeground(QBrush(QColor("#FFFFFF")))

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
        
        super().paintEvent(event)

        
        painter = QPainter(self.viewport())
        pen = QPen(QColor(170, 170, 170))
        pen.setWidth(3)
        painter.setPen(pen)

        
        x = 0
        for c in range(9):
            x += self.columnWidth(c)
            if c in (2, 5):
                painter.drawLine(x, 0, x, self.viewport().height())

       
        y = 0
        for r in range(9):
            y += self.rowHeight(r)
            if r in (2, 5):
                painter.drawLine(0, y, self.viewport().width(), y)

        painter.end()
