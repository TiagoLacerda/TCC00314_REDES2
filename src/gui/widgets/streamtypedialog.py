from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPainterPath
from PyQt5.QtWidgets import QOpenGLWidget, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel
from OpenGL.GL import *
from multipledispatch import *


# TODO: Make this class more customizable (just like RoundPushButton is)
class StreamTypeDialog(QDialog):
    def __init__(self, title='StreamTypeDialog'):
        super().__init__()
        self.setStyleSheet('background-color: #1f1f1f; color: white; font-size: 16px; font-weight: bold; font-family: Roboto;')
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout()

        self.button1 = QPushButton('APENAS PARA MIM')
        self.button1.clicked.connect(self.accept)
        self.button1.setStyleSheet('''
            QPushButton         {{background-color: {0}; height: {3}px; border-radius: {4}px;}}
            QPushButton:hover   {{background-color: {1}}} 
            QPushButton:pressed {{background-color: {2}}}
            '''.format('#d72337', '#a11a29', '#6b111b', 32, 2))

        self.button2 = QPushButton('PARA O GRUPO')
        self.button2.clicked.connect(self.accept)
        self.button2.setStyleSheet('''
            QPushButton         {{background-color: {0}; height: {3}px; border-radius: {4}px;}}
            QPushButton:hover   {{background-color: {1}}} 
            QPushButton:pressed {{background-color: {2}}}
            '''.format('#d72337', '#a11a29', '#6b111b', 32, 2))

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        self.setLayout(self.layout)

        self.button1.clicked.connect(self.button1_clicked)
        self.button2.clicked.connect(self.button2_clicked)

        self.option = 0

    def button1_clicked(self):
        self.option = 1
        self.close()

    def button2_clicked(self):
        self.option = 2
        self.close()

