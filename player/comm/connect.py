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
    QWidgetAction,
)

from ..base.buttons import ActionButton
from ..gui import icons
from ..output.status import IconStatusLabel, TextStatusLabel
from ..util import config

log = logging.getLogger(__name__)


class ConnectToServerAction(QWidgetAction):
    stoppedconnecting = pyqtSignal(bool)
    disconnected = pyqtSignal()

    DisconnectedMode = 0
    ConnectingMode = 1
    ConnectedMode = 2

    mode_status_tips = {
        DisconnectedMode: "Disconnected",
        ConnectingMode: "Connecting...",
        ConnectedMode: "Connected",
    }
    mode_tool_tips = {
        DisconnectedMode: "Connect Now",
        ConnectingMode: "Connecting...",
        ConnectedMode: "Disconnect Now",
    }

    def __init__(self, auto_connect_socket, connect_status_widget, parent):
        super().__init__(parent)
        self.socket = auto_connect_socket
        self.connect_status_widget = connect_status_widget
        self.parent = parent
        self.setIcon(icons.connect_to_server_status)
        self.setCheckable(True)
        self.set_mode(self.DisconnectedMode)

        self.socket.stoppedconnecting.connect(self.on_stoppedconnecting)
        self.socket.disconnected.connect(self.on_disconnected)
        self.triggered.connect(self.on_triggered)

    def createWidget(self, parent):
        return ConnectToServerWidget(self.parent, self)

    def on_triggered(self, checked):
        print("TRIGGERED", checked)
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

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode
        self.setText(self.mode_status_tips[self.mode])
        self.setStatusTip(self.mode_status_tips[self.mode])
        self.setToolTip(self.mode_tool_tips[self.mode])

        if self.mode == self.DisconnectedMode:
            self.setEnabled(True)
            self.setChecked(False)
            self.connect_status_widget.set_status(
                text=f"{self.mode_status_tips[self.mode]} ({config.state.url})",
                mode=QIcon.Normal,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )
        elif self.mode == self.ConnectingMode:
            self.setEnabled(False)
            self.setChecked(False)
            self.connect_status_widget.set_status(
                text=f"{self.mode_status_tips[self.mode]} ({config.state.url})",
                mode=QIcon.Disabled,
                state=QIcon.Off,
                elide_mode=Qt.ElideMiddle,
            )
        elif self.mode == self.ConnectedMode:
            self.setEnabled(True)
            self.setChecked(True)
            self.connect_status_widget
            self.connect_status_widget.set_status(
                text=f"{self.mode_status_tips[self.mode]} ({config.state.url})",
                mode=QIcon.Selected,
                state=QIcon.On,
                elide_mode=Qt.ElideMiddle,
            )


class ProxyToolButton(QToolButton):
    """Cosmetic button that lets the parent button or a connected action handle the the
    manage it's state. Useful as one of multiple child buttons all connected to the
    same function that can serve a unique layout.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("connect")

    def mousePressEvent(self, e):
        e.ignore()

    def mouseReleaseEvent(self, e):
        e.ignore()


class ConnectToServerWidget(QToolButton):

    leave_style_sheets = {
        ConnectToServerAction.DisconnectedMode: "color: crimson;",
        ConnectToServerAction.ConnectedMode: "color: darkgreen;",
    }
    border_width = "2px"

    mouse_press_style_sheets = {
        "pressed": {
            "text": f"border: {border_width} inset palette(base); border-left:none;",
            "icon": f"border: {border_width} inset palette(base); border-right:none;",
        },
        "unpressed": {
            "text": f"border: {border_width} outset palette(base); border-left:none;",
            "icon": f"border: {border_width} outset palette(base); border-right:none;",
        },
    }

    def __init__(self, parent, connect_to_server_action):
        super().__init__(parent)
        self.action = connect_to_server_action
        self.setLayout(QHBoxLayout(self))
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.icon_bttn = ProxyToolButton(self)
        self.icon_bttn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.icon_bttn.setIconSize(QSize(32, 32))
        self.icon_bttn.setDefaultAction(connect_to_server_action)
        self.icon_bttn.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.text_bttn = ProxyToolButton(self)
        self.text_bttn.setDefaultAction(connect_to_server_action)
        self.text_bttn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.text_bttn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.layout().addWidget(self.icon_bttn, alignment=Qt.AlignLeft)
        self.layout().addWidget(self.text_bttn, alignment=Qt.AlignJustify)

        self.text_bttn.setFixedWidth(self.get_max_text_bttn_width() + 10)
        self.set_proxy_buttons_unpressed()

        self.action.stoppedconnecting.connect(self.on_stoppedconnecting)

    def get_max_text_bttn_width(self):
        """Get the largest potential width of the button, suitable for setting as minimum width.
        """
        start_text = self.text_bttn.text()
        mode_widths = []
        potential_strings = list(self.action.mode_tool_tips.values()) + list(
            self.action.mode_status_tips.values()
        )
        for string in potential_strings:
            self.text_bttn.setText(string)
            width = self.text_bttn.sizeHint().width()
            mode_widths.append(width)
        self.text_bttn.setText(start_text)
        return max(mode_widths)

    def mousePressEvent(self, e):
        e.accept()
        self._pressed = True
        self.set_proxy_buttons_pressed()

    def mouseReleaseEvent(self, e):
        self._pressed = False
        self.set_proxy_buttons_unpressed()
        if self._hovered:
            self.action.triggered.emit(not self.action.isChecked())

    def set_proxy_buttons_pressed(self):
        self.text_bttn.setStyleSheet(self.mouse_press_style_sheets["pressed"]["text"])
        self.icon_bttn.setStyleSheet(self.mouse_press_style_sheets["pressed"]["icon"])

    def set_proxy_buttons_unpressed(self):
        self.text_bttn.setStyleSheet(self.mouse_press_style_sheets["unpressed"]["text"])
        self.icon_bttn.setStyleSheet(self.mouse_press_style_sheets["unpressed"]["icon"])

    def enterEvent(self, e):
        self._hovered = True
        self.text_bttn.setText(self.text_bttn.toolTip())

    def leaveEvent(self, e):
        print("leave")
        self._hovered = False
        self.text_bttn.setText(self.text_bttn.statusTip())

    def on_stoppedconnecting(self, is_connected):
        """If connected/disconnected before leave event, go ahead and update text color to deliver smooth feedback instead of flashing a separate hover color.
        """
        self.text_bttn.setText(self.text_bttn.statusTip())
        if not self._hovered:
            return None
        elif is_connected:
            self.text_bttn.setStyleSheet("color: darkgreen;")
        else:
            self.text_bttn.setStyleSheet("color: crimson;")

    def sizeHint(self):
        return QSize(
            self.layout().totalSizeHint().width(), self.icon_bttn.sizeHint().height()
        )
