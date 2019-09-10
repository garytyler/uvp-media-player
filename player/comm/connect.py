import logging

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
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


class ConnectActionCenterFillText(ConnectAction):
    def __init__(self, parent, socket):
        self.text_area_width_chars = None
        super().__init__(parent=parent, socket=socket)

    # def statusTip(self):
    #     if self.text_area_width_chars:
    #         return super().statusTip().center(self.text_area_width_chars)
    #     else:
    #         return super().statusTip()

    # def toolTip(self):
    #     if self.text_area_width_chars:
    #         return super().toolTip().center(self.text_area_width_chars)
    #     else:
    #         return super().toolTip()

    # def text(self):
    #     if self.text_area_width_chars:
    #         return super().text().center(self.text_area_width_chars)
    #     else:
    #         return super().text()


class ConnectButtonWidgetAction(QWidgetAction):
    extra_width_chars = 2

    def __init__(self, parent, socket):
        super().__init__(parent)
        self.socket = socket

        # super().__init__(
        #     parent=parent,
        #     socket=socket,
        # )
        # self.button.setDefaultAction(self)

    def createWidget(self, parent):

        self.action = ConnectActionCenterFillText(parent=parent, socket=self.socket)
        self.button = ConnectButton(parent=parent, action=self.action)
        # self.button.setDefaultAction(self.action)

        return self.button

    def statusTip(self):
        return self.status_tips[self.mode]

    def toolTip(self):
        return self.tool_tips[self.mode]

    def text(self):
        return super().statusTip()


class ConnectButton(QToolButton):

    extra_width_chars = 2

    def __init__(self, parent, action):
        super().__init__(parent)
        self.setObjectName("connect")
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setDefaultAction(action)

        text_strings = []
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

        # # Replace status_tip strings in action instance
        # for key, value in CONNECTION_STATUS_TIPS.items():
        #     text = value.center(self.text_area_width_chars)
        #     CONNECTION_STATUS_TIPS[key] = text

        # # Replace tool_tip strings in action instance
        # for key, value in CONNECTION_TOOL_TIPS.items():
        #     text = value.center(self.text_area_width_chars)
        #     CONNECTION_TOOL_TIPS[key] = text

        # Setup
        # self.update_button_text()
        # action.stoppedconnecting.connect(self.on_stoppedconnecting)

        # return super().setDefaultAction(action)

    def max_default_button_width(self, text_strings):
        # action = self.defaultAction()
        start_text = self.text()
        widths: list[int, int] = []
        for string in text_strings:
            self.setText(string)
            button_width = self.sizeHint().width()
            widths.append(button_width)
        self.setText(start_text)
        return max(widths)

    def setText(self, text):
        # text = text.center(self.text_area_width_chars)
        text = self.defaultAction().statusTip().center(self.text_area_width_chars)
        # print(text)
        super().setText(text)

    # def setText(self, text):
    #     # text = text.center(self.text_area_width_chars)
    #     text = self.defaultAction().statusTip().center(self.text_area_width_chars)
    #     # print(text)
    #     super().setText(text)

    # def text(self, text):

    # def update_button_text(self):
    #     try:
    #         _is_hovering = self.is_hovering
    #     except AttributeError:
    #         _is_hovering = self.is_hovering = False

    #     action = self.defaultAction()
    #     if _is_hovering:
    #         text = CONNECTION_TOOL_TIPS[action.mode]
    #     else:
    #         text = CONNECTION_TOOL_TIPS[action.mode]
    #     self.setText(text)

    # def enterEvent(self, e):
    #     self.is_hovering = True
    #     self.update_button_text()

    # def leaveEvent(self, e):
    #     self.is_hovering = False
    #     self.update_button_text()

    # def on_stoppedconnecting(self, is_connected):
    #     """If connected/disconnected before leave event, go ahead and update text color to deliver smooth feedback instead of flashing a separate hover color.
    #     """
    #     self.text_bttn.setText(self.text_bttn.statusTip())
    #     if not self._hovered:
    #         return None
    #     elif is_connected:
    #         self.text_bttn.setStyleSheet("color: darkgreen;")
    #     else:
    #         self.text_bttn.setStyleSheet("color: crimson;")
