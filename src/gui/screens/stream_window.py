from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from gui.widgets.navbar import Navbar


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redes de Computadores II - Streaming Server")
        self.setMinimumSize(640, 480)
        self.resize(800, 600)
        self.setStyleSheet('background-color: #0f0f0f; color: white; font-size: 16px; font-weight: bold; font-family: Consolas;')

        self.navbar = Navbar()
        self.navbar.addButton(icon_path='src/assets/images/film-solid.png',     color='#286ed2', color_hover='#1e529d', color_press='#143769')
        self.navbar.addSeparator()
        self.navbar.addButton(icon_path='src/assets/images/sync-alt-solid.png', color='#82af69', color_hover='#5f8849', color_press='#3f5b30')
        self.navbar.addButton(icon_path='src/assets/images/times-solid.png',    color='#d72337', color_hover='#a11a29', color_press='#500c14')

        # --------------------------------------------------
        # List of videos

        self.videoListLayout = QVBoxLayout()
        self.videoListLayout.addStretch()

        self.videoList = QWidget()
        self.videoList.setLayout(self.videoListLayout)

        self.videoListScrollArea = QScrollArea()

        self.videoListScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.videoListScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.videoListScrollArea.setWidgetResizable(True)
        self.videoListScrollArea.setStyleSheet('border: 0px;')
        self.videoListScrollArea.setWidget(self.videoList)

        # --------------------------------------------------
        # Log (QPlainTextEdit)

        self.plaintextedit = QPlainTextEdit()
        self.plaintextedit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.plaintextedit.setReadOnly(True)
        self.plaintextedit.setStyleSheet('border: 0px solid white; color: #b6b6b6; font-size: 14px; font-weight: 700; font-family: Consolas;')

        # --------------------------------------------------

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.videoListScrollArea)
        self.splitter.addWidget(self.plaintextedit)
        self.splitter.setStretchFactor(0, 100)
        self.splitter.setStretchFactor(1,  1)
        self.splitter.setStyleSheet('QSplitter::handle {background: #3c3c3c;} QSplitter {border: 4px solid #3c3c3c;}')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.navbar)
        self.layout.addWidget(self.splitter)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)
