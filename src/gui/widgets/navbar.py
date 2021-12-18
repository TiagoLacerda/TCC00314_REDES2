from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel

from gui.widgets.roundpushbutton import RoundPushButton


class Navbar(QWidget):
    def __init__(self, height=48):
        super().__init__()
        #print('Navbar()')

        self.label = QLabel()
        self.label.setStyleSheet('color: #d72337; font-family: Roboto;')

        self.button1 = RoundPushButton(icon_path='src/assets/images/document.png', color='#286ed2', color_hover='#1e529d', color_press='#143769')
        self.button2 = RoundPushButton(icon_path='src/assets/images/ping.png',     color='#286ed2', color_hover='#1e529d', color_press='#143769')
        self.button3 = RoundPushButton(icon_path='src/assets/images/refresh.png',  color='#82af69', color_hover='#5f8849', color_press='#3f5b30')
        self.button4 = RoundPushButton(icon_path='src/assets/images/cross.png',    color='#d72337', color_hover='#a11a29', color_press='#500c14')

        self.containerLayout = QHBoxLayout()
        self.containerLayout.addWidget(self.label)
        self.containerLayout.addStretch()
        self.containerLayout.addWidget(self.button1)
        self.containerLayout.addWidget(QLabel('|'))
        self.containerLayout.addWidget(self.button2)
        self.containerLayout.addWidget(self.button3)
        self.containerLayout.addWidget(self.button4)

        self.container = QWidget()
        self.container.setLayout(self.containerLayout)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.setStyleSheet('background-color: #1f1f1f;')
        self.setFixedHeight(height)
