import logging
from typing import List

from PyQt5.QtCore import QSize, Qt, QTextStream, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAction,
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
    QWidgetAction,
)

from ..base.buttons import ActionButton
from ..gui import icons
from ..output.status import IconStatusLabel
from ..util import config

log = logging.getLogger(__name__)


CONNECTION_STATUS_TIPS = {
    QAbstractSocket.ConnectedState: "Connected",
    QAbstractSocket.ConnectingState: "Connecting...",
    QAbstractSocket.UnconnectedState: "Disconnected",
}
CONNECTION_TOOL_TIPS = {
    QAbstractSocket.ConnectedState: "Press To Disonnect",
    QAbstractSocket.ConnectingState: "Connecting...",
    QAbstractSocket.UnconnectedState: "Press To Connect",
}


def connection_status_tip(state):
    if state in (QAbstractSocket.ConnectedState, QAbstractSocket.UnconnectedState):
        return CONNECTION_STATUS_TIPS[state]
    else:
        return CONNECTION_STATUS_TIPS[QAbstractSocket.ConnectingState]


def connection_tool_tip(state):
    if state in (QAbstractSocket.ConnectedState, QAbstractSocket.UnconnectedState):
        return CONNECTION_TOOL_TIPS[state]
    else:
        return CONNECTION_TOOL_TIPS[QAbstractSocket.ConnectingState]


class ConnectAction(QWidgetAction):
    def __init__(self, socket, parent):
        super().__init__(parent)
        self.socket = socket
        self.button = None
        self.setCheckable(True)
        self.setIcon(icons.connect_to_server_status)
        self.update_state(self.socket.state())

        self.socket.stateChanged.connect(self.update_state)
        self.triggered.connect(self.on_triggered)

    def on_triggered(self, checked):
        if checked:
            self.socket.connect(config.state.url)
        else:
            self.socket.disconnect()

    @pyqtSlot(QAbstractSocket.SocketState)
    def update_state(self, state):
        self.setStatusTip(self.statusTip())
        self.setToolTip(self.toolTip())
        self.setText(self.text())
        if state == self.socket.ConnectedState:
            self.setEnabled(True)
            self.setChecked(True)
        elif state == self.socket.UnconnectedState:
            self.setEnabled(True)
            self.setChecked(False)
        elif state == self.socket.ConnectingState:
            self.setEnabled(False)
            self.setChecked(False)

    def statusTip(self):
        state = self.socket.state()
        return connection_status_tip(state)

    def toolTip(self):
        state = self.socket.state()
        return connection_tool_tip(state)

    def text(self):
        return self.statusTip()


class ConnectWideButton(QToolButton):

    extra_width_chars = 2

    def __init__(self, parent, action: ConnectAction):
        super().__init__(parent)
        self.setObjectName("connect")
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setDefaultAction(action)

        text_strings: List[str] = []
        text_strings.extend(CONNECTION_STATUS_TIPS.values())
        text_strings.extend(CONNECTION_TOOL_TIPS.values())

        # Set text area width
        avg_char_width = self.fontMetrics().averageCharWidth()
        max_string_width_pixels = max(
            (self.fontMetrics().boundingRect(s).width() for s in text_strings)
        )
        extra_width_pixels = self.extra_width_chars * avg_char_width
        text_area_width_pixels = max_string_width_pixels + extra_width_pixels
        self.text_area_width_chars = int(text_area_width_pixels / avg_char_width)

        # Set total button width
        max_default_button_width = self.max_default_button_width(text_strings)
        total_button_width = max_default_button_width + extra_width_pixels
        self.setFixedWidth(total_button_width)

        # Init
        self.setText(action.text())
        action.socket.stateChanged.connect(action.update_state)

    def enterEvent(self, e):
        self.is_hovering = True
        action = self.defaultAction()
        self.setText(action.toolTip())

    def leaveEvent(self, e):
        self.is_hovering = False
        action = self.defaultAction()
        self.setText(action.statusTip())

    def max_default_button_width(self, text_strings):
        start_text = self.text()
        widths: List[int] = []
        for string in text_strings:
            self.setText(string)
            button_width = self.sizeHint().width()
            widths.append(button_width)
        self.setText(start_text)
        return max(widths)

    def setText(self, text):
        super().setText(text.center(self.text_area_width_chars))


class ConnectWideButtonBuilder(ConnectAction):
    extra_width_chars = 2

    def __init__(self, parent, socket):
        super().__init__(parent=parent, socket=socket)
        self.button = None

    def setText(self, text):
        if self.button:
            self.button.setText(text)

    def createWidget(self, parent):
        self.text_width_chars = "***"
        self.button = ConnectWideButton(parent=parent, action=self)
        return self.button


class ConnectStatusLabel(IconStatusLabel):
    def __init__(self, parent, socket):
        super().__init__(parent=parent, icon=icons.connect_to_server_status)
        self.socket = socket
        self.update_state(self.socket.state())
        self.socket.stateChanged.connect(self.update_state)

    @pyqtSlot(QAbstractSocket.SocketState)
    def update_state(self, state):
        status_tip = connection_status_tip(state)
        if state == self.socket.ConnectedState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Selected,
                state=QIcon.On,
                elide_mode=Qt.ElideMiddle,
            )
        elif state == self.socket.ConnectingState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Disabled,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )
        elif state == self.socket.UnconnectedState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Normal,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )

    def get_status_txt(self, status, url=""):
        return f"{status} {url}"
