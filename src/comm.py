import array
import logging

from PyQt5.QtCore import QByteArray, Qt, QTimer, QUrl
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol

from . import comm, util

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
        self.__payload = util.rand_id().encode()
        self.pong.connect(self._pong)
        self.ping(self.__payload)


class AutoConnectSocket(ClientSocketBase):
    def __init__(self):
        ClientSocketBase.__init__(self)

        # Timer for connection attempts
        self.connect_timer = QTimer()
        self.connect_timer.setTimerType(Qt.VeryCoarseTimer)
        self.connect_timer.timeout.connect(self._on_attempt_interval)
        self.connect_timer.setInterval(1000)

        self.connected.connect(self.connect_timer.stop)
        self.disconnected.connect(self.connect_timer.start)

    def _on_attempt_interval(self):
        self.open(self.qurl)
        log.info(f"No connection found qurl={self.qurl}, exit_code{self.closeCode()}")

    def attempt_open_once(self, url):
        self.qurl = QUrl(url)
        self.open(self.qurl)

    def attempt_open_on_interval(self, url, interval=1000):
        self.qurl = QUrl(url)
        log.info(
            f"ATTEMPT SOCKET OPEN ON INTERVAL interval={interval}, url={self.qurl}"
        )
        self.connect_timer.setInterval(interval)
        QTimer.singleShot(0, self.connect_timer.start)


class RemoteInputClient:
    def __init__(self, url):
        self.motion_state = None
        self.state_changed = False
        self.socket = comm.AutoConnectSocket()

        self._curr_motion_state = QByteArray()
        self._last_motion_state = QByteArray()

        self.socket.binaryMessageReceived.connect(self.received_bytes)

        # TODO Call this later to not risk a connection before all signals are connected
        self.socket.attempt_open_on_interval(url=url)

    def received_bytes(self, qbytearray):
        self._curr_motion_state = qbytearray

    def get_new_motion_state(self):
        if self._curr_motion_state == self._last_motion_state:
            return
        motion_state_array = array.array("d", self._curr_motion_state.data())
        return motion_state_array
