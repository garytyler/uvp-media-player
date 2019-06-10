import logging
import sys
from typing import Optional

import vlc
from PyQt5.QtCore import QObject, QSize
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame

log = logging.getLogger(__name__)


class DisplayFrame(QFrame, QObject):
    media_player: vlc.MediaListPlayer = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.set_fill_color(150, 150, 150)
        # self.adjustSize()

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)

    def sizeHint(self, *args, **kwargs):
        if self.media_player:
            media_size = self.get_current_media_size()
            if media_size:
                return media_size
        w, h = self.width(), self.height()
        if w >= 200:
            return QSize(w, w / 1.77)
        elif h >= 100:
            return QSize(h, h * 1.77)
        else:
            return QSize(640, 360)

    def get_current_media_size(self) -> Optional[QSize]:
        media = self.media_player.get_media()
        if not media:
            return None
        if not media.is_parsed():
            media.parse()
        media_tracks = media.tracks_get()
        if not media_tracks:  # Possibly not necessary. Does all media have a track?
            return None
        track = [t for t in media_tracks][0]
        return QSize(track.video.contents.width, track.video.contents.height)

    def set_media_player(self, media_player):
        self.media_player = media_player

        if sys.platform.startswith("linux"):  # for Linux X Server
            self.media_player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.media_player.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

        self.set_fill_color(0, 0, 0)
