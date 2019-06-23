from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel

from . import comm, icons, viewpoint


class ServerConnectionWidget(QLabel):
    url = "wss://eventvr.herokuapp.com/mediaplayer"

    def __init__(self):
        super().__init__()
        self.qapp = QApplication.instance()
        self.setToolTip("Server is disconnected.")
        self.set_icons()

        self.client = comm.RemoteInputClient(url=self.url)
        self.vp_manager = viewpoint.ViewpointManager(client=self.client)
        self.client.socket.connected.connect(self.on_connected)
        self.client.socket.disconnected.connect(self.on_disconnected)

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
