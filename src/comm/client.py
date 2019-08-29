import logging
from array import array

from PyQt5.QtCore import QByteArray

from . import socks
from .. import vlcqt
from ..util import config

log = logging.getLogger(__name__)


class RemoteInputManager:
    def __init__(self):
        self.motion_state = None
        self.state_changed = False
        self.socket = socks.AutoReconnectSocket()

        self._curr_motion_state = QByteArray()
        self._last_motion_state = QByteArray()

        self.socket.binaryMessageReceived.connect(self.received_bytes)

    def received_bytes(self, qbytearray):
        self._curr_motion_state = qbytearray

    def get_new_motion_state(self):
        if self._curr_motion_state == self._last_motion_state:
            return None
        motion_state_array = array("d", self._curr_motion_state.data())
        return motion_state_array
