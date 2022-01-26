from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget

from gui.widgets.roundpushbutton import RoundPushButton


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.button1 = RoundPushButton(size=32, color='#82af69', color_hover='#5f8849', color_press='#3f5b30', icon_path='src/assets/images/plus-solid.png')
        self.button2 = RoundPushButton(size=32, color='#d72337', color_hover='#a11a29', color_press='#6b111b', icon_path='src/assets/images/times-solid.png')
        self.button3 = RoundPushButton(size=32, color='#286ed2', color_hover='#1e529d', color_press='#143769', icon_path='src/assets/images/user-solid.png')
        self.button4 = RoundPushButton(size=32, color='#d72337', color_hover='#a11a29', color_press='#6b111b', icon_path='src/assets/images/user-minus-solid.png')
        self.button5 = RoundPushButton(size=32, color='#82af69', color_hover='#5f8849', color_press='#3f5b30', icon_path='src/assets/images/user-plus-solid.png')
        
        self.controlContainerLayout = QHBoxLayout()
        self.controlContainerLayout.addWidget(self.button1)
        self.controlContainerLayout.addWidget(self.button2)
        self.controlContainerLayout.addWidget(self.button3)
        self.controlContainerLayout.addWidget(self.button4)
        self.controlContainerLayout.addWidget(self.button5)

        self.controlContainer = QWidget()
        self.controlContainer.setLayout(self.controlContainerLayout)

        #

        self.resolutionLabel = QLabel('Resolução:')
        self.resolutionLabel.setContentsMargins(8, 8, 8, 8)

        self.resolutionComboBox = QComboBox()
        self.resolutionComboBox.setFixedHeight(24)
        self.resolutionComboBox.addItem('240p')  # 426x240
        self.resolutionComboBox.addItem('480p')  # 854x480
        self.resolutionComboBox.addItem('720p')  # 1280x720

        self.resolutionContainerLayout = QHBoxLayout()
        self.resolutionContainerLayout.addWidget(self.resolutionLabel)
        self.resolutionContainerLayout.addWidget(self.resolutionComboBox)
        self.resolutionContainerLayout.addStretch()

        self.resolutionContainer = QWidget()
        self.resolutionContainer.setLayout(self.resolutionContainerLayout)

        #

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.controlContainer)
        self.layout.addStretch()
        self.layout.addWidget(self.resolutionContainer)
        
        self.setLayout(self.layout)