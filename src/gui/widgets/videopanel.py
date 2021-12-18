from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class VideoPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.listLayout = QVBoxLayout()
        self.listLayout.addStretch()
        self.list = QWidget()
        self.list.setLayout(self.listLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet('border: 0px;')
        self.scrollArea.setWidget(self.list)

        self.containterLayout = QVBoxLayout()        
        self.containterLayout.addWidget(self.scrollArea)
        self.containterLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.containterLayout)
