# gui/board_widget.py
"""
Board widget for displaying and interacting with a 9x9 Sudoku grid.
This module provides the visual representation and input handling for Sudoku boards.
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QItemDelegate, QLineEdit
from PyQt5.QtGui import QFont, QColor, QBrush, QPainter, QPen, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
import numpy as np

class DigitDelegate(QItemDelegate):
    """
    Input delegate that restricts cell editing to a single digit (1-9).
    This ensures users can only enter valid Sudoku digits when editing cells.
    """
    def createEditor(self, parent, option, index):
        """
        Create an editor widget (QLineEdit) for cell input.
        - Restricts input to 1 character maximum
        - Validates input to only allow digits 1-9 (rejects 0 and non-digit characters)
        """
        editor = QLineEdit(parent)
        editor.setMaxLength(1)
        # Regular expression validator: only accepts digits 1-9
        validator = QRegExpValidator(QRegExp("^[1-9]$"), parent)
        editor.setValidator(validator)
        return editor

class BoardWidget(QTableWidget):
    """
    Main Sudoku board display widget.
    A 9x9 table widget that provides:
    - Visual display of the Sudoku grid with 3x3 box separators
    - User input handling with digit validation
    - Highlighting and color coding for visual feedback during solving
    """
    def __init__(self, parent=None):
        """Initialize a 9x9 Sudoku board table widget."""
        super().__init__(9, 9, parent)
        self._init_ui()
        # Store previous grid state for change detection (used during solving visualization)
        self._prev_grid = np.zeros((9,9), dtype=int)

    def _init_ui(self):
        """
        Initialize the board UI appearance and configuration.
        - Sets fixed size (543x543 pixels for a 9x9 grid of 60x60 cells)
        - Applies dark theme styling
        - Configures edit behavior (double-click, selection-triggered, or key-triggered)
        - Sets up cells with center alignment and editable flags
        - Applies the digit validator delegate to all cells
        """
        # Set fixed dimensions to match 9 cells × 60 pixels each
        self.setFixedSize(543, 543)
        # Allow editing via double-click, clicking, or pressing a key
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        # Hide row and column headers for a cleaner appearance
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        # Set monospace font for consistent digit display
        self.setFont(QFont("Consolas", 18))
        # Ensure the table gets keyboard focus when clicked
        self.setFocusPolicy(Qt.StrongFocus)
        # apply digit-only delegate for all cells
        self.setItemDelegate(DigitDelegate(self))
        # Initialize the 9x9 grid cells
        for r in range(9):
            self.setRowHeight(r, 60)
            for c in range(9):
                self.setColumnWidth(c, 60)
                # Create an empty cell with center alignment
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                # Allow selection, interaction, and editing
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self.setItem(r, c, item)
        # Apply border styling (thin cell borders + thicker box separators)
        self._apply_grid_lines()

    def _apply_grid_lines(self):
        """
        Apply dark theme styling with subtle cell borders.
        Thicker 3x3 box separators are drawn separately in paintEvent().
        Dark theme: #222 background, #ddd text, #444 gridlines
        """
        self.setStyleSheet("""
        QTableWidget::item { border: 1px solid #333; color: #ddd; background: #222; }
        QTableWidget { gridline-color: #444; }
        """)

    def get_grid(self) -> np.ndarray:
        """
        Extract the current grid state from the UI into a 9x9 numpy array.
        
        Parsing rules:
        - Empty cells or "." are treated as 0 (empty)
        - Only accepts first digit in range 1-9 from cell text
        - Invalid characters or 0 are converted to 0 (empty)
        
        Returns:
            numpy.ndarray: 9x9 integer array with values 0-9
        """
        grid = np.zeros((9,9), dtype=int)
        for r in range(9):
            for c in range(9):
                # Get cell text and strip whitespace
                txt = self.item(r, c).text().strip() if self.item(r, c) else ""
                if txt == "" or txt == ".":
                    # Empty cell
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
        """
        Display a grid state on the board UI.
        
        Args:
            grid (numpy.ndarray): 9x9 array of integers (0-9, where 0 = empty)
        
        Displays non-zero values as digits, and 0 as empty cells.
        """
        grid = np.array(grid, dtype=int)
        for r in range(9):
            for c in range(9):
                v = grid[r, c]
                # Convert 0 to empty string, others to digit string
                text = "" if v == 0 else str(int(v))
                self.item(r, c).setText(text)

    def clear(self):
        """Clear all cells on the board (set all to empty)."""
        for r in range(9):
            for c in range(9):
                self.item(r, c).setText("")

    def highlight_cell(self, r: int, c: int, temporary=True):
        """
        Highlight a single cell to draw user attention (used for solving animation).
        
        Args:
            r (int): Row index (0-8)
            c (int): Column index (0-8)
            temporary (bool): If True, caller is responsible for clearing highlight via QTimer
        
        Sets cell background to blue (#3c78c8) and text to white.
        """
        if not (0 <= r < 9 and 0 <= c < 9):
            return
        item = self.item(r, c)
        if item is None:
            return
        # apply bright background for a short time (caller handles timer)
        item.setBackground(QBrush(QColor(60, 120, 200)))
        item.setForeground(QBrush(QColor(255, 255, 255)))

    def mark_final(self, r: int, c: int):
        """
        Mark a cell with final solution styling (distinct color).
        Used to distinguish solver-assigned values from user input.
        
        Args:
            r (int): Row index (0-8)
            c (int): Column index (0-8)
        
        Applies dark green background (#145014) with light green text.
        """
        item = self.item(r, c)
        if item:
            item.setBackground(QBrush(QColor(20, 80, 20)))
            item.setForeground(QBrush(QColor(220, 255, 220)))

    def show_grid_snapshot(self, grid: np.ndarray, highlight=None):
        """
        Display a grid snapshot and optionally highlight a specific cell.
        Used during solving animation to show intermediate steps.
        
        Args:
            grid (numpy.ndarray): 9x9 grid to display
            highlight (tuple or None): (row, col) tuple to highlight, or None for no highlight
        """
        self.set_grid(grid)
        if highlight:
            r, c = highlight
            self.highlight_cell(r, c)

    def paintEvent(self, event):
        """
        Override paint event to draw thick 3x3 box separators.
        The default grid lines (thin 1px borders) are handled by stylesheet.
        This method draws additional 3px-wide lines after columns 2, 5 and rows 2, 5
        to create the classic Sudoku 3x3 box structure.
        """
        # First, draw the standard cell borders and content via parent paintEvent
        super().paintEvent(event)

        # Create a painter for drawing 3x3 box separators
        painter = QPainter(self.viewport())
        pen = QPen(QColor(170, 170, 170))
        pen.setWidth(3)
        painter.setPen(pen)

        # Draw vertical separators between 3x3 boxes
        # These appear after columns 2 and 5 (total width spans columns 0-2, 3-5, 6-8)
        x = 0
        for c in range(9):
            x += self.columnWidth(c)
            if c in (2, 5):
                painter.drawLine(x, 0, x, self.viewport().height())

        # Draw horizontal separators between 3x3 boxes
        # These appear after rows 2 and 5 (total height spans rows 0-2, 3-5, 6-8)
        y = 0
        for r in range(9):
            y += self.rowHeight(r)
            if r in (2, 5):
                painter.drawLine(0, y, self.viewport().width(), y)

        painter.end()
