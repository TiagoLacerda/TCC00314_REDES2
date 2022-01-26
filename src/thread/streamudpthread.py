import socket
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QByteArray, QBuffer, QIODevice
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap

from utility import Utility
from thread.mediasendthread import MediaSendThread
from requests import get as getPublicIP

import sys

class StreamUDPThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self, udpTarget, udpSocket, bufferSize):
        super().__init__()
        self.udpTarget = udpTarget
        self.udpSocket = udpSocket
        self.bufferSize = bufferSize

        self.closing = False

        self.workers = {}    # address: {fullpath: str, thread: MediaSendThread}
        self.videoList = []  # (fullpath: '', title: '',    thumbnail: QPixmap)

    def run(self):
        self.setPriority(QThread.Priority.HighPriority)

        ip = getPublicIP('https://api.ipify.org').text
        self.log('UDP Server up and listening at ({}:{})'.format(ip, self.udpTarget[1]))

        while not self.closing:
            try:
                messages, address = Utility.recvUDPMessages(self.udpSocket, self.bufferSize)
                command = messages[0].decode()

                if command == 'videoinfolist':
                    self.log('{} says ["{}"]'.format(address, command))

                    for item in self.videoList:
                        # https://stackoverflow.com/questions/57404778/how-to-convert-a-qpixmaps-image-into-a-bytes
                        qByteArray = QByteArray()
                        qBuffer = QBuffer(qByteArray)
                        qBuffer.open(QIODevice.WriteOnly)
                        item['thumbnail'].save(qBuffer, 'JPG')
                        thumbnail = qByteArray.data()

                        data = ['videoinfo'.encode(), item['fullpath'].encode(), item['title'].encode(), thumbnail]
                        Utility.sendUDPMessages(self.udpSocket, address, data)
                    continue

                if command == 'stream':  # ['stream', username, fullpath, width, height]
                    username = messages[1].decode()
                    fullpath = messages[2].decode()
                    w = int(messages[3].decode())
                    h = int(messages[4].decode())

                    self.log('{} says ["{}", "{}", "{}", "{}", "{}"]'.format(address, command, username, fullpath, w, h))

                    # TODO: If user is premium, start mediasendthread, else, send denial message

                    if address in self.workers:
                        self.workers[address]['thread'].close()
                        del self.workers[address]

                    thread = MediaSendThread(address, self.udpSocket, self.bufferSize, w, h, fullpath)
                    thread.logger.connect(self.log)
                    thread.start()
                    self.workers[address] = {'fullpath': fullpath, 'thread': thread}
                    continue

                if command == 'cancel':
                    self.log('{} says ["{}"]'.format(address, command))
                    
                    if address in self.workers:
                        self.workers[address]['thread'].close()
                        del self.workers[address]
                    continue

            except socket.timeout as e:
                continue
            except Exception as e:
                # self.log('{}: {} {}'.format(self, e, command))
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                self.log('Exception thrown: File({}) Line({})'.format(filename, line_number))
                if address in self.workers:
                    self.workers[address]['thread'].close()
                    del self.workers[address]



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

        for address in self.workers:
            if self.workers[address]['fullpath'] == fullpath:
                self.workers[address]['thread'].close()
                del self.workers[address]
