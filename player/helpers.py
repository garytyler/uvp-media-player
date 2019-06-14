import vlc
from PyQt5.QtCore import QObject, pyqtSlot

from .vlc_objects import media_player

# class SignalObserver(QObject):
#     signal_names = [
#         "audiodevice",
#         "audiovolume",
#         "backward",
#         "buffering",
#         "chapterchanged",
#         "corked",
#         "esadded",
#         "esdeleted",
#         "esselected",
#         "encounterederror",
#         "endreached",
#         "forward",
#         "lengthchanged",
#         "mediachanged",
#         "muted",
#         "nothingspecial",
#         "opening",
#         "pausablechanged",
#         "paused",
#         "playing",
#         "positionchanged",
#         "scrambledchanged",
#         "seekablechanged",
#         "snapshottaken",
#         "stopped",
#         "timechanged",
#         "titlechanged",
#         "uncorked",
#         "unmuted",
#         "vout",
#     ]

#     def __init__(self):
#         self.mp = media_player
#         self.signals = []
#         for name in self.signal_names:
#             s = getattr(self.mp, name, None)
#             self.signals.append(s)

#         for s in self.signals:
#             print(s)
#             try:
#                 s.connect(self.print_event_type)
#             except Exception as e:
#                 print(e)

#     # @pyqtSlot(vlc.Event)
#     def print_event_type(self, e):
#         print(e.type())
