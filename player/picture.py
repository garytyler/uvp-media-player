import logging
import sys

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy

from . import util, vlc_objects

log = logging.getLogger(__name__)


class MediaFrame(QFrame, QObject):
    mediachanged = pyqtSignal()

    _default_media_h = media_h = 360
    _default_media_w = media_w = 600

    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.main_win = main_win

        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoFillBackground(True)

        self.media = None
        self.media_qsize = QSize(self.media_h, self.media_w)
        self.mp = vlc_objects.media_player

        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mp.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mp.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mp.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

        self.conform_to_current_media()

        self.mp.mediachanged.connect(self.on_mp_mediachanged)

    def on_mp_mediachanged(self):
        self.conform_to_current_media()

    def conform_to_current_media(self):
        self.media = self.mp.get_media()
        if self.media:
            _dimensions = util.get_media_size(self.media)
        else:
            self.media = None
            _dimensions = self._default_media_w, self._default_media_h
        self.media_w, self.media_h = _dimensions
        self.mediachanged.emit()

    def get_media_size(self, zoom: int = 1):
        return self.media_w * zoom, self.media_h * zoom

    def get_media_qsize(self, zoom: int = 1):
        w, h = self.get_media_size(zoom=zoom)
        self.media_qsize.setWidth(w)
        self.media_qsize.setHeight(h)
        return self.media_qsize

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)
