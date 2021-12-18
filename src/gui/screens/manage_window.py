
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from datetime import datetime

import subprocess
import sys
import os


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redes de Computadores II - Management Server")
        self.setWindowIcon(QIcon('../assets/images/clapperboard.png'))
        self.setMinimumSize(640, 480)

        # -------------------- TOOLBAR ---------------------

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(QAction(QIcon(os.path.join(os.getcwd(), 'src/assets/images/eraser-white.png')), 'Erase', self.toolbar))

        self.toolbar.actionTriggered[QAction].connect(self.toolbarActionTriggered)

        # ---------------------- LOG -----------------------
        
        self.plaintextedit = QPlainTextEdit()
        self.plaintextedit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.plaintextedit.setReadOnly(True)

        self.setCentralWidget(self.plaintextedit)

        # ------------------- STYLESHEET -------------------

        self.setStyleSheet('background-color: #1e1e1e; color: white; font-size: 16px; font-weight: bold; font-family: Consolas;')
        self.toolbar.setStyleSheet('background-color: #3c3c3c;')
        self.plaintextedit.setStyleSheet('border: 0px solid white;')

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
