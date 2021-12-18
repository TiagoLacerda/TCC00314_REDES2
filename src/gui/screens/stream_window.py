from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from gui.widgets.navbar import Navbar


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redes de Computadores II - Streaming Server")
        self.setWindowIcon(QIcon('src/assets/images/clapperboard-black.png'))
        self.setMinimumSize(640, 480)
        self.resize(800, 600)
        self.setStyleSheet('background-color: #1e1e1e; color: white; font-size: 16px; font-weight: bold; font-family: Consolas;')

        # --------------------------------------------------
        # Navbar

        self.navbar = Navbar()

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
        self.plaintextedit.setStyleSheet('border: 0px solid white;')

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
