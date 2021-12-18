from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
from gui.widgets.controlpanel import ControlPanel

from gui.widgets.navbar import Navbar
from gui.widgets.roundpushbutton import RoundPushButton
from gui.widgets.videopanel import VideoPanel


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.label1 = QLabel('Usuário')

        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setTextMargins(8, 0, 8, 0)
        self.lineEdit1.setStyleSheet('QLineEdit {height: 32px; border-radius: 16px; background-color: #181818;}')

        self.label2 = QLabel('Senha')

        self.lineEdit2 = QLineEdit()
        self.lineEdit2.setEchoMode(QLineEdit.Password)
        self.lineEdit2.setTextMargins(8, 0, 8, 0)
        self.lineEdit2.setStyleSheet('QLineEdit {height: 32px; border-radius: 16px; background-color: #181818;}')

        self.button1 = QPushButton('ACESSAR')
        self.button1.setStyleSheet(
            'QPushButton {height: 32px; border-radius: 16px; background-color: #d72337;} QPushButton:hover {background-color: #a11a29} QPushButton:pressed {background-color: #500c14}')

        self.label3 = QLabel('Ainda não possui conta? Registre-se agora!')
        self.label3.setAlignment(Qt.AlignCenter)

        self.button2 = QPushButton('REGISTRAR-SE')
        self.button2.setStyleSheet(
            'QPushButton {height: 32px; border-radius: 16px; background-color: #286ed2;} QPushButton:hover {background-color: #1e529d} QPushButton:pressed {background-color: #143769}')

        self.label4 = QLabel('')
        self.label4.setStyleSheet('color: #d72337;')

        self.button3 = RoundPushButton(icon_path='src/assets/images/refresh.png', color='#82af69', color_hover='#5f8849', color_press='#3f5b30')
        self.button3.hide()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.setMinimumWidth(480)

        self.layout.addStretch()
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.lineEdit1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.lineEdit2)
        self.layout.addWidget(self.button1)
        self.layout.addSpacing(24)
        self.layout.addWidget(self.label3)
        self.layout.addWidget(self.button2)
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label4, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button3, alignment=Qt.AlignCenter)
        self.layout.addStretch()

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.container.setFixedWidth(480)

        self.hboxlayout = QHBoxLayout()
        self.hboxlayout.addStretch()
        self.hboxlayout.addWidget(self.container)
        self.hboxlayout.addStretch()

        self.setLayout(self.hboxlayout)


class RegisterPage(QWidget):
    def __init__(self):
        super().__init__()

        self.label1 = QLabel('Usuário')
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setTextMargins(8, 0, 8, 0)
        self.lineEdit1.setStyleSheet('QLineEdit {height: 32px; border-radius: 16px; background-color: #181818;}')

        self.label2 = QLabel('Senha')
        self.lineEdit2 = QLineEdit()
        self.lineEdit2.setEchoMode(QLineEdit.Password)
        self.lineEdit2.setTextMargins(8, 0, 8, 0)
        self.lineEdit2.setStyleSheet('QLineEdit {height: 32px; border-radius: 16px; background-color: #181818;}')

        self.label3 = QLabel('Código Premium')
        self.lineEdit3 = QLineEdit()
        self.lineEdit3.setEchoMode(QLineEdit.Password)
        self.lineEdit3.setTextMargins(8, 0, 8, 0)
        self.lineEdit3.setStyleSheet('QLineEdit {height: 32px; border-radius: 16px; background-color: #181818;}')

        self.button1 = QPushButton('REGISTRAR-SE')
        self.button1.setStyleSheet(
            'QPushButton {height: 32px; border-radius: 16px; background-color: #d72337;} QPushButton:hover {background-color: #a11a29} QPushButton:pressed {background-color: #500c14}')

        self.button2 = QPushButton('VOLTAR')
        self.button2.setStyleSheet(
            'QPushButton {height: 32px; border-radius: 16px; background-color: #286ed2;} QPushButton:hover {background-color: #1e529d} QPushButton:pressed {background-color: #143769}')
        self.button2.setIcon(QIcon(os.getcwd() + '/src/assets/images/arrow-left-white.png'))
        # self.return_PushButton.setFixedSize(32,32)

        self.label4 = QLabel('')
        self.label4.setStyleSheet('color: #d72337;')

        self.button3 = RoundPushButton(icon_path='src/assets/images/refresh.png', color='#82af69', color_hover='#5f8849', color_press='#3f5b30')
        self.button3.hide()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.setMinimumWidth(480)

        self.layout.addStretch()
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.lineEdit1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.lineEdit2)
        self.layout.addWidget(self.label3)
        self.layout.addWidget(self.lineEdit3)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addSpacing(8)
        self.layout.addWidget(self.label4, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button3, alignment=Qt.AlignCenter)
        self.layout.addStretch()

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.container.setFixedWidth(480)

        self.hboxlayout = QHBoxLayout()
        self.hboxlayout.addStretch()
        self.hboxlayout.addWidget(self.container)
        self.hboxlayout.addStretch()

        self.setLayout(self.hboxlayout)


