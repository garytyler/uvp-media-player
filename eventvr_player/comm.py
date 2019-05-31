import array
import json
import logging
import random
import string

from PyQt5.QtCore import QByteArray, Qt, QTimer, QUrl
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol

log = logging.getLogger(__name__)


def rand_id(size=6):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(size)
    )


class ClientSocketBase(QWebSocket):
    def __init__(self):
        QWebSocket.__init__(
            self, origin="", version=QWebSocketProtocol.Version13, parent=None
        )
        # Connect base methods to signals
        self.connected.connect(self.__connected)
        self.textMessageReceived.connect(self.__textMessageReceived)
        self.binaryMessageReceived.connect(self.__binaryMessageReceived)
        self.disconnected.connect(self.__disconnected)

    def __connected(self):
        self.connect_timer.stop()
        self.peeraddr = self.peerAddress().toString()
        log.info(f"CONNECTED to [{self.peeraddr}]")

    def __disconnected(self):
        self.connect_timer.start()
        log.info(f"DISCONNECTED from ({self.peeraddr})")
        self.peeraddr = None

    def __textMessageReceived(self, data):
        log.debug(f"RECEIVED TEXT [{data}]")
        self.received_text(data)

    def __binaryMessageReceived(self, qbytearray):
        log.debug(f"RECEIVED BYTES")

    def _pong(self, elapsed_time, payload):
        if not str(payload) == str(self.__payload):
            raise RuntimeError("Ping payload mismatch")
        else:
            print("pong time: {}".format(elapsed_time))
            self.__payload = None

    def send_ping(self):
        self.__payload = rand_id().encode()
        self.pong.connect(self._pong)
        self.ping(self.__payload)


class AutoConnectSocket(ClientSocketBase):
    def __init__(self, url=None):
        ClientSocketBase.__init__(self)
        self._set_url(url)

        # Timer for connection attempts
        self.connect_timer = QTimer()
        self.connect_timer.setTimerType(Qt.CoarseTimer)
        self.connect_timer.timeout.connect(self._on_attempt_interval)
        self.connect_timer.setInterval(1000)

        self.connected.connect(self.connect_timer.stop)
        self.disconnected.connect(self.connect_timer.start)

    def _set_url(self, url):
        if url:
            self.url = url
            self.qurl = QUrl(self.url)

    def _on_attempt_interval(self):
        self.open(self.qurl)
        log.info(f"No connection found [{self.url}] {self.closeCode()}")

    def attempt_open_once(self, url=None):
        self._set_url(url)
        self.open(self.qurl)

    def attempt_open_at_interval(self, interval=1000, url=None):
        self._set_url(url)
        self.connect_timer.setInterval(interval)
        QTimer.singleShot(0, self.connect_timer.start)


class RemoteInputClient:
    def __init__(self, url):
        self.motion_state = None
        self.state_changed = False
        self.socket = comm.AutoConnectSocket(url)

        self._curr_motion_state = QByteArray()
        self._last_motion_state = QByteArray()

        self.socket.textMessageReceived.connect(self.received_text)
        self.socket.binaryMessageReceived.connect(self.received_bytes)

        # TODO Call this later to not risk a connection before all signals are connected
        self.socket.attempt_open_at_interval()

    def received_bytes(self, qbytearray):
        self._curr_motion_state = qbytearray

    def get_new_motion_state(self):
        if not self._curr_motion_state.compare(self._last_motion_state):
            return None
        values = (y, p, r) = array.array("d", self._curr_motion_state.data())
        self._last_motion_state = self._curr_motion_state
        log.debug(values)
        return values
