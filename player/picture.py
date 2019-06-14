import logging
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy

from . import util, vlc_objects

log = logging.getLogger(__name__)


class MediaFrame(QFrame):
    view_scale = 1

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.media = None
        self.new_media_size = True
        self.media_qsize = QSize(600, 360)
        self.set_fill_color(175, 175, 175)

        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mp = vlc_objects.media_player
        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mp.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mp.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mp.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

        self.mp.mediachanged.connect(self.on_mediachanged)

    def get_media_qsize(self):
        if self.new_media_size and self.media:
            w, h = util.get_media_dimensions(self.media)
            self.media_qsize.setWidth(float(w * self.view_scale))
            self.media_qsize.setHeight(float(h * self.view_scale))
            self.new_media_size = False
        return self.media_qsize

    def sizeHint(self):
        """TODO:
        Have given size adhere and adjust to these rules in such a way that the window is not restricted to the '2/3 of screen size' limit. This will involve attaining the current screen size and calculating a given frame size from that?

        https://doc-snapshots.qt.io/qtforpython/PySide2/QtWidgets/QWidget.html?highlight=adjustsize#PySide2.QtWidgets.PySide2.QtWidgets.QWidget.adjustSize
        """
        return self.get_media_qsize()

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)

    def on_mediachanged(self):
        self.media = self.mp.get_media()
        self.new_media_size = True
        self.adjustSize()
