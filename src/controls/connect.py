from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QSizePolicy, QToolButton

from ..gui import icons


class ServerConnectionAction(QAction):
    startedconnecting = pyqtSignal()
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, client, viewpoint_manager, parent):
        super().__init__(parent=parent)
        self.setIcon(icons.server_connection)
        self.setIconText("Disconnected")
        self.setToolTip("Server is disconnected")
        self.setCheckable(True)

        self.client = client
        self.vp_manger = viewpoint_manager

        self.client.socket.connected.connect(self.on_connected)
        self.client.socket.disconnected.connect(self.on_disconnected)

        self.startedconnecting.connect(self.on_startedconnecting)

        self.setDisabled(True)

        self.start_connecting()

    def start_connecting(self, url="wss://eventvr.herokuapp.com/mediaplayer"):
        self.client.socket.attempt_open_on_interval(url=url)
        self.startedconnecting.emit()

    def on_startedconnecting(self):
        self.setIconText("Connecting...")

    @pyqtSlot()
    def on_connected(self,):
        self.connected.emit()
        self.setChecked(True)

    @pyqtSlot()
    def on_disconnected(self):
        self.disconnected.emit()
        self.setChecked(False)


class ServerConnectionButton(QToolButton):
    def __init__(self, action, parent, size):
        super().__init__(parent=parent)
        self.action = action
        self.setStyleSheet("font-size:8;")
        self.setDefaultAction(self.action)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.action.setDisabled(True)

        self.setMinimumSize(self.sizeHint())
        self.url = None
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.action.connected.connect(self.on_connected)
        self.action.disconnected.connect(self.on_disconnected)

    @pyqtSlot()
    def on_connected(self):
        self.url = self.action.client.socket.qurl.toDisplayString()
        self.action.setIconText(f"Connected")
        self.update_url_display()

    @pyqtSlot()
    def on_disconnected(self):
        self.url = None
        self.action.setIconText("Disconnected")

    def update_url_display(self):
        if self.url:
            elided_txt = self.get_elided_txt(self.url)
            self.action.setIconText(f"Connected:\n{elided_txt}")

    def get_elided_txt(self, string):
        return QFontMetrics(self.font()).elidedText(
            string, Qt.ElideRight, self.sizeHint().width()
        )

    def resizeEvent(self, e):
        self.update_url_display()


class ServerConnectionWidget(QLabel):
    def __init__(self, client, viewpoint_manager):
        super().__init__()
        self.client = client
        self.vp_manger = viewpoint_manager
        self.client.socket.disconnected.connect(self.on_disconnected)

        self.qapp = QApplication.instance()
        self.setToolTip("Server is disconnected.")
        self.set_icons()

    def set_icons(self):
        self.icon_size = QSize(48, 48)
        self.connected_icon = icons.server_connection.pixmap(
            self.icon_size, QIcon.Normal, QIcon.On
        )
        self.disconnected_icon = icons.server_connection.pixmap(
            self.icon_size, QIcon.Normal, QIcon.Off
        )
        self.setPixmap(self.disconnected_icon)

    def on_disconnected(self):
        self.setToolTip("Server is disconnected.")
        self.setPixmap(self.disconnected_icon)

    def on_connected(self):
        self.setToolTip("Server is connected.")
        self.setPixmap(self.connected_icon)
