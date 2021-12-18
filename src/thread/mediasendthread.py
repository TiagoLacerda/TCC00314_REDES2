from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


import cv2
from utility import Utility
from itertools import chain

import os
import subprocess
import wave


class MediaSendThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self, udpTarget, udpSocket, bufferSize, targetW, targetH, videopath):
        super().__init__()

        self.udpTarget = udpTarget
        self.udpSocket = udpSocket
        self.bufferSize = bufferSize
        self.targetW = targetW
        self.targetH = targetH
        self.audioChunkSize = 1024
        self.videopath = videopath

        self.closing = False

    # Create a corresponding .wav audio file if one does not exist in assets/videos
    # Build metadata from audio and video files
    #   { audioFPS, audioFrameCount, audioFrameWidth, audioChannelCount, videoWidth, videoHeight, videoFPS, videoFrameCount }
    #
    def run(self):
        self.setPriority(QThread.Priority.HighPriority)
        self.log('MediaSendThread(updTarget=\'{}\', bufferSize=\'{}\', targetW=\'{}\', targetH=\'{}\', audioFramesPerFrame=\'{}\', videopath=\'{}\')'.format(
            self.udpTarget, self.bufferSize, self.targetW, self.targetH, self.audioChunkSize, self.videopath))

        try:
            # Create audio file if one does not exist

            self.videopath = os.path.normpath(self.videopath)
            path = os.path.split(self.videopath)  # [directory, name + extension]
            file = os.path.splitext(path[1])      # [name, extension]
            audiopath = os.path.join(path[0], file[0]) + '.wav'

            if not os.path.isfile(audiopath):
                command = 'ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}'.format(self.videopath, audiopath)
                print(command)
                subprocess.call(command, shell=True)

            # Collect Audio & Video Metadata

            wavefile = wave.open(audiopath, 'rb')
            capture = cv2.VideoCapture(self.videopath)

            metadata = {
                'audioFPS':          wavefile.getframerate(),
                'audioFrameCount':   wavefile.getnframes() / self.audioChunkSize,
                'audioSampleWidth':  wavefile.getsampwidth(),
                'audioChannelCount': wavefile.getnchannels(),
                'audioChunkSize':    self.audioChunkSize,
                'videoTargetWidth':  self.targetW,  # capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                'videoTargetHeight': self.targetH,  # capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                'videoFPS':          capture.get(cv2.CAP_PROP_FPS),
                'videoFrameCount':   capture.get(cv2.CAP_PROP_FRAME_COUNT)
            }

            print(metadata)
            msgs = list(chain(['stream'.encode(), 'metadata'.encode()], [int(item).to_bytes(8, 'big') for item in metadata.values()]))
            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, msgs)

            # Main Loop

            then = datetime.now()
            dt = 0.0
            elapsed = 0.0

            videoFrameIndex = 0
            audioFrameIndex = 0
            isProcessing = True

            while not self.closing and isProcessing:
                now = datetime.now()
                dt = (now - then).total_seconds()
                then = now

                elapsed += dt

                isProcessing = False
                read = True

                videoPercentage = videoFrameIndex / metadata['videoFrameCount']
                audioPercentage = audioFrameIndex / metadata['audioFrameCount']

                if elapsed >= 1.0:
                    elapsed = 0.0
                    self.log('Video: {:.2f}% Audio: {:.2f}%'.format(100.0 * videoPercentage, 100.0 * audioPercentage))

                if videoPercentage <= audioPercentage:
                    read, array = capture.read()
                    if read:
                        isProcessing = True
                        videobytes = cv2.imencode('.jpg', cv2.resize(array, (self.targetW, self.targetH)))[1].tobytes()

                        command = 'videodata'.encode()
                        chunks = Utility.fragment(videobytes, self.bufferSize - len(command) - 3 * 4 - 5 * 2)  # See Utility.chainByteMessages

                        frameIndex = videoFrameIndex.to_bytes(4, 'big')
                        totalBytes = len(videobytes).to_bytes(4, 'big')
                        for i in range(len(chunks)):
                            chunkIndex = i.to_bytes(4, 'big')
                            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [command, frameIndex, chunkIndex, totalBytes, chunks[i]])
                        videoFrameIndex += 1

                if audioPercentage <= videoPercentage:
                    audiobytes = wavefile.readframes(self.audioChunkSize)
                    if audiobytes != b'':
                        isProcessing = True

                        command = 'audiodata'.encode()
                        chunks = Utility.fragment(audiobytes, self.bufferSize - len(command) - 3 * 4 - 5 * 2)  # See Utility.chainByteMessages

                        frameIndex = audioFrameIndex.to_bytes(4, 'big')
                        totalBytes = len(audiobytes).to_bytes(4, 'big')
                        for i in range(len(chunks)):
                            chunkIndex = i.to_bytes(4, 'big')
                            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [command, frameIndex, chunkIndex, totalBytes, chunks[i]])
                        audioFrameIndex += 1

        except Exception as e:
            self.log('{}: {}'.format(self, e))
            self.close()

        self.log('Closing MediaSendThread...')

    def log(self, message):
        self.logger.emit(message)

    def close(self):
        self.closing = True
