import socket
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap

from utility import Utility
from thread.mediasendthread import MediaSendThread
from requests import get as getPublicIP


class StreamUDPThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self, udpTarget, udpSocket, bufferSize):
        super().__init__()
        self.udpTarget = udpTarget
        self.udpSocket = udpSocket
        self.bufferSize = bufferSize

        self.closing = False

        self.workers = []    # {fullpath: '', address: '', thread: MediaSendThread}
        self.videoList = []  # (fullpath: '', title: '',    thumbnail: QPixmap)

    def run(self):
        self.setPriority(QThread.Priority.HighPriority)

        ip = getPublicIP('https://api.ipify.org').text
        self.log('UDP Server up and listening at ({}:{})'.format(ip, self.udpTarget[1]))

        while not self.closing:
            try:
                messages, address = Utility.recvUDPMessages(self.udpSocket, self.bufferSize)
                self.log('{} says {}'.format(address, messages))

                command = messages[0].decode()

                if command == 'ping':
                    Utility.sendUDPMessages(self.udpSocket, address, ['pong'], True)
                    continue

                if command == 'videoinfolist':
                    for item in self.videoList:
                        data = ['videoinfo'.encode(), item['fullpath'].encode(), item['title'].encode(), 'thumbnail'.encode()]
                        Utility.sendUDPMessages(self.udpSocket, address, data)
                    continue

                if command == 'stream':  # ['stream', username, fullpath, width, height]
                    username = messages[1].decode()
                    fullpath = messages[2].decode()
                    w = int(messages[3].decode())
                    h = int(messages[4].decode())

                    # TODO: If user is premium, start mediasendthread, else, send denial message

                    for thread in self.workers:
                        if thread['address'] == address:
                            thread['thread'].close()

                    thread = MediaSendThread(address, self.udpSocket, self.bufferSize, w, h, fullpath)
                    thread.logger.connect(self.log)
                    thread.start()
                    self.workers.append({'fullpath': fullpath, 'address': address, 'thread': thread})
                    continue

                if command == 'cancel':
                    for thread in self.workers:
                        if thread['address'] == address:
                            thread['thread'].close()
                    continue

            except socket.timeout as e:
                continue
            except Exception as e:
                self.log('{}: {}'.format(self, e))

    @pyqtSlot(str)
    def log(self, message):
        self.logger.emit(message)

    def close(self):
        self.closing = True

    @pyqtSlot(str, str, QPixmap)
    def insertVideoInfo(self, fullpath, title, thumbnail):
        for item in self.videoList:
            if item['fullpath'] == fullpath:
                return

        self.videoList.append({'fullpath': fullpath, 'title': title, 'thumbnail': thumbnail})

    @pyqtSlot(str)
    def deleteVideoInfo(self, fullpath):
        for item in self.videoList:
            if item['fullpath'] == fullpath:
                self.videoList.remove(item)

        for item in self.workers:
            if item['fullpath'] == fullpath:
                item['thread'].close()
                self.workers.remove(item)
