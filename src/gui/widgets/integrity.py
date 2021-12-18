from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QPointF, QRect, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QTextOption, QTransform
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from multipledispatch import *

# https://doc.qt.io/qt-5/qopenglwidget.html
# https://doc.qt.io/qt-5/coordsys.html


class Integrity(QOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.metadata = None
        self.videoFrames = None
        self.audioFrames = None
        self.videoFrameIndex = None
        self.audioFrameIndex = None

        self.painter = QPainter(self)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.painter.setFont(QFont('Consolas', 12))
        self.squareSide = 6

    def initializeGL(self):
        glClearColor(0.058, 0.058, 0.058, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_LINE_SMOOTH)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        if not (self.metadata and self.videoFrames and self.videoFrameIndex and self.audioFrames and self.audioFrameIndex):
            return

        self.painter.begin(self)

        self.drawIntegrity(self.videoFrames, self.videoFrameIndex, self.metadata['videoFPS'], 0)
        self.drawIntegrity(self.audioFrames, self.audioFrameIndex, self.metadata['audioFPS'] / self.metadata['audioChunkSize'], (self.metadata['videoFPS'] + 2) * (self.squareSide + 1))

        self.painter.end()

    def drawIntegrity(self, buffer, index, fps, offset):
        for key in buffer:
            # if key < index:
            #     continue
            frame = buffer[key]

            i = int(key % fps)
            j = int(key / fps)

            if frame['totalBytes'] == 0:
                color = QColor('#d72337')
            else:
                g = int(frame['loadedBytes'] / frame['totalBytes']) * 255
                color = QColor.fromRgb(0, g, 0)

            self.painter.setPen(QPen(color, self.squareSide))
            self.painter.drawPoint((j + 1) * (self.squareSide + 1), (i + 1) * (self.squareSide + 1) + offset)

        self.painter.setPen(QPen(QColor('#286ed2'), self.squareSide))
        i = int(index % fps)
        j = int(index / fps)
        self.painter.drawPoint((j + 1) * (self.squareSide + 1), (i + 1) * (self.squareSide + 1) + offset)

    @pyqtSlot(object, object, object, int, int)
    def refresh(self, metadata, videoFrames, audioFrames, videoFrameIndex, audioFrameIndex):

        self.metadata = dict(metadata)
        self.videoFrames = dict(videoFrames)
        self.audioFrames = dict(audioFrames)
        self.videoFrameIndex = videoFrameIndex
        self.audioFrameIndex = audioFrameIndex

        videoN = self.metadata['videoFPS']
        videoM = int(self.metadata['videoFrameCount'] / self.metadata['videoFPS']) + 1

        audioN = int(self.metadata['audioFPS'] / self.metadata['audioChunkSize'])
        audioM = int(self.metadata['audioFrameCount'] / self.metadata['audioFPS']) + 1

        self.parent().resize((max(videoM, audioM) + 5) * (self.squareSide + 1), (videoN + audioN + 5) * (self.squareSide + 1))
        self.update()
