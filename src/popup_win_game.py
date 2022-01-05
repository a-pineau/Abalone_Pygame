import sys
import pygame
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QGridLayout, 
                             QWidget, QLayout)



class PopUpWindow(QMainWindow):
    def __init__(self, abalone):
        super().__init__()
        self.abalone = abalone
        self.setWindowTitle("Play again/Quit game?")
        self.setFixedHeight(100)
        self.setFixedWidth(290)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.h_box = QtWidgets.QHBoxLayout(self.central_widget)
        self.pbutton_replay = QtWidgets.QPushButton(text="Replay")
        self.pbutton_replay.clicked.connect(self.reset_game)
        self.pbutton_replay.setFixedHeight(80)
        self.pbutton_quit = QtWidgets.QPushButton(text="Quit Game")
        self.pbutton_quit.clicked.connect(self.set_run_game)
        self.pbutton_quit.setFixedHeight(80)
        self.h_box.addWidget(self.pbutton_replay)
        self.h_box.addWidget(self.pbutton_quit)
        self.run_game = True

    @QtCore.pyqtSlot()
    def reset_game(self):
        self.abalone.reset_game()
        self.close()

    @QtCore.pyqtSlot()
    def set_run_game(self):
        self.run_game = False

    def get_run_game(self):
        return self.run_game


def main():
    pass

if __name__ == "__main__":
    main()
