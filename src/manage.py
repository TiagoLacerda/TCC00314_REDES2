import sys
from PyQt5 import QtWidgets
import cv2
import subprocess
import socket

import os
import threading
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import subprocess
import socket
import sys
import os

from gui.screens.manage_window import Window
from datetime import datetime
from database import Database
from utility import Utility


class TCPConnectionThread(QThread):
    logger = pyqtSignal(str)
    closeSignal = pyqtSignal(str, int)

    def __init__(self, connection: socket, address):
        super().__init__()
        self.connection = connection
        self.address = address
        self.closing = False

        self.username = None  # If someone successfully logs in, save their username (stream.py might ask for their address)

    def run(self):
        try:
            while not self.closing:
                message = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')
                self.log('{} says: {}'.format(self.address, message))

                if message == 'login':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')
                    password = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8')

                    dblocker.lock()

                    if(username == '' or password == ''):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Credenciais inválidas'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    member = db.selectUser(username)

                    if member is None:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário não registrado'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    if member.password != password:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Senha incorreta'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    Utility.sendTCPMessage(self.connection, envoyLength, 'allow'.encode('utf-8'))
                    Utility.sendTCPMessage(self.connection, envoyLength, str(member.premium).encode('utf-8'))
                    self.username = member.username
                    dblocker.unlock()
                    continue

                if message == 'register':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    password = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    premium = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()  # Premium code: if this says "premium", user will be premium

                    dblocker.lock()

                    if(username == '' or password == '' or ':' in username or ':' in password):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Credenciais inválidas'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    member = db.selectUser(username)

                    if member is not None:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário já registrado'.encode('utf-8'))
                        dblocker.unlock()
                        continue

                    isPremium = True if premium == 'premium' else False
                    db.insertUser(username, password, isPremium)

                    Utility.sendTCPMessage(self.connection, envoyLength, 'allow'.encode('utf-8'))
                    dblocker.unlock()
                    continue

                if message == 'disconnect':
                    self.close()

                #

                if message == 'isMember':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    if db.isMember(username):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'True'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'False'.encode('utf-8'))
                    dblocker.unlock()
                    continue

                if message == 'isAdmin':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    if db.isAdmin(username):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'True'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'False'.encode('utf-8'))
                    dblocker.unlock()
                    continue

                if message == 'isMemberOrAdmin':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    if db.isMemberOrAdmin(username):
                        Utility.sendTCPMessage(self.connection, envoyLength, 'True'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'False'.encode('utf-8'))
                    dblocker.unlock()
                    continue

                if message == 'insert_room':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    room = db.insertRoom(username)

                    if room:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'True'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'False'.encode('utf-8'))

                    dblocker.unlock()
                    continue

                if message == 'delete_room':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    room = db.selectRoom(username)

                    if room:
                        db.deleteRoom(username)
                        Utility.sendTCPMessage(self.connection, envoyLength, 'True'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'False'.encode('utf-8'))

                    dblocker.unlock()
                    continue

                if message == 'insert_member':
                    logged_username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    member_username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    logged = db.selectUser(logged_username)

                    if logged:
                        member = db.selectUser(member_username)
                        if member:
                            if db.isAdmin(logged.username):
                                if not db.isMemberOrAdmin(member.username):
                                    result = db.insertMember(logged.username, member.username)
                                    if result:
                                        Utility.sendTCPMessage(self.connection, envoyLength, 'Membro inserido com sucesso'.encode('utf-8'))
                                    else:
                                        Utility.sendTCPMessage(self.connection, envoyLength, 'Ocorreu um erro ao inserir um membro'.encode('utf-8'))
                                else:
                                    Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário já pertence a um grupo'.encode('utf-8'))
                            else:
                                Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário não administra nenhum grupo'.encode('utf-8'))
                        else:
                            Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário membro não registrado'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário administrador não registrado'.encode('utf-8'))

                    dblocker.unlock()
                    continue

                if message == 'delete_member':
                    # Inverted roles if member tries to leave
                    logged_username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    member_username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()

                    dblocker.lock()
                    logged = db.selectUser(logged_username)

                    if logged:
                        member = db.selectUser(member_username)
                        if member:
                            if db.isAdmin(logged.username):
                                if db.isMemberOrAdmin(member.username):
                                    result = db.deleteMember(logged.username, member.username)
                                    if result:
                                        Utility.sendTCPMessage(self.connection, envoyLength, 'Membro removido com sucesso'.encode('utf-8'))
                                    else:
                                        Utility.sendTCPMessage(self.connection, envoyLength, 'Ocorreu um erro ao remover um membro'.encode('utf-8'))
                                else:
                                    Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário não pertence a nenhum grupo'.encode('utf-8'))
                            else:
                                Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário não administra nenhum grupo'.encode('utf-8'))
                        else:
                            Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário membro não registrado'.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, 'Usuário administrador não registrado'.encode('utf-8'))

                    dblocker.unlock()
                    continue

                if message == 'select_admin_by_member_or_admin':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    self.log('{} says:  {}'.format(self.address, username))

                    dblocker.lock()
                    admin = db.selectAdminByMemberOrAdmin(username)
                    if admin:
                        Utility.sendTCPMessage(self.connection, envoyLength, admin.username.encode('utf-8'))
                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, ''.encode('utf-8'))

                    dblocker.unlock()
                    continue

                if message == 'select_members':
                    username = Utility.recvTCPMessage(self.connection, envoyLength).decode('utf-8').strip()
                    self.log('{} says:  {}'.format(self.address, username))

                    dblocker.lock()
                    room = db.selectRoom(username)

                    addresses = tcpThread.getAllAddresses()

                    if room:
                        Utility.sendTCPMessage(self.connection, envoyLength, '{}'.format(1 + len(room.members)).encode('utf-8'))
                        Utility.sendTCPMessage(self.connection, envoyLength, room.admin.username.encode('utf-8'))
                        for member in room.members:
                            Utility.sendTCPMessage(self.connection, envoyLength, member.username.encode('utf-8'))
                            if member.username in addresses:
                                Utility.sendTCPMessage(self.connection, envoyLength, '{}'.format(addresses[member.username]).encode('utf-8'))
                            else:
                                Utility.sendTCPMessage(self.connection, envoyLength, ''.encode('utf-8'))

                    else:
                        Utility.sendTCPMessage(self.connection, envoyLength, '{}'.format(0).encode('utf-8'))

                    dblocker.unlock()
                    continue

        except Exception as e:
            self.log(str(e) + ' {}'.format(self.address))
        finally:
            self.connection.close()
            self.closeSignal.emit(self.address[0], self.address[1])

    def log(self, message):
        self.logger.emit(message)

    def close(self):
        self.closing = True


