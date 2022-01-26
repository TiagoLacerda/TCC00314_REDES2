import sys
from PyQt5 import QtWidgets
import cv2
import subprocess
import socket

import os
import threading
import time

from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
from thread.streamudpthread import StreamUDPThread

from utility import Utility
from gui.screens.stream_window import Window
from gui.widgets.videoinfo import VideoInfo

from datetime import datetime


class MyWindow(Window):
    insertVideoInfoSignal = pyqtSignal(str, str, QPixmap)
    deleteVideoInfoSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.envoyLength = 4
        self.bufferSize = 2**14  # 2**15 = 65536, 2**12 = 4096

        self.tcpTarget = ('localhost', 6060)
        self.tcpSocket = None

        self.udpTarget = ('localhost', 50505)
        self.udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpSocket.bind(self.udpTarget)

        self.udpThread = StreamUDPThread(self.udpTarget, self.udpSocket, self.bufferSize)
        self.udpThread.logger.connect(self.log)
        self.insertVideoInfoSignal.connect(self.udpThread.insertVideoInfo)
        self.deleteVideoInfoSignal.connect(self.udpThread.deleteVideoInfo)
        self.udpThread.start()

        self.navbar.buttons[0].clicked.connect(self.showFileDialog)
        self.navbar.buttons[1].clicked.connect(lambda: self.log('Botão de refresh ainda não implementado'))
        self.navbar.buttons[1].hide()
        self.navbar.buttons[2].clicked.connect(self.quit)

    @pyqtSlot(str)
    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        message = '[{}] {}'.format(now, message)
        print(message)
        self.plaintextedit.appendPlainText(message)

    def showFileDialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter('Videos (*.mp4)')
        # dialog.setFilter()
        if dialog.exec():

            oldfiles = []
            for widget in self.selectVideoInfoWidgets():
                oldfiles.append(widget.fullpath)

            newfiles = dialog.selectedFiles()
            for fullpath in newfiles:
                fullpath = fullpath.replace('\\', '/')

                if fullpath in oldfiles:
                    continue

                cwd = os.getcwd().replace('\\', '/')
                path = fullpath.split(cwd)[-1]
                title = ' '.join((path.split('/')[-1].split('.')[0]).split('_'))
                thumbnail = Utility.getThumbnail(fullpath, int(96 * 16.0 / 9.0), 96)

                self.log('\nfullpath: {}\ncwd:      {}\npath:     {}\ntitle:    {}\n'.format(fullpath, cwd, path, title))

                widget = VideoInfo(fullpath, title, thumbnail, read_only=False, icon_path='src/assets/images/trash-alt-solid.png')
                widget.button.clicked.connect(self.deleteVideoInfo)
                self.videoListLayout.insertWidget(0, widget)

                self.insertVideoInfoSignal.emit(fullpath, title, thumbnail)

    def deleteVideoInfo(self):
        widget = self.sender().parent().parent()
        fullpath = widget.fullpath
        self.deleteVideoInfoSignal.emit(fullpath)
        widget.deleteLater()

    def selectVideoInfoWidgets(self):
        widgets = []
        for i in range(self.videoListLayout.count()):
            widget = self.videoListLayout.itemAt(i).widget()
            if widget is not None:
                widgets.append(widget)
        return widgets

    def quit(self):
        # TODO: Gracefully end connections
        qApp.quit()


subprocess.run('cls', shell=True)

app = QApplication(sys.argv)
# app.setStyleSheet('QToolTip {background-color: #1e1e1e !important; border: 1px solid #1e1e1e; padding: 2px; font-family: Roboto !important;}')
# QToolTip {background-color: #1e1e1e; color: white; font-size: 16px; font-weight: bold; font-family: Consolas;}
gui = MyWindow()
gui.show()
app.exec()
