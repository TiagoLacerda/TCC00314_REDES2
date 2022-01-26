from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QByteArray, QBuffer, QIODevice
from PyQt5.QtWidgets import QApplication, QWidget, qApp
from PyQt5.QtGui import QPixmap
from datetime import datetime


import sys
import socket
import subprocess
from gui.widgets.videoinfo import VideoInfo

from utility import Utility

from gui.screens.client_window import Window
from thread.mediathread import MediaThread
from database import User
from collections import namedtuple


class ClientUDPThread(QThread):
    logger = pyqtSignal(str)
    updateVideoFrameSignal = pyqtSignal(QPixmap)

    insertVideoInfoSignal = pyqtSignal(str, str, QPixmap)

    def __init__(self, udpTarget: tuple, udpSocket: socket, bufferSize: int):
        super().__init__()
        print('ClientUDPThread(udpTarget={}, bufferSize={})'.format(udpTarget, bufferSize))

        self.udpTarget = udpTarget
        self.udpSocket = udpSocket
        self.bufferSize = bufferSize
        self.closing = False

        self.mediaThread = None

        self.videoFrames = {}
        self.audioFrames = {}

    def run(self):
        self.setPriority(QThread.Priority.HighPriority)

        while not self.closing:
            try:
                messages, address = Utility.recvUDPMessages(self.udpSocket, self.bufferSize)
                command = messages[0].decode()

                if command == 'videodata' or command == 'audiodata':
                    # self.log('{} says ["{}", ...]'.format(address, command))

                    frameIndex = int.from_bytes(messages[1], 'big')
                    chunkIndex = int.from_bytes(messages[2], 'big')
                    totalBytes = int.from_bytes(messages[3], 'big')
                    try:
                        if command == 'videodata':
                            self.videoFrames[frameIndex]['loadedBytes'] += len(messages[4])
                            self.videoFrames[frameIndex]['totalBytes'] = totalBytes
                            self.videoFrames[frameIndex]['chunks'].append((chunkIndex, messages[4]))
                        else:
                            self.audioFrames[frameIndex]['loadedBytes'] += len(messages[4])
                            self.audioFrames[frameIndex]['totalBytes'] = totalBytes
                            self.audioFrames[frameIndex]['chunks'].append((chunkIndex, messages[4]))
                    except Exception as e:
                        print(str(e))
                    continue

                if command == 'videoinfo':  # VideoInfo for building videolist
                    self.log('{} says ["{}", ..., "{}", ...]'.format(address, command, messages[2].decode()))

                    # https://stackoverflow.com/questions/57404778/how-to-convert-a-qpixmaps-image-into-a-bytes
                    qByteArray = QByteArray(messages[3])
                    pixmap = QPixmap()
                    pixmap.loadFromData(qByteArray, 'JPG')

                    self.insertVideoInfoSignal.emit(messages[1].decode(), messages[2].decode(), pixmap)
                    continue

                if command == 'stream':     # Request stream response
                    self.log('{} says ["{}", ...]'.format(address, command))

                    if messages[1].decode() != 'metadata':
                        continue

                    metadata_raw = [int.from_bytes(b, 'big') for b in messages[2:]]
                    metadata = {
                        'audioFPS':          metadata_raw[0],
                        'audioFrameCount':   metadata_raw[1],
                        'audioChannelCount': metadata_raw[2],
                        'audioSampleWidth':  metadata_raw[3],
                        'audioChunkSize':    metadata_raw[4],
                        'videoTargetWidth':  metadata_raw[5],
                        'videoTargetHeight': metadata_raw[6],
                        'videoFPS':          metadata_raw[7],
                        'videoFrameCount':   metadata_raw[8]
                    }

                    self.videoFrames = {}
                    self.audioFrames = {}

                    for i in range(metadata['videoFrameCount']):
                        self.videoFrames[i] = {'loadedBytes': 0, 'totalBytes': 0, 'chunks': []}

                    for i in range(metadata['audioFrameCount']):
                        self.audioFrames[i] = {'loadedBytes': 0, 'totalBytes': 0, 'chunks': []}

                    self.mediaThread = MediaThread(metadata, self.videoFrames, self.audioFrames)
                    self.mediaThread.logger.connect(self.log)
                    self.mediaThread.updateFrameSignal.connect(self.updateVideoFrame)
                    self.mediaThread.start()
                    continue

            except socket.timeout as e:
                continue
            except Exception as e:
                self.log(str(e))

    def close(self):
        self.closing = True

    @pyqtSlot(str)
    def log(self, message):
        self.logger.emit(message)

    @pyqtSlot(QPixmap)
    def updateVideoFrame(self, pixmap):
        self.updateVideoFrameSignal.emit(pixmap)

    @pyqtSlot()
    def closeMediaThread(self):
        if self.mediaThread is not None:
            self.mediaThread.close()
