import logging
from random import choice
from string import ascii_uppercase, digits

from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol

# from .. import util

log = logging.getLogger(__name__)


class ClientSocketBase(QWebSocket):
    def __init__(self):
        QWebSocket.__init__(
            self, origin="", version=QWebSocketProtocol.Version13, parent=None
        )
        # Connect base methods to signals
        self.connected.connect(self.__connected)
        self.disconnected.connect(self.__disconnected)

    def __connected(self):
        self.peeraddr = self.peerAddress().toString()
        log.info(f"CONNECTED peer_address={getattr(self, 'peeraddr', '')}")

    def __disconnected(self):
        log.info(f"DISCONNECTED peer_address={getattr(self, 'peeraddr', '')}")
        self.peeraddr = None

    def _pong(self, elapsed_time, payload):
        if not str(payload) == str(self.__payload):
            raise RuntimeError("Ping payload mismatch")
        else:
            print("pong time: {}".format(elapsed_time))
            self.__payload = None

    def send_ping(self):
        self.__payload = self.rand_id().encode()
        self.pong.connect(self._pong)
        self.ping(self.__payload)

    @staticmethod
    def rand_id(size=6):
        return "".join(choice(ascii_uppercase + digits) for _ in range(size))


class AutoConnectSocket(ClientSocketBase):
    startedconnecting = pyqtSignal()
    stoppedconnecting = pyqtSignal(bool)

    def __init__(self):
        ClientSocketBase.__init__(self)
        self.session_timer = None
        self.stable_timer = None
        self.__connection_expected = False
        self.qurl = QUrl()

        # Timer for connection attempts
        self.connect_timer = QTimer()
        self.connect_timer.setTimerType(Qt.VeryCoarseTimer)
        self.connect_timer.timeout.connect(self._attempt_open)

        self.connected.connect(self._on_connected)
        self.disconnected.connect(self._on_disconnected)

    def _attempt_open(self):
        self.open(self.qurl)
        log.info(f"SOCKET OPEN ATTEMPT qurl={self.qurl}")

    def _start_open_attempt_session(self, url, interval):
        self.qurl = QUrl(url)
        self.connect_timer.setInterval(interval)
        QTimer.singleShot(0, self.connect_timer.start)

    def _on_connected(self):
        self.connect_timer.stop()
        if self.stable_timer:
            self.stable_timer.stop()

        self.stable_timer = QTimer.singleShot(2000, self._stop_connecting)

    def _on_disconnected(self):
        if self.stable_timer:
            self.stable_timer.stop()
        if self.__connection_expected:
            self.connect_timer.start()

    def _stop_connecting(self):

        self.connect_timer.stop()
        is_connected = bool(self.state() == QAbstractSocket.ConnectedState)
        self.__connection_expected = is_connected
        self.stoppedconnecting.emit(is_connected)

    def connect(self, url, interval=1000, num_attempts=3):

        self.__connection_expected = True
        self._start_open_attempt_session(url, interval)
        if self.session_timer:
            self.session_timer.stop()
        session_length = num_attempts * interval + interval
        self.session_timer = QTimer.singleShot(session_length, self._stop_connecting)

    def disconnect(self):
        self.__connection_expected = False
        self.connect_timer.stop()
        self.close()
