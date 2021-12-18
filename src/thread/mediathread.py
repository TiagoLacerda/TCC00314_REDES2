from subprocess import call
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog, QMainWindow, qApp
from collections import namedtuple
from datetime import datetime

import numpy as np
import pyaudio
import wave

import cv2
from gui.screens.integritydialog import IntegrityDialog

from utility import Utility


class MediaThread(QThread):
    logger = pyqtSignal(str)
    updateFrameSignal = pyqtSignal(QPixmap)
    integritySignal = pyqtSignal(object, object, object, int, int)

    def __init__(self, metadata, videoFrames, audioFrames):
        super().__init__()
        print('MediaThread(metadata={})'.format(metadata))

        self.metadata = metadata

        self.videoFrames = videoFrames
        self.audioFrames = audioFrames

        self.closing = False

    def run(self):
        try:
            then = datetime.now()
            dt = 0.0

            elapsed = 0.0
            debugElapsed = 0.0
            videoElapsed = 0.0
            audioElapsed = 0.0

            videoFrameIndex = 0
            audioFrameIndex = 0

            lostVideoFrames = 0
            lostAudioFrames = 0

            videoFrametime = 1.0 / self.metadata['videoFPS']
            audioFrametime = 1.0 / self.metadata['audioFPS'] * self.metadata['audioChunkSize']

            buffering = False
            videoDone = False
            audioDone = False

            # Get debug dialog
            gui = None
            for widget in qApp.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    gui = widget
                    break

            dialog = gui.integrityDialog
            self.integritySignal.connect(dialog.integrity.refresh)

            self.pa = pyaudio.PyAudio()
            self.audioStream = self.pa.open(
                format=self.pa.get_format_from_width(self.metadata['audioSampleWidth']),
                channels=self.metadata['audioChannelCount'],
                rate=self.metadata['audioFPS'],
                output=True)

            while not self.closing and not videoDone and not audioDone:
                now = datetime.now()
                dt = (now - then).total_seconds()
                then = now

                # debugElapsed += dt

                # if debugElapsed >= 1.0:
                #     debugElapsed = 0.0
                #     self.integritySignal.emit(self.metadata, self.videoFrames, self.audioFrames, videoFrameIndex, audioFrameIndex)

                if lostVideoFrames > self.metadata['videoFPS']:
                    self.log('Buffering...')
                    lostAudioFrames = 0
                    lostVideoFrames = 0
                    buffering = True
                    elapsed = 0.0

                if buffering:
                    elapsed += dt
                    if(elapsed >= 3.0):
                        self.log('Resuming...')
                        elapsed = 0.0
                        buffering = False
                    continue

                videoElapsed += dt
                audioElapsed += dt

                if videoFrameIndex < self.metadata['videoFrameCount']:
                    if videoElapsed >= videoFrametime:
                        elapsedFrames = int(videoElapsed / videoFrametime)
                        videoElapsed = videoElapsed % videoFrametime
                        frame = self.videoFrames[videoFrameIndex + elapsedFrames - 1]

                        if frame['loadedBytes'] == frame['totalBytes'] and frame['totalBytes'] != 0:
                            videoBytes = b''.join([chunk[1] for chunk in frame['chunks']])
                            img = cv2.imdecode(np.frombuffer(videoBytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                            frame = QPixmap.fromImage(QImage(img, self.metadata['videoTargetWidth'], self.metadata['videoTargetHeight'], self.metadata['videoTargetWidth'] * 3, QImage.Format_BGR888))
                            self.updateFrameSignal.emit(frame)
                            lostVideoFrames = max(lostVideoFrames - elapsedFrames, 0)
                        else:
                            lostVideoFrames += elapsedFrames
                        videoFrameIndex += elapsedFrames
                else:
                    videoDone = True

                if audioFrameIndex < self.metadata['audioFrameCount']:
                    if audioElapsed >= audioFrametime:
                        elapsedFrames = int(audioElapsed / audioFrametime)
                        audioElapsed = audioElapsed % audioFrametime
                        frame = self.audioFrames[audioFrameIndex + elapsedFrames - 1]

                        if frame['loadedBytes'] == frame['totalBytes'] and frame['totalBytes'] != 0:
                            audioBytes = b''.join([chunk[1] for chunk in frame['chunks']])
                            self.audioStream.write(audioBytes)
                            lostAudioFrames = max(lostAudioFrames - elapsedFrames, 0)
                        else:
                            lostAudioFrames += elapsedFrames
                        audioFrameIndex += elapsedFrames
                else:
                    audioDone = True

            # After all has been played
            self.integritySignal.emit(self.metadata, self.videoFrames, self.audioFrames, videoFrameIndex, audioFrameIndex)

        except Exception as e:
            raise e
            self.log('{}: {}'.format(self, e))
            self.close()

        self.log('Closing MediaThread...')

    @pyqtSlot(str)
    def log(self, message):
        self.logger.emit(message)

    def close(self):
        self.closing = True
