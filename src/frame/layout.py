import logging
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QStackedLayout

from .. import vlcqt
from ..util import config

log = logging.getLogger(__name__)


class _BaseContentFrame(QFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(parent=main_win)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_qsize = QSize()
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.mp = vlcqt.media_player

    def sizeHint(self):
        self.mp.get_media()
        w, h = self.frame_size_ctrlr.get_current_media_size()
        scale = config.state.view_scale
        self.content_qsize.setWidth(w * scale)
        self.content_qsize.setHeight(h * scale)
        return QSize(w, h)

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)


class _MainContentFrame(_BaseContentFrame):
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


class MainContentFrameLayout(QStackedLayout):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.replacement = _BaseContentFrame(
            main_win=self.main_win, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.insertWidget(1, self.replacement)

    def _new_content_frame(self):
        self.clear_content_frame()
        new_content_frame = _MainContentFrame(
            main_win=self.main_win, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.content_frame = new_content_frame
        self.content_frame.activate()
        self.insertWidget(0, self.content_frame)
        self.setCurrentIndex(0)

    def clear_content_frame(self):
        if hasattr(self, "content_frame"):
            self.content_frame.hide()
            self.removeWidget(self.content_frame)
            del self.content_frame
        if isinstance(self.widget(0), _BaseContentFrame):
            _w = self.widget(0)
            _w.hide()
            self.removeWidget(_w)
            del _w

    def reset_content_frame(self):
        self._new_content_frame()
        self.frame_size_ctrlr.conform_to_media()

    def start_fullscreen(self, qscreen):
        self.insertWidget(1, self.replacement)
        self.setCurrentIndex(1)
        self.content_frame.configure_for_fullscreen(qscreen)

    def stop_fullscreen(self):
        self.content_frame.configure_for_embedded()
        self.insertWidget(0, self.content_frame)
        self.setCurrentIndex(0)
