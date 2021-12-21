from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, qApp
from PyQt5.QtGui import QPixmap
from datetime import datetime

import sys
import socket
import subprocess
from gui.screens.integritydialog import IntegrityDialog
from gui.widgets.integrity import Integrity
from gui.widgets.videoinfo import VideoInfo
from thread.clientudpthread import ClientUDPThread

from utility import Utility

from gui.screens.client_window import Window
from thread.mediathread import MediaThread
from database import User


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        # Media stuff

        self.resolutions = {'240p': '426 240', '480p': '854 480', '720p': '1280 720'}

        # Socket stuff

        self.envoyLength = 4
        self.bufferSize = 2**14  # 2**15 = 65536, 2**12 = 4096

        self.tcpTarget = ('localhost', 6060)
        self.tcpSocket = None

        self.udpTarget = ('localhost', 50505)
        self.udpSocket = None

        self.configureSockets()

        self.udpThread = ClientUDPThread(self.udpTarget, self.udpSocket, self.bufferSize)
        self.udpThread.logger.connect(self.log)
        self.udpThread.updateVideoFrameSignal.connect(self.updateVideoFrame)
        self.udpThread.insertVideoInfoSignal.connect(self.insertVideoInfo)
        self.udpThread.start()  # TODO: Do this after init

        # PyQt stuff

        self.page3.navbar.button1.clicked.connect(self.requestVideoInfo)
        self.page3.navbar.button3.clicked.connect(self.configureSockets)
        self.page3.navbar.button4.clicked.connect(self.cancelStream)
        self.page3.navbar.button5.clicked.connect(self.quit)

        self.setPage(2)

        self.integrityDialog = IntegrityDialog()
        self.integrityDialog.open()


    @pyqtSlot(str)
    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        message = '[{}]: {}'.format(now, message)
        print(message)
        self.page3.plaintextedit.appendPlainText(message)

    @pyqtSlot(QPixmap)
    def updateVideoFrame(self, pixmap):
        # Expands the pixmap
        size = self.page3.mediaPanel.size()
        scale = min(size.width() / pixmap.width(), size.height() / pixmap.height())
        self.page3.mediaVideoLabel.setPixmap(pixmap.scaled(pixmap.width() * scale, pixmap.height() * scale))

    def setAlert(self, alert):
        self.page1.label4.setText(alert)
        self.page2.label4.setText(alert)
        self.page3.navbar.label.setText(alert)

    def setPage(self, index):
        self.setAlert('')
        self.stackedWidget.setCurrentIndex(index)

    # TODO: Do I need to reopen sockets that raised exceptions?
    def configureSockets(self):
        if self.tcpSocket is not None:
            self.tcpSocket.close()

        self.tcpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udpSocket.settimeout(1.0)

        # try:
        #     self.setAlert('')
        #     self.tcpSocket.connect(self.tcpTarget)
        #     self.log('Connection successful!')
        #     self.page1.button3.hide()
        #     self.page2.button3.hide()
        #     self.page3.navbar.button3.hide()

        # except Exception as e:
        #     self.setAlert('Connection failed!')
        #     self.log('Connection failed!')
        #     self.log(str(e))
        #     self.page1.button3.show()
        #     self.page2.button3.show()
        #     self.page3.navbar.button3.show()

    def cancelStream(self):
        # TODO: Is it okay to directly call a QThread method? Without a signal?
        self.udpThread.closeMediaThread()
        Utility.sendUDPMessages(self.udpSocket, self.udpTarget, ['cancel'], True)
    
    def quit(self):
        self.cancelStream()
        qApp.quit()

    @pyqtSlot(QWidget)
    def requestStream(self, videoInfo):
        try:
            self.cancelStream()
            i = str(self.page3.controlPanel.comboBox.currentText())
            w, h = self.resolutions[i].split(' ')
            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, ['stream', 'tiago', videoInfo.fullpath, w, h], True)
        except Exception as e:
            self.log(str(e))

    def requestVideoInfo(self):
        try:
            videoListLayout = self.page3.videoPanel.listLayout
            for i in range(videoListLayout.count()):
                widget = videoListLayout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, ['videoinfolist'], True)
        except Exception as e:
            print(str(e))

    @pyqtSlot(str, str, QPixmap)
    def insertVideoInfo(self, fullpath, title, thumbnail):
        print('insertVideoInfo(title=\'{}\')'.format(title))

        videoListLayout = self.page3.videoPanel.listLayout
        for i in range(videoListLayout.count()):
            widget = videoListLayout.itemAt(i).widget()
            if widget is not None and widget.fullpath == fullpath:
                return

        widget = VideoInfo(fullpath, title, thumbnail)
        widget.button.hide()
        widget.mouseReleaseSignal.connect(self.requestStream)
        videoListLayout.insertWidget(0, widget)

    @pyqtSlot(str)
    def deleteVideoInfo(self, fullpath):
        videoListLayout = self.page3.videoPanel.listLayout
        for i in range(videoListLayout.count()):
            widget = videoListLayout.itemAt(i).widget()
            if widget is not None and widget.fullpath == fullpath:
                widget.deleteLater()


subprocess.run('cls', shell=True)
Utility.debug = False

app = QApplication(sys.argv)
app.setStyleSheet('QToolTip {background-color: black; color: white; border: black solid 1px;}')
window = MyWindow()
window.show()
app.exec()
