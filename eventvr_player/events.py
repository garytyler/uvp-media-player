import logging

import vlc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

log = logging.getLogger(__name__)


class ListSignals(QObject):
    list_player: MediaListPlayer = None

    next_item_set = pyqtSignal(vlc.Event)
    played = pyqtSignal(vlc.Event)
    stopped = pyqtSignal(vlc.Event)

    def __init__(self, list_player: vlc.MediaListPlayer):
        super().__init__()
        self.list_player = list_player
        self.event_manager = list_player.event_manager()

        type_slot_pairs = [
            (vlc.EventType.MediaListPlayerNextItemSet, self._on_next_item_set),
            (vlc.EventType.MediaListPlayerPlayed, self._on_played),
            (vlc.EventType.MediaListPlayerStopped, self._on_stopped),
        ]

        for e_type, cb_slot in type_slot_pairs:
            self.event_manager.event_attach(e_type, cb_slot)

    @pyqtSlot(vlc.Event)
    def _on_next_item_set(self, e):
        self.next_item_set.emit(e)

    @pyqtSlot(vlc.Event)
    def _on_played(self, e):
        self.played.emit(e)

    @pyqtSlot(vlc.Event)
    def _on_stopped(self, e):
        self.stopped.emit(e)
