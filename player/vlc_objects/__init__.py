from . import vlc_facades
from player import user
import vlc
from PyQt5.QtCore import pyqtSlot

Instance = vlc_facades.Instance


class MediaPlayer(vlc_facades.MediaPlayerFacade):
    def __init__(self):
        super().__init__()
        self.stopped.connect(self.stop)
        # self.endreached.connect(self.stop)
        # self.stopped.connect(self.stop)


media_player = MediaPlayer()


class MediaListPlayer(vlc_facades.MediaListPlayerFacade):
    def __init__(self):
        super().__init__()
        self.mp = media_player
        self.set_media_player(self.mp)

    def set_mrls(self, media_paths):
        self.ml = vlc.MediaList(media_paths)
        self.set_media_list(self.ml)

    @pyqtSlot(str)
    def on_setplaybackmode(self, value):
        enums = {
            "off": vlc.PlaybackMode.default,
            "one": vlc.PlaybackMode.loop,
            "all": vlc.PlaybackMode.repeat,
        }
        self.set_playback_mode(enums[value])


list_player = MediaListPlayer()
