from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QWidget, QLabel, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from gui.widgets.roundpushbutton import RoundPushButton
import os


class VideoInfo(QWidget):
    mouseReleaseSignal = pyqtSignal(QWidget)

    def __init__(self, fullpath: str, title: str, thumbnail: QPixmap, read_only=True, icon_path=None):
        super().__init__()

        self.fullpath = fullpath
        self.title = title
        self.thumbnail = thumbnail

        self.setStyleSheet('font-family: Roboto;')

        # --------------------------------------------------

        self.thumbnailLabel = QLabel()
        self.thumbnailLabel.setFixedSize(int(96 * 16.0 / 9.0), 96)
        if self.thumbnail is not None:
            self.thumbnailLabel.setPixmap(self.thumbnail)

        self.titleLineEdit = QLineEdit(self.title)
        self.titleLineEdit.setStyleSheet('font-size: 16px;')
        self.titleLineEdit.setTextMargins(24, 0, 0, 0)
        self.titleLineEdit.editingFinished.connect(self.validate_title)

        self.titleLineEdit.setReadOnly(read_only)
        if read_only:
            self.setCursor(Qt.PointingHandCursor)
            self.titleLineEdit.setCursor(Qt.PointingHandCursor)
        else:
            self.titleLineEdit.setCursor(Qt.IBeamCursor)

        path = os.path.normpath(self.fullpath).split(os.path.normpath(os.getcwd()))[-1]

        self.pathLabel = QLabel(path)
        self.pathLabel.setStyleSheet('font-size: 12px;')
        self.pathLabel.setWordWrap(True)
        self.pathLabel.setMargin(24)

        self.button = RoundPushButton(icon_path=icon_path)

        self.containerLayout = QGridLayout()
        self.containerLayout.addWidget(self.thumbnailLabel, 0, 0, 2, 1)
        self.containerLayout.addWidget(self.titleLineEdit,  0, 1, 1, 1)
        self.containerLayout.addWidget(self.pathLabel,      1, 1, 1, 1)
        self.containerLayout.addWidget(self.button,         0, 2, 2, 1)

        self.container = QWidget()
        self.container.setLayout(self.containerLayout)
        self.container.setStyleSheet('background-color: #2f2f2f;')
        self.container.setContentsMargins(0, 0, 0, 0)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

    def mouseReleaseEvent(self, event):
        self.mouseReleaseSignal.emit(self)

    def validate_title(self):
        text = self.titleLineEdit.text()
        if text.strip() != '':
            self.title = text
        self.titleLineEdit.setText(self.title)