class TCPThread(QThread):
    logger = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.target = None
        self.socket = None
        self.workers = {}  #

    def run(self):
        self.target = ('localhost', 6060)
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.bind(self.target)

        self.log('Management Server open at {}'.format(self.target))

        self.socket.listen(5)

        while True:
            connection, address = self.socket.accept()
            if address in self.workers:
                self.log('Connecion already exists with {}'.format(address))
            else:
                self.log('Established connection with {}'.format(address))

                thread = TCPConnectionThread(connection, address)
                thread.logger.connect(self.log)
                thread.closeSignal.connect(self.closeWorker)
                thread.start()
                self.workers[address] = thread

    @pyqtSlot(str)
    def log(self, message):
        self.logger.emit(message)

    @pyqtSlot(str, int)
    def closeWorker(self, addr, port):
        address = (addr, port)
        if address in self.workers:
            self.workers[address].close()
            del self.workers[address]

    def getAllAddresses(self):
        addresses = {}
        for address in tcpThread.workers:
            worker = tcpThread.workers[address]
            addresses[worker.username] = address
        return addresses


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        self.navbar.buttons[0].clicked.connect(lambda: self.plaintextedit.clear())
        self.navbar.buttons[1].clicked.connect(qApp.quit)

        global db, dblocker, envoyLength, tcpThread
        db = Database()
        dblocker = QMutex()
        envoyLength = 4

        db.insertUser('admin', '1234', True)
        db.insertUser('tiago', '1234', False)

        tcpThread = TCPThread()
        tcpThread.logger.connect(self.log)
        tcpThread.start()
        self.tcpThread = tcpThread

    @pyqtSlot(str)
    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        message = '[{}]: {}'.format(now, message)
        print(message)
        self.plaintextedit.appendPlainText(message)


subprocess.run('cls', shell=True)
Utility.debug = False

app = QApplication(sys.argv)
gui = MyWindow()
gui.show()
app.exec()
