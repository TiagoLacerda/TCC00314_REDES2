from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, qApp
from PyQt5.QtGui import QPixmap
from datetime import datetime

import sys
import socket
import subprocess
from gui.widgets.inputdialog import InputDialog
from gui.widgets.streamtypedialog import StreamTypeDialog
from gui.widgets.videoinfo import VideoInfo
from thread.clientudpthread import ClientUDPThread

from utility import Utility

from gui.screens.client_window import Window
from database import User


class MyWindow(Window):
    def __init__(self):
        super().__init__()

        self.user = None
        self.resolutions = {'240p': '426 240', '480p': '854 480', '720p': '1280 720'}

        # PyQt stuff

        self.page1.button1.clicked.connect(self.login)
        self.page1.button2.clicked.connect(lambda: self.setPage(1))
        self.page1.button3.clicked.connect(self.configureSockets)

        self.page2.button1.clicked.connect(self.register)
        self.page2.button2.clicked.connect(lambda: self.setPage(0))
        self.page1.button3.clicked.connect(self.configureSockets)

        self.page3.navbar.buttons[0].clicked.connect(self.refresh)
        self.page3.navbar.buttons[1].clicked.connect(self.cancelStream)
        self.page3.navbar.buttons[2].clicked.connect(self.configureSockets)
        self.page3.navbar.buttons[3].clicked.connect(self.logout)

        self.page3.controlPanel.button1.clicked.connect(self.controlPanelButton1Function)
        self.page3.controlPanel.button2.clicked.connect(self.controlPanelButton2Function)
        self.page3.controlPanel.button3.clicked.connect(self.controlPanelButton3Function)
        self.page3.controlPanel.button4.clicked.connect(self.controlPanelButton4Function)
        self.page3.controlPanel.button5.clicked.connect(self.controlPanelButton5Function)

        self.setPage(0)

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



    def getUserInfo(self, username: str):
        self.setAlert('')
        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'isMemberOrAdmin'.encode('utf-8'))
        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, '{}'.format(username).encode('utf-8'))
        response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
        isMemberOrAdmin = True if response == 'True' else False

        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'isAdmin'.encode('utf-8'))
        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, '{}'.format(username).encode('utf-8'))
        response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
        isAdmin = True if response == 'True' else False

        self.log('premium[{}] isMemberOrAdmin[{}] isAdmin[{}]'.format(self.user.premium, isMemberOrAdmin, isAdmin))

        return isMemberOrAdmin, isAdmin

    def controlPanelButton1Function(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
            if self.user.premium:
                if isMemberOrAdmin:
                    self.setAlert('Você já pertence a um grupo')
                else:
                    # Criar o grupo
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'insert_room'.encode('utf-8'))
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                    response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                    success = True if response == 'True' else False
                    if success:
                        self.setAlert('Grupo criado com sucesso')
                    else:
                        self.setAlert('Ocorreu um erro ao criar o grupo')
            else:
                self.setAlert('Você não é um usuário Premium')

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def controlPanelButton2Function(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
            if self.user.premium:
                if isMemberOrAdmin:
                    if isAdmin:
                        # Deletar o grupo
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'delete_room'.encode('utf-8'))
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                        response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                        success = True if response == 'True' else False
                        if success:
                            self.setAlert('Grupo deletado com sucesso')
                        else:
                            self.setAlert('Ocorreu um erro ao deletar o grupo')
                    else:
                        # Deixar o grupo
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'select_admin_by_member_or_admin'.encode('utf-8'))
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                        response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'delete_member'.encode('utf-8'))
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, response.encode('utf-8'))
                        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                        response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                        self.setAlert(response)
                else:
                    self.setAlert('Você não pertence a nenhum grupo')
            else:
                if isMemberOrAdmin:
                    # Deixar o grupo
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'select_admin_by_member_or_admin'.encode('utf-8'))
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                    response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'delete_member'.encode('utf-8'))
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, response.encode('utf-8'))
                    Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                    response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                    self.setAlert(response)
                else:
                    self.setAlert('Você não pertence a nenhum grupo')

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def controlPanelButton3Function(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
            if isMemberOrAdmin:
                # Listar os membros
                Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'select_admin_by_member_or_admin'.encode('utf-8'))
                Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'select_members'.encode('utf-8'))
                Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, response.encode('utf-8'))
                response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                count = int(response)

                if count > 0:
                    admin = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                    members = []
                    for i in range(count - 1):
                        name = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                        addr = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                        members.append([name, addr])

                    text = '\n  Administrador:\n   {}\n  Membros:\n'.format(admin)
                    for member in members:
                        text += '   {} @ {}\n'.format(member[0], member[1])

                    self.log(text)
            else:
                self.setAlert('Você não pertence a nenhum grupo')

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def controlPanelButton4Function(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
            if self.user.premium:
                if isMemberOrAdmin:
                    if isAdmin:
                        # Remove membro do grupo
                        dialog = InputDialog(title='Remover membro', labels=['Nome de usuário'])
                        dialog.exec()
                        if dialog.result() == 1:
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'delete_member'.encode('utf-8'))
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, dialog.lineEdits[0].text().encode('utf-8'))
                            response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

                            self.setAlert(response)
                    else:
                        self.setAlert('Você não é administrador deste grupo')
                else:
                    self.setAlert('Você não administra nenhum grupo')
            else:
                self.setAlert('Você não é um usuário Premium')

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def controlPanelButton5Function(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
            if self.user.premium:
                if isMemberOrAdmin:
                    if isAdmin:
                        # Insere membro no grupo
                        dialog = InputDialog(title='Inserir membro', labels=['Nome de usuário'])
                        dialog.exec()
                        if dialog.result() == 1:
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'insert_member'.encode('utf-8'))
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, self.user.username.encode('utf-8'))
                            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, dialog.lineEdits[0].text().encode('utf-8'))
                            response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                            self.setAlert(response)
                    else:
                        self.setAlert('Você não é administrador deste grupo')
                else:
                    self.setAlert('Você não administra nenhum grupo')
            else:
                self.setAlert('Você não é um usuário Premium')

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

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

        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()
            self.tcpSocket.connect(self.tcpTarget)

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def cancelStream(self):
        # TODO: Is it okay to directly call a QThread method? Without a signal?
        self.udpThread.closeMediaThread()
        Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [self.user.username, 'cancel'], True)

    def quit(self):
        self.cancelStream()
        qApp.quit()

    @pyqtSlot(QWidget)
    def requestStream(self, videoInfo):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            if not self.user.premium:
                self.setAlert('Você não é um usuário premium')
            else:
                isMemberOrAdmin, isAdmin = self.getUserInfo(self.user.username)
                self.cancelStream()
                i = str(self.page3.controlPanel.resolutionComboBox.currentText())
                w, h = self.resolutions[i].split(' ')

                if isAdmin:
                    dialog = StreamTypeDialog()
                    dialog.exec()

                    if dialog.option == 1:
                        Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [self.user.username, 'stream', videoInfo.fullpath, w, h], True)
                    elif dialog.option == 2:
                        Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [self.user.username, 'stream_group', videoInfo.fullpath, w, h], True)
                else:
                    Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [self.user.username, 'stream', videoInfo.fullpath, w, h], True)

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def requestVideoInfo(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            videoListLayout = self.page3.videoPanel.listLayout
            for i in range(videoListLayout.count()):
                widget = videoListLayout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            Utility.sendUDPMessages(self.udpSocket, self.udpTarget, [self.user.username, 'videoinfolist'], True)

        except Exception as e:
            self.setAlert('Falha na conexão!')
            self.log(str(e))
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    @pyqtSlot(str, str, QPixmap)
    def insertVideoInfo(self, fullpath, title, thumbnail):
        videoListLayout = self.page3.videoPanel.listLayout
        for i in range(videoListLayout.count()):
            widget = videoListLayout.itemAt(i).widget()
            if widget is not None and widget.fullpath == fullpath:
                return

        widget = VideoInfo(fullpath, title, thumbnail)
        widget.button.hide()
        widget.mouseReleaseSignal.connect(self.requestStream)
        videoListLayout.insertWidget(0, widget)

    
    def refresh(self):
        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()
            
            #

            self.requestVideoInfo()

        except:
            self.setAlert('Falha na Conexão')
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()
        

    def login(self):
        username = self.page1.lineEdit1.text().strip()
        password = self.page1.lineEdit2.text().strip()
        self.setAlert('({}, {})'.format(username, password))

        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'login'.encode('utf-8'))
            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, username.encode('utf-8'))
            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, password.encode('utf-8'))
            response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')

            # TODO: Hide/Show control buttons accordingly

            if response == 'allow':
                response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
                isPremium = True if response == 'True' else False
                self.user = User(username, password, isPremium)
                self.setPage(2)
            else:
                self.setAlert(response)
        except:
            self.setAlert('Falha na Conexão')
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def register(self):
        username = self.page2.lineEdit1.text().strip()
        password = self.page2.lineEdit2.text().strip()
        premium = self.page2.lineEdit3.text().strip()
        self.setAlert('({}, {}, {})'.format(username, password, premium))

        try:
            self.setAlert('')
            self.page1.button3.hide()
            self.page2.button3.hide()
            self.page3.navbar.buttons[2].hide()

            #

            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'register'.encode('utf-8'))
            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, username.encode('utf-8'))
            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, password.encode('utf-8'))
            Utility.sendTCPMessage(self.tcpSocket, self.envoyLength,  premium.encode('utf-8'))
            response = Utility.recvTCPMessage(self.tcpSocket, self.envoyLength).decode('utf-8')
            if response == 'allow':
                self.setAlert('Usuário registrado com sucesso!')
            else:
                self.setAlert(response)
        except:
            self.setAlert('Falha na Conexão')
            self.page1.button3.show()
            self.page2.button3.show()
            self.page3.navbar.buttons[2].show()

    def logout(self):
        self.cancelStream()

        self.setPage(0)
        self.user = None
        self.setAlert('')
        self.page1.button3.hide()
        self.page2.button3.hide()
        self.page3.navbar.buttons[2].hide()

        self.page1.lineEdit1.setText('')
        self.page1.lineEdit2.setText('')

        self.page2.lineEdit1.setText('')
        self.page2.lineEdit2.setText('')
        self.page2.lineEdit3.setText('')

    def closeEvent(self, event):
        Utility.sendTCPMessage(self.tcpSocket, self.envoyLength, 'disconnect'.encode('utf-8'))


subprocess.run('cls', shell=True)
Utility.debug = False

app = QApplication(sys.argv)
app.setStyleSheet('QToolTip {background-color: black; color: white; border: black solid 1px;}')
window = MyWindow()
window.show()
app.exec()
