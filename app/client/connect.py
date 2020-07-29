import logging
from typing import List

import config
from gui import icons
from output.status import IconStatusLabel
from PyQt5 import QtCore, QtNetwork
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QWidgetAction

log = logging.getLogger(__name__)


CONNECTION_STATUS_TIPS = {
    QtNetwork.QAbstractSocket.ConnectedState: "Connected",
    QtNetwork.QAbstractSocket.ConnectingState: "Connecting...",
    QtNetwork.QAbstractSocket.UnconnectedState: "Disconnected",
}
CONNECTION_TOOL_TIPS = {
    QtNetwork.QAbstractSocket.ConnectedState: "Press To Disconnect",
    QtNetwork.QAbstractSocket.ConnectingState: "Connecting...",
    QtNetwork.QAbstractSocket.UnconnectedState: "Press To Connect",
}


def connection_status_tip(state):
    if state in (
        QtNetwork.QAbstractSocket.ConnectedState,
        QtNetwork.QAbstractSocket.UnconnectedState,
    ):
        return CONNECTION_STATUS_TIPS[state]
    else:
        return CONNECTION_STATUS_TIPS[QtNetwork.QAbstractSocket.ConnectingState]


def connection_tool_tip(state):
    if state in (
        QtNetwork.QAbstractSocket.ConnectedState,
        QtNetwork.QAbstractSocket.UnconnectedState,
    ):
        return CONNECTION_TOOL_TIPS[state]
    else:
        return CONNECTION_TOOL_TIPS[QtNetwork.QAbstractSocket.ConnectingState]


class ConnectAction(QWidgetAction):
    changed = QtCore.pyqtSignal(QtNetwork.QAbstractSocket.SocketState)

    def __init__(self, socket, parent):
        super().__init__(parent)
        self.socket = socket
        self.button = None
        self.setCheckable(True)
        self.setIcon(icons.get("connect_to_server_status"))
        self.update(self.socket.state())

        self.socket.stateChanged.connect(self.update)
        self.triggered.connect(self.on_triggered)

    def on_triggered(self, checked):
        if checked:
            self.socket.connect(config.state.url)
        else:
            self.socket.disconnect()

    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketState)
    def update(self, socketState: QtNetwork.QAbstractSocket.SocketState):
        if socketState == QtNetwork.QAbstractSocket.ConnectedState:
            self.setEnabled(True)
            self.setChecked(True)
        elif socketState == QtNetwork.QAbstractSocket.UnconnectedState:
            self.setEnabled(True)
            self.setChecked(False)
        elif socketState == QtNetwork.QAbstractSocket.ConnectingState:
            self.setEnabled(False)
            self.setChecked(False)
        self.changed.emit(socketState)

    def statusTip(self):
        state = self.socket.state()
        return connection_status_tip(state)

    def toolTip(self):
        state = self.socket.state()
        return connection_tool_tip(state)

    def text(self):
        return self.statusTip()


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


class ConnectWideButton(QToolButton):

    extra_width_chars = 2

    def __init__(self, parent, action: ConnectAction):
        super().__init__(parent)
        self.setObjectName("connect")
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
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
        self.defaultAction().changed.connect(self.updateText)

    def event(self, e):
        """Set action as unchecked when button is clicked while disabled, to allow
        forced cancelling of a connection attempt before timeout.
        """
        if e.type() == QtCore.QEvent.MouseButtonPress:
            action = self.defaultAction()
            socket = action.socket
            if socket.state() == socket.ConnectingState:
                socket.disconnect()
                return True
        return super().event(e)

    def on_socket_stateChanged(self, state):
        action = self.defaultAction()
        self.setText(action.toolTip())
        self.updateText(hovering=self.underMouse())

    def enterEvent(self, e):
        self.updateText(hovering=True)

    def leaveEvent(self, e):
        self.updateText(hovering=False)

    def updateText(self, hovering=None):
        if hovering if not None else self.underMouse():
            action = self.defaultAction()
            self.setText(action.toolTip())
        else:
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


class ConnectStatusLabel(IconStatusLabel):
    def __init__(self, parent, socket):
        super().__init__(parent=parent, icon=icons.get("connect_to_server_status"))
        self.socket = socket
        self.update_state(self.socket.state())
        self.socket.stateChanged.connect(self.update_state)

    @QtCore.pyqtSlot(QtNetwork.QAbstractSocket.SocketState)
    def update_state(self, state):
        status_tip = connection_status_tip(state)
        if state == self.socket.ConnectedState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Selected,
                state=QIcon.On,
                elide_mode=QtCore.Qt.ElideMiddle,
            )
        elif state == self.socket.ConnectingState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Disabled,
                state=QIcon.Off,
                elide_mode=QtCore.Qt.ElideMiddle,
            )
        elif state == self.socket.UnconnectedState:
            self.set_status(
                text=f"{status_tip} ({config.state.url})",
                mode=QIcon.Normal,
                state=QIcon.Off,
                elide_mode=QtCore.Qt.ElideMiddle,
            )

    def get_status_txt(self, status, url=""):
        return f"{status} {url}"
