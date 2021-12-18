import cv2
from PyQt5.QtGui import *
from datetime import datetime
import socket

from PyQt5.QtCore import Qt


class Utility():
    debug = False

    def convertCvToQt(cv_img, dst_w, dst_h):
        # Convert from an opencv image to QPixmap
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        src_h, src_w, ch = rgb_image.shape
        bytesPerLine = ch * src_w
        qimage = QImage(rgb_image.data, src_w, src_h, bytesPerLine, QImage.Format_RGB888)
        p = qimage.scaled(dst_w, dst_h, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        return QPixmap.fromImage(p)

    def getThumbnail(fullpath, w, h):
        capture = cv2.VideoCapture(fullpath)
        frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        framerate = int(capture.get(cv2.CAP_PROP_FPS))

        index = min(frames, framerate * 5)
        capture.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, cv_img = capture.read()
        if(ret):
            return Utility.convertCvToQt(cv_img, w, h)

    def fragment(bytes: bytes, stride: int):
        chunks = []
        total = len(bytes)
        l = 0
        while l != total:
            r = l + min(stride, total - l)
            chunk = bytes[l:r]
            chunks.append(chunk)
            l += len(chunk)
        return chunks

    # Flattens a list of bytes objects with sections in between indicating where a next bytes object's corresponding data begins

    def chainByteMessages(messages: list, stride=2):
        chunks = []
        p = 0
        for i in range(len(messages)):
            w = p + stride + len(messages[i])
            chunks.append(w.to_bytes(stride, 'big'))
            chunks.append(messages[i])
            p = w
        return b''.join(chunks)

    # Undoes what chainByteMessages does

    def breakByteMessages(bytes: bytes, stride=2):
        if stride > len(bytes):
            raise Exception('Message is shorter than stride ({})! Message (len={}): {}'.format(stride, len(bytes), bytes))

        messages = []
        l = 0
        while l < len(bytes):
            r = l + stride
            w = int.from_bytes(bytes[l:r], 'big')
            messages.append(bytes[r:w])
            l = w
        return messages

    # Sends all bytes of <message>

    def sendall(socket: socket, message: bytes):
        if Utility.debug:
            print('utility.sendall(message={})'.format(message))

        total = 0
        while total < len(message):
            sent = socket.send(message[total:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            total += sent

    # Sends a message of <length> bytes containing <content> which is the length in bytes of another message to come, encoded using <encoding>

    def sendenvoy(socket: socket, length: int, content: int, encoding='utf-8'):
        if Utility.debug:
            print('utility.sendenvoy(length={}, content={}, encoding={})'.format(length, content, encoding))

        message = str(content).encode(encoding)
        if length < len(message):
            raise Exception('Content does not fit in Envoy!')
        message = b' ' * (length - len(message)) + message
        Utility.sendall(socket, message)

    # Receives a message of <length> bytes

    def recvall(socket: socket, length: int):
        if Utility.debug:
            print('utility.recvall(length={})'.format(length))

        chunks = []
        total = 0
        while total < length:
            chunk = socket.recv(min(length - total, length))
            if chunk is None or chunk == b'':
                raise RuntimeError('socket connection broken')
            chunks.append(chunk)
            total += len(chunk)
        return b''.join(chunks)

    # Receives a message containing the length in bytes of another message to come

    def recvenvoy(socket: socket, length: int, encoding='utf-8'):
        if Utility.debug:
            print('utility.recvenvoy(length={}, encoding={})'.format(length, encoding))

        return int((Utility.recvall(socket, length)).decode(encoding))

    # Sends a message, both parties must agree on envoy length and encoding

    def sendTCPMessage(socket: socket, envoy: int,  content: bytes, encoding='utf-8'):
        if Utility.debug:
            print('utility.sendMessage(content={}, envoy={}, encoding={})'.format(content, envoy, encoding))

        Utility.sendenvoy(socket, envoy, len(content), encoding)
        Utility.sendall(socket, content)

    # Receives a message, both parties must agree on envoy length and encoding

    def recvTCPMessage(socket: socket, envoy: int, encoding='utf-8'):
        if Utility.debug:
            print('utility.recvMessage(envoy={}, encoding={})'.format(envoy, encoding))

        length = Utility.recvenvoy(socket, envoy, encoding)
        return Utility.recvall(socket, length)

    def sendUDPMessages(socket: socket, target: tuple, messages: list, encode=False):
        if encode:
            for i in range(len(messages)):
                messages[i] = messages[i].encode()

        bytes = Utility.chainByteMessages(messages)
        socket.sendto(bytes, target)

    def recvUDPMessages(socket: socket, bufferSize: int, decode=False):
        bytes, address = socket.recvfrom(bufferSize)
        messages = Utility.breakByteMessages(bytes)
        if decode:
            for i in range(len(messages)):
                messages[i] = messages[i].decode()
        return messages, address