class MainPage(QWidget):
    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # Navbar

        self.navbar = Navbar()

        # --------------------------------------------------
        # Room management

        self.controlPanel = ControlPanel()

        # --------------------------------------------------
        # Media

        self.mediaVideoLabel = QLabel()
        self.mediaVideoLabel.setMinimumSize(1, 1)

        self.mediaTitleLabel = QLabel()
        self.mediaTitleLabel.setWordWrap(True)

        self.containerMLayout = QVBoxLayout()
        self.containerMLayout.addWidget(self.mediaVideoLabel, alignment=Qt.AlignCenter)
        # self.mediaContainerLayout.addWidget(self.mediaTitleLabel)

        self.mediaPanel = QWidget()
        self.mediaPanel.setLayout(self.containerMLayout)
        self.mediaPanel.setStyleSheet('background-color: black;')

        # --------------------------------------------------
        # Video selection

        self.videoPanel = VideoPanel()

        # --------------------------------------------------
        # Logger

        self.plaintextedit = QPlainTextEdit()
        self.plaintextedit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.plaintextedit.setReadOnly(True)
        self.plaintextedit.setStyleSheet('border: 0px solid white; font-weight: 600; font-family: Consolas;')

        # --------------------------------------------------
        # Where it all comes together

        self.screenHSplitter = QSplitter()
        self.screenHSplitter.setOrientation(Qt.Horizontal)
        self.screenHSplitter.addWidget(self.controlPanel)
        self.screenHSplitter.addWidget(self.mediaPanel)
        self.screenHSplitter.addWidget(self.videoPanel)
        self.screenHSplitter.setStretchFactor(0, 1)
        self.screenHSplitter.setStretchFactor(1, 10)
        self.screenHSplitter.setStretchFactor(2, 5)

        self.screenVSplitter = QSplitter()
        self.screenVSplitter.setOrientation(Qt.Vertical)
        self.screenVSplitter.addWidget(self.screenHSplitter)
        self.screenVSplitter.addWidget(self.plaintextedit)
        self.screenVSplitter.setStretchFactor(0, 100)
        self.screenVSplitter.setStretchFactor(1, 1)
        self.screenVSplitter.setStyleSheet('QSplitter::handle {background: #3c3c3c;} QSplitter {border: 4px solid #3c3c3c;}')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.navbar)
        self.layout.addWidget(self.screenVSplitter)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redes de Computadores II - Client")
        self.setWindowIcon(QIcon('src/assets/images/clapperboard-black.png'))
        self.setMinimumSize(640, 480)
        self.resize(800, 600)

        # -------------------- WIDGETS ---------------------

        self.page1 = LoginPage()
        self.page2 = RegisterPage()
        self.page3 = MainPage()

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.page1)
        self.stackedWidget.addWidget(self.page2)
        self.stackedWidget.addWidget(self.page3)
        self.stackedWidget.setCurrentIndex(0)

        self.setCentralWidget(self.stackedWidget)

        # ------------------- STYLESHEET -------------------

        self.setStyleSheet('background-color: #1e1e1e; color: white; font-size: 16px; font-weight: bold; font-family: Roboto;')


# app = QApplication(sys.argv)
# app.setStyleSheet('QToolTip {background-color: black; color: white; border: black solind 1px;}')
# gui = Window()
# gui.show()
# app.exec()
