from . import vlc_facades

# from . import vlc_views
import sys
import vlc
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFrame
from ..frame.layout import MediaPlayerContentFrame

Instance = vlc_facades.Instance


def set_media_player_view_widget(media_player, widget):
    if sys.platform.startswith("linux"):  # for Linux X Server
        media_player.set_xwindow(widget.winId())
    elif sys.platform == "win32":  # for Windows
        media_player.set_hwnd(widget.winId())
    elif sys.platform == "darwin":  # for MacOS
        media_player.set_nsobject(int(widget.winId()))
    else:
        raise EnvironmentError("Could not determine platform")


class MediaPlayer(vlc_facades.MediaPlayerFacade):
    def __init__(self):
        super().__init__()

    def set_view_widget(self, widget):
        set_media_player_view_widget(media_player=self, widget=widget)


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


class Media(vlc_facades.MediaFacade):
    def __init__(self, mrl, *options):
        super().__init__(mrl, *options)

    def _parse_with_options(self, parse_flag, timeout):
        self._vlc_obj.parse_with_options(parse_flag, timeout)

    def parse_with_options(self, parse_flag, timeout):
        self.vlc_instance = vlc.Instance()
        self.mp = vlc.MediaPlayer(self.vlc_instance)
        self.frame = QFrame()
        set_media_player_view_widget(media_player=self.mp, widget=self.frame)
        self.mp.set_media(self)
        self.mp.play()
        connection = self.mediaparsedchanged.connect(self.on_mediaparsedchanged)
        self.mediaparsedchanged_connection = connection
        self._parse_with_options(parse_flag, timeout)

    def on_mediaparsedchanged(self, e):
        self.mediaparsedchanged.disconnect(self.mediaparsedchanged_connection)
        self.mp.stop()
        self.mediaparsedchanged.emit(e)


def __getattr__(attribute):
    try:
        return locals()[attribute]
    except KeyError:
        return vars(vlc)[attribute]
