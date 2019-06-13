# import logging

# import vlc
# from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
# from . import videolan

# log = logging.getLogger(__name__)


# class ListPlayerSignals(QObject):

#     next_item_set = pyqtSignal(vlc.Event)
#     played = pyqtSignal(vlc.Event)
#     stopped = pyqtSignal(vlc.Event)

#     def __init__(self, list_player: vlc.MediaListPlayer):
#         super().__init__()
#         type_slot_pairs = [
#             (vlc.EventType.MediaListPlayerNextItemSet, self._on_next_item_set),
#             (vlc.EventType.MediaListPlayerPlayed, self._on_played),
#             (vlc.EventType.MediaListPlayerStopped, self._on_stopped),
#         ]
#         event_manager = videolan.list_player.event_manager()
#         for e_type, cb_slot in type_slot_pairs:
#             event_manager.event_attach(e_type, cb_slot)

#     @pyqtSlot(vlc.Event)
#     def _on_next_item_set(self, e):
#         self.next_item_set.emit(e)

#     @pyqtSlot(vlc.Event)
#     def _on_played(self, e):
#         self.played.emit(e)

#     @pyqtSlot(vlc.Event)
#     def _on_stopped(self, e):
#         self.stopped.emit(e)


# list_player_signals = ListPlayerSignals()
