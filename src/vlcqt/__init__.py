from . import vlc_facades
from ffmpeg import probe
from os import path
import sys
import vlc
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFrame
from ..output.frame import MainContentFrame

Instance = vlc_facades.Instance


def set_output_to_widget(media_player, widget):
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

    def set_output_widget(self, widget):
        state = self.get_state()
        time = self.get_time()
        if state in [vlc.State.Buffering, vlc.State.Playing]:
            time = self.get_time()
            self.stop()
            set_output_to_widget(media_player=self, widget=widget)
            self.play()
            self.set_time(time)
        elif state in [vlc.State.Opening]:
            self.stop()
            set_output_to_widget(media_player=self, widget=widget)
            self.play()
        elif state in [vlc.State.Paused]:
            self.stop()
            set_output_to_widget(media_player=self, widget=widget)
            self.play()
            self.set_time(time)
            self.pause()
        elif state in [vlc.State.Ended]:
            self.stop()
            set_output_to_widget(media_player=self, widget=widget)
            self.play()
            self.pause()
            self.set_time(-1)
        elif state in [vlc.State.Stopped, vlc.State.Error, vlc.State.NothingSpecial]:
            self.play()
            set_output_to_widget(media_player=self, widget=widget)
            self.stop()


media_player = MediaPlayer()


# class MediaListPlayer(vlc_facades.MediaListPlayerFacade):
#     def __init__(self):
#         super().__init__()
#         self.mp = media_player
#         self.set_media_player(self.mp)

#     def set_mrls(self, media_paths):
#         self.ml = vlc.MediaList(media_paths)
#         self.set_media_list(self.ml)

#     @pyqtSlot(str)
#     def on_setplaybackmode(self, value):
#         enums = {
#             "off": vlc.PlaybackMode.default,
#             "one": vlc.PlaybackMode.loop,
#             "all": vlc.PlaybackMode.repeat,
#         }
#         self.set_playback_mode(enums[value])


# list_player = MediaListPlayer()


class Media(vlc_facades.MediaFacade):
    """
    Use to get size: vlcqt.libvlc_video_get_size(self.mp, 0)

    """

    def __init__(self, mrl, *options):
        super().__init__(mrl, *options)

    def _parse_with_options(self, parse_flag, timeout):
        # 'parse()' has limited functionality, and does not parse meta data
        # We use async method 'parse_with_options()' for parsing meta data
        self._vlc_obj.parse_with_options(parse_flag, timeout)

    def parse_with_options(self, parse_flag, timeout):
        self.vlc_instance = vlc.Instance()
        self.mp = vlc.MediaPlayer(self.vlc_instance)
        self.frame = QFrame()
        set_output_to_widget(media_player=self.mp, widget=self.frame)
        self.mp.set_media(self)
        self.mp.play()
        connection = self.mediaparsedchanged.connect(self.on_mediaparsedchanged)
        self.mediaparsedchanged_connection = connection
        self._parse_with_options(parse_flag, timeout)

    def on_mediaparsedchanged(self, e):
        self.mediaparsedchanged.disconnect()
        self.mp.stop()
        del self.vlc_instance
        del self.mp
        del self.frame


def __getattr__(attribute):
    try:
        return locals()[attribute]
    except KeyError:
        return vars(vlc)[attribute]
