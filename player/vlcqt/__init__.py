import sys
from os import path

import vlc
from ffmpeg import probe
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFrame

from ..output.frame import MainContentFrame
from . import vlc_facades

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


class Media(vlc_facades.MediaFacade):
    """Use to get size: vlcqt.libvlc_video_get_size(self.aux_mp, 0)"""

    def __init__(self, mrl, *options):
        super().__init__(mrl, *options)


def __getattr__(attribute):
    try:
        return locals()[attribute]
    except KeyError:
        return vars(vlc)[attribute]
