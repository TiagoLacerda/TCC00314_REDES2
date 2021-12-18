from PyQt5.QtCore import QMutex, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

import subprocess
import socket
import sys
import os

from gui.manage_window import Window

from database import Database
from utility import Utility

from datetime import datetime


class TCPConnectionThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self, connection: socket, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        try:
            while True:
                message = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')
                self.log(message)

                if message == 'ping':
                    Utility.sendTCPMessage(self.connection, envoyLength, 'pong'.encode('utf-8'))
                    continue

                if message == 'login':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')
                    password = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')

                    dblocker.lock()

                    if(username == '' or password == ''):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'invalid credentials'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    user = db.selectUser(username)

                    if user is None:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'username not registered'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    if user.password != password:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'incorrect password'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    Utility.sendTCPMessage(self.connection, envoyLength, 'allow'.encode('utf-8'))
                    Utility.sendTCPMessage(self.connection, envoyLength, str(user.premium).encode('utf-8'))
                    dblocker.unlock()
                    continue

                if message == 'register':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    password = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    premium = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()

                    if(username == '' or password == '' or ':' in username or ':' in password):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'invalid credentials'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    user = db.selectUser(username)

                    if user is not None:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'username already registered'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    isPremium = True if premium == 'premium' else False
                    db.insertUser(username, password, isPremium)

                    Utility.sendTCPMessage(self.connection, envoyLength, 'successfully registered'.encode('utf-8'))
                    Utility.sendTCPMessage(self.connection, envoyLength, str(isPremium).encode('utf-8'))
                    dblocker.unlock()
                    continue

        except Exception as e:
            self.log(str(e))
        finally:
            self.connection.close()

    def log(self, message):
        self.logger.emit(message)


class TCPThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.target = None
        self.socket = None

    def run(self):
        self.target = ('localhost', 6060)
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.bind(self.target)

        self.log('Management Server open at {}'.format(self.target))

        self.socket.listen(5)

        while True:
            connection, address = self.socket.accept()

            self.log('Established connection with {}'.format(address))

            thread = TCPConnectionThread(connection, address)
            thread.logger = self.logger
            thread.start()

    @pyqtSlot(str)
    def log(self, message):
        self.logger.emit(message)


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        global db, dblocker, envoyLength
        db = Database()
        dblocker = QMutex()
        envoyLength = 4

        self.tcpThread = TCPThread()
        self.tcpThread.logger.connect(self.log)
        self.tcpThread.start()

    @pyqtSlot(str)
    def log(self, message):
        now = datetime.now().strftime("%d\\%m\\%Y %H:%M:%S")
        message = '[{}]: {}'.format(now, message)
        print(message)
        self.plaintextedit.appendPlainText(message)
        Utility.log('Manager: ' + message)


subprocess.run('cls', shell=True)
Utility.debug = True

app = QApplication(sys.argv)
gui = MyWindow()
gui.show()
app.exec()
