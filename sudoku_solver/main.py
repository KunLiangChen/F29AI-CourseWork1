# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt5.QtCore import QFile, QTextStream

def load_stylesheet(app, path="gui/styles.qss"):
    try:
        f = QFile(path)
        if f.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(f)
            app.setStyleSheet(stream.readAll())
            f.close()
    except Exception:
        pass

def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
