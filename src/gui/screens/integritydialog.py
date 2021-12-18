from PyQt5.QtWidgets import QDialog, QVBoxLayout

from gui.widgets.integrity import Integrity


class IntegrityDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setModal(False)
        self.setStyleSheet('background-color: #1e1e1e; color: white; font-size: 16px; font-weight: bold; font-family: Roboto;')
        self.setWindowTitle('Debug: Media Frames Integrity')
        self.resize(426, 240)

        self.integrity = Integrity()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.integrity)

        self.setLayout(self.layout)