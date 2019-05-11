import json
import random
import string

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol


def rand_id(size=6):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(size)
    )


class ClientSocket(QWebSocket):
    def __init__(self):
        QWebSocket.__init__(
            self, origin="", version=QWebSocketProtocol.Version13, parent=None
        )

    # def _pong(self, elapsed_time, payload):
    #     if not str(payload) == str(self.__payload):
    #         raise RuntimeError("Ping payload mismatch")
    #     else:
    #         print("pong time: {}".format(elapsed_time))
    #         self.__payload = None

    # def do_ping(self):
    #     self.__payload = rand_id().encode()
    #     self.pong.connect(self._pong)
    #     self.ping(self.__payload)

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.errorString())


class ClientConnectionBase:
    """Base class that opens and maintains websocket connection in background."""

    def __init__(self, url):
        self.url = url

        # Connect base methods to signals
        self.sock = ClientSocket()

        self.sock.sslErrors.connect(self.ssl_errors)

        self.sock.connected.connect(self._connected)
        self.sock.disconnected.connect(self._disconnected)
        self.sock.textMessageReceived.connect(self._received)

        # Timer for connection attempts
        self.connect_timer = QTimer()
        self.connect_timer.setTimerType(Qt.CoarseTimer)
        self.connect_timer.timeout.connect(self._attempt_connect)
        self.connect_timer.setInterval(1000)
        QTimer.singleShot(0, self.connect_timer.start)

    def ssl_errors(self, e):
        print(e, flush=True)

    def _attempt_connect(self):
        print(f"ATTEMPT CONNECT ({self.url})")
        self.sock.open(QUrl(self.url))

    def send(self, data):
        string = json.dumps(data)
        self.sock.sendTextMessage(string)

    def _received(self, string):
        data = json.loads(string)
        self.received(data)

    def _connected(self):
        self._connected = True
        self.connect_timer.stop()
        self.localaddr = self.sock.localAddress().toString()
        self.peername = self.sock.peerName()
        self.peeraddr = self.sock.peerAddress().toString()
        print(f"Connected ({self.localaddr}) to '{self.peername}' ({self.peeraddr})")
        self.connected()

    def _disconnected(self):
        print("DISCONNECTED")
        self._connected = False

        # print(f"Disconnected ({self.localaddr}) from {self.peername} ({self.peeraddr})")
        self.localaddr = None
        self.peername = None
        self.peeraddr = None
        self.connect_timer.start()
        self.disconnected()

    def received(self, data):
        """Base method"""
        pass

    def connected(self):
        """Base method"""
        pass

    def disconnected(self):
        """Base method"""
        pass
