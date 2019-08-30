import logging

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAction,
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from ..base.buttons import ActionButton
from ..gui import icons
from ..util import config

# from ..output.status import StatusLabel

log = logging.getLogger(__name__)


class ConnectToServerAction(QAction):
    stoppedconnecting = pyqtSignal(bool)
    disconnected = pyqtSignal()

    DisconnectedMode = 0
    ConnectingMode = 1
    ConnectedMode = 2

    def __init__(self, auto_connect_socket, connect_status_widget, parent):
        super().__init__(parent=parent)
        self.socket = auto_connect_socket
        self.connect_status_widget = connect_status_widget
        self.parent = parent
        self.setIcon(icons.connect_to_server_status)
        self.setCheckable(True)
        self.icon = icons.connect_to_server_status
        self.set_mode(self.DisconnectedMode)

        self.socket.stoppedconnecting.connect(self.on_stoppedconnecting)
        self.socket.disconnected.connect(self.on_disconnected)
        self.triggered.connect(self.on_triggered)

    def on_triggered(self, checked):
        if checked:
            self.socket.connect(config.state.url)
            self.set_mode(self.ConnectingMode)
        else:
            self.socket.disconnect()

    @pyqtSlot(bool)
    def on_stoppedconnecting(self, is_connected):
        if is_connected:
            self.set_mode(self.ConnectedMode)
        else:
            self.set_mode(self.DisconnectedMode)

    @pyqtSlot()
    def on_disconnected(self):
        self.set_mode(self.DisconnectedMode)

    def get_status_txt(self, status, url=""):
        return f"{status} {url}"

    def set_mode(self, mode):
        if mode == self.DisconnectedMode:
            self.setEnabled(True)
            self.setChecked(False)
            self.setText("Connect")
            self.setToolTip("Connect to server")
            self.connect_status_widget.set_status(
                text=f"Disconnected ({config.state.url})",
                mode=QIcon.Normal,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )
        elif mode == self.ConnectingMode:
            self.setEnabled(False)
            self.setText("Connecting...")
            self.setToolTip("Connecting to server")
            self.connect_status_widget.set_status(
                text=f"Connecting... ({config.state.url})",
                mode=QIcon.Disabled,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )
        elif mode == self.ConnectedMode:
            self.setEnabled(True)
            self.setChecked(True)
            self.setText("Disconnect")
            self.setToolTip("Disconnect from server")
            self.connect_status_widget
            self.connect_status_widget.set_status(
                text=f"Connected ({config.state.url})",
                mode=QIcon.Normal,
                state=QIcon.On,
                elide_mode=Qt.ElideMiddle,
            )
