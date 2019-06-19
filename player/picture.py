import logging
import sys

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy

from . import config, util, vlc_objects

log = logging.getLogger(__name__)


class MediaZoomController(QObject):
    zoomrequest = pyqtSignal(float)

    def __init__(self):
        super().__init__()

    def set_zoom(self, value) -> float:
        config.state.zoom = value
        self.zoomrequest.emit(value)


media_zoomer = MediaZoomController()


class MediaFrame(QFrame, QObject):
    explicitresize = pyqtSignal(int, int)

    _default_media_h = media_h = 360
    _default_media_w = media_w = 600

    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.main_win = main_win

        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoFillBackground(True)

        self.media = None
        self.mp = vlc_objects.media_player
        self.conform_to_current_media()
        self.media_qsize = QSize(self.media_h, self.media_w)

        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mp.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mp.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mp.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

        self.mp.mediachanged.connect(self.on_mp_mediachanged)
        media_zoomer.zoomrequest.connect(self.on_zoomer_zoomrequest)

    @pyqtSlot(float)
    def on_zoomer_zoomrequest(self, value):
        print(value)
        self.explicitresize.emit(self.media_w * value, self.media_h * value)

    def on_mp_mediachanged(self):
        self.conform_to_current_media()

    def conform_to_current_media(self):
        self.media = self.mp.get_media()
        if self.media:
            self.media_w, self.media_h = util.get_media_size(self.media)
        else:
            self.media = None
            self.media_w, self.media_h = self._default_media_w, self._default_media_h

        _zoom = config.state.zoom
        self.explicitresize.emit(self.media_w * _zoom, self.media_h * _zoom)

    def sizeHint(self):
        return self.get_zoomed_media_qsize()

    def get_zoomed_media_size(self):
        _zoom = config.state.zoom if self.mp.has_media else 1
        # _zoom = config.state.zoom
        zoomed_size = self.media_w * _zoom, self.media_h * _zoom
        # print("zoomed_size", zoomed_size)
        return zoomed_size

    def get_zoomed_media_qsize(self):
        w, h = self.get_zoomed_media_size()
        self.media_qsize.setWidth(w)
        self.media_qsize.setHeight(h)
        return self.media_qsize

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)
