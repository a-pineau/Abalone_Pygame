import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QGridLayout, 
                             QWidget, QLayout)


class PopUpWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game over! Play again/Quit?")
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)


def main():
    app = QApplication(sys.argv)
    win = PopupWindow()
    win.show()
    app.setStyle("Fusion")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
