from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel('Resolução:')
        self.label.setContentsMargins(8, 8, 8, 8)

        self.comboBox = QComboBox()
        self.comboBox.setFixedHeight(24)
        self.comboBox.addItem('240p')  # 426x240
        self.comboBox.addItem('480p')  # 854x480
        self.comboBox.addItem('720p')  # 1280x720

        self.resolutionContainerLayout = QHBoxLayout()
        self.resolutionContainerLayout.addWidget(self.label)
        self.resolutionContainerLayout.addWidget(self.comboBox)
        self.resolutionContainerLayout.addStretch()

        self.setLayout(self.resolutionContainerLayout)