import logging
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QStackedLayout

from .. import vlcqt

log = logging.getLogger(__name__)


class _BaseMediaFrame(QFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(parent=main_win)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.media_qsize = QSize()
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr

    def sizeHint(self):
        w, h = self.frame_size_ctrlr.get_media_size(scaled=True)
        self.media_qsize.setWidth(w)
        self.media_qsize.setHeight(h)
        return QSize(w, h)

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)


class _MainMediaFrame(_BaseMediaFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(main_win=main_win, frame_size_ctrlr=frame_size_ctrlr)

    def activate(self, mp=None):
        # self.mp = mp if mp else vlcqt.media_player
        self.mp = vlcqt.list_player.get_media_player()
        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mp.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mp.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mp.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

    def configure_for_fullscreen(self, qscreen):
        self.setParent(None)
        self.setWindowState(Qt.WindowFullScreen)  # Lets geo map to non-primary screens
        self.setGeometry(qscreen.geometry())
        self.showFullScreen()

    def configure_for_embedded(self):
        self.setParent(self.main_win)
        self.setWindowState(Qt.WindowNoState)


class MainMediaFrameLayout(QStackedLayout):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.replacement = _BaseMediaFrame(
            main_win=self.main_win, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.insertWidget(1, self.replacement)
        # self.reset_media_frame()
        # self._new_media_frame()

    def _new_media_frame(self):
        self.clear_media_frame()
        new_media_frame = _MainMediaFrame(
            main_win=self.main_win, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.media_frame = new_media_frame
        self.media_frame.activate()
        self.insertWidget(0, self.media_frame)
        self.setCurrentIndex(0)

    def clear_media_frame(self):
        if hasattr(self, "media_frame"):
            self.media_frame.hide()
            self.removeWidget(self.media_frame)
            del self.media_frame
        if isinstance(self.widget(0), _BaseMediaFrame):
            _w = self.widget(0)
            _w.hide()
            self.removeWidget(_w)
            del _w

    def reset_media_frame(self):

        self._new_media_frame()

        self.frame_size_ctrlr.conform_to_media()

    def start_fullscreen(self, qscreen):
        self.insertWidget(1, self.replacement)
        self.setCurrentIndex(1)
        self.media_frame.configure_for_fullscreen(qscreen)

    def stop_fullscreen(self):
        self.media_frame.configure_for_embedded()
        self.insertWidget(0, self.media_frame)
        self.setCurrentIndex(0)
