import sys
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QFileDialog
from uiMainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)

    mainWindow = MainWindow()

    minimized = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'minimized':
            minimized = True

    if not minimized: mainWindow.show()

    try:
        sys.exit(app.exec_())
    except AttributeError:
        sys.exit(app.exec())