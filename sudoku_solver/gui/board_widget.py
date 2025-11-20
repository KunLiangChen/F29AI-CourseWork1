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
        self.is_solved = False    

    def _on_cell_changed(self, r, c):
        # 1. 阻止信号，防止无限递归
        self.blockSignals(True)
        
        try:
            # 仅在非初始值的可编辑单元格上进行样式更新
            if self._initial_grid[r, c] == 0:
                grid = self.get_grid()
                v = grid[r, c]
                text = "" if v == 0 else str(int(v))
                item = self.item(r, c)

                # 沿用 set_grid 中的用户输入样式逻辑 (亮灰白)
                # 注意：item.setText(text) 在某些Qt版本中可能会再次触发 cellChanged
                item.setText(text) 
                
                # 用户输入时的样式 (求解器运行前)
                COLOR_USER = QColor("#E0E0E0") 
                COLOR_BACKGROUND = QColor("#1A1A2E")
                
                item.setFont(QFont("Consolas", 18))
                item.setForeground(QBrush(COLOR_USER)) 
                item.setBackground(QBrush(COLOR_BACKGROUND))
                # 确保编辑权限依然存在
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)

        finally:
            # 2. 恢复信号发射
            self.blockSignals(False)

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
        self.cellChanged.connect(self._on_cell_changed)

    

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
        """Update the display based on the numpy grid."""
        for r in range(9):
            for c in range(9):
                v = grid[r, c]
                item = self.item(r, c)
                if item is None:
                    # Create item if it doesn't exist
                    item = QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(r, c, item)
                
                # Check for existing value for coloring
                initial_v = self._initial_grid[r, c]

                if v == 0:
                    item.setText("")
                else:
                    item.setText(str(v))

                # Apply styling
                if initial_v != 0:
                    # 1. Initial number (fixed)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setBackground(QBrush(QColor("#1A1A2E"))) # Background from CSS
                    item.setForeground(QBrush(QColor("#B0C4DE"))) # Initial value color
                elif v != 0 and self.is_solved:
                    # 2. Solved number (Final state, solver-assigned). CHANGE HERE: Use green text.
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    # 更改为绿色字体，并使用深色背景
                    item.setBackground(QBrush(QColor("#1A1A2E"))) # 主题背景色
                    item.setForeground(QBrush(QColor("#81C784"))) # 柔和的亮绿色文字
                elif v != 0:
                    # 3. Solved number (During solving process - intermediate step)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    # Use standard green font for solver-filled during animation
                    item.setForeground(QBrush(QColor("#4CAF50"))) # 标准绿色文字
                    item.setBackground(QBrush(QColor("#1A1A2E"))) # 主题背景色
                else:
                    # 4. Empty cell (editable, including user-inputted cells if set_grid is called)
                    # Note: User input coloring is mostly handled by _on_cell_changed 
                    # but this provides a fallback for resets/updates.
                    item.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setBackground(QBrush(QColor("#1A1A2E"))) # Background from CSS
                    item.setForeground(QBrush(QColor("#E0E0E0"))) # User input color (white/light gray)

    def clear(self):
        # 1. 重置初始网格状态和求解状态
        self._initial_grid = np.zeros((9,9), dtype=int) 
        self.is_solved = False # 确保重置状态

        # 2. 清除所有单元格文本并恢复默认样式
        font = QFont("Consolas", 18)
        default_fg_color = QColor("#E0E0E0") # 使用用户输入颜色作为默认色
        default_bg_color = QColor("#1A1A2E") # 和主背景一致

        # 遍历单元格时阻止信号，防止 set_grid 内部修改触发 cellChanged
        self.blockSignals(True) 
        
        try:
            for r in range(9):
                for c in range(9):
                    item = self.item(r, c)
                    item.setText("")
                    
                    # 彻底恢复默认样式 (亮灰白/主背景)
                    item.setFont(font)
                    item.setForeground(QBrush(default_fg_color))
                    item.setBackground(QBrush(default_bg_color))
                    
                    # 恢复编辑权限
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        finally:
            self.blockSignals(False)
                

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
