from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel

from gui.widgets.roundpushbutton import RoundPushButton


class Navbar(QWidget):
    def __init__(self, height=64):
        super().__init__()
        #print('Navbar()')

        self.label = QLabel()
        self.label.setStyleSheet('color: #d72337; font-family: Roboto;')

        self.buttons = []

        # self.button1 = RoundPushButton(icon_path='src/assets/images/sync-alt-solid.png', color='#286ed2', color_hover='#1e529d', color_press='#143769')
        # # self.button2 = RoundPushButton(icon_path='src/assets/images/ping.png',         color='#286ed2', color_hover='#1e529d', color_press='#143769')
        # self.button3 = RoundPushButton(icon_path='src/assets/images/sync-alt-solid.png', color='#82af69', color_hover='#5f8849', color_press='#3f5b30')
        # self.button4 = RoundPushButton(icon_path='src/assets/images/stop-solid.png',     color='#d72337', color_hover='#a11a29', color_press='#500c14')
        # self.button5 = RoundPushButton(icon_path='src/assets/images/times-solid.png',    color='#d72337', color_hover='#a11a29', color_press='#500c14')

        self.containerLayout = QHBoxLayout()
        self.containerLayout.addWidget(self.label)
        self.containerLayout.addStretch()
        # self.containerLayout.addWidget(self.button1)
        # self.containerLayout.addWidget(QLabel('|'))
        # # self.containerLayout.addWidget(self.button2)
        # self.containerLayout.addWidget(self.button3)
        # self.containerLayout.addWidget(self.button4)
        # self.containerLayout.addWidget(self.button5)

        self.container = QWidget()
        self.container.setLayout(self.containerLayout)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.setStyleSheet('background-color: #1f1f1f;')
        self.setFixedHeight(height)

    def addButton(self, size=48, color='#d72337', color_hover='#a11a29', color_press='#6b111b', icon_path=None, tooltip=None):
        button = RoundPushButton(size, color, color_hover, color_press, icon_path, tooltip)
        self.buttons.append(button)
        self.containerLayout.addWidget(button)

    def addSeparator(self):
        self.containerLayout.addWidget(QLabel('|'))
