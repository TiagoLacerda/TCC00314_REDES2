
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from datetime import datetime

import subprocess
import sys
import os

from gui.widgets.navbar import Navbar


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redes de Computadores II - Management Server")
        self.setWindowIcon(QIcon('../assets/images/clapperboard.png'))
        self.setMinimumSize(640, 480)
        self.setStyleSheet('background-color: #0f0f0f;')

        self.navbar = Navbar()
        self.navbar.addButton(icon_path='src/assets/images/eraser-solid.png', color='#d72337', color_hover='#a11a29', color_press='#500c14')
        self.navbar.addButton(icon_path='src/assets/images/times-solid.png',  color='#d72337', color_hover='#a11a29', color_press='#500c14')

        # ---------------------- LOG -----------------------

        self.plaintextedit = QPlainTextEdit()
        self.plaintextedit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.plaintextedit.setReadOnly(True)
        self.plaintextedit.setStyleSheet('border: 0px solid white; color: #b6b6b6; font-size: 14px; font-weight: 700; font-family: Consolas;')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.navbar)
        self.layout.addWidget(self.plaintextedit)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def toolbarActionTriggered(self, args):
        when = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if args.text() == 'Erase':
            self.plaintextedit.clear()
            subprocess.run('cls', shell=True)
            print('Erased called at {}'.format(when))


# # TODO: Remove window initialization
# app = QApplication(sys.argv)
# gui = Window()
# gui.show()
# app.exec()
