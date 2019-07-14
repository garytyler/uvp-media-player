import logging
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QStackedLayout

from .. import vlcqt
from ..util import config

log = logging.getLogger(__name__)


def set_widget_as_media_player_view(media_player, widget):
    if sys.platform.startswith("linux"):  # for Linux X Server
        media_player.set_xwindow(widget.winId())
    elif sys.platform == "win32":  # for Windows
        media_player.set_hwnd(widget.winId())
    elif sys.platform == "darwin":  # for MacOS
        media_player.set_nsobject(int(widget.winId()))
    else:
        raise EnvironmentError("Could not determine platform")


class BaseContentFrame(QFrame):
    def __init__(self, window, frame_size_ctrlr):
        super().__init__(parent=window)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_qsize = QSize()
        self.window = window
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


class MediaPlayerContentFrame(BaseContentFrame):
    def __init__(self, window, frame_size_ctrlr):
        super().__init__(window=window, frame_size_ctrlr=frame_size_ctrlr)

    def activate(self, mp=None):
        self.mp = mp if mp else vlcqt.media_player
        self.mp.set_view_widget(self)

    def configure_for_fullscreen(self, qscreen):
        self.setwindow(None)
        self.setWindowState(Qt.WindowFullScreen)  # Lets geo map to non-primary screens
        self.setGeometry(qscreen.geometry())
        self.showFullScreen()

    def configure_for_embedded(self):
        self.setwindow(self.window)
        self.setWindowState(Qt.WindowNoState)


class MainContentFrameLayout(QStackedLayout):
    def __init__(self, window, frame_size_ctrlr):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.window = window
        self.frame_size_ctrlr = frame_size_ctrlr
        self.filler_frame = BaseContentFrame(
            window=self.window, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.insertWidget(1, self.filler_frame)

    def _new_content_frame(self):
        self.clear_content_frame()
        new_mp_content_frame = MediaPlayerContentFrame(
            window=self.window, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.mp_content_frame = new_mp_content_frame
        self.mp_content_frame.activate()
        self.insertWidget(0, self.mp_content_frame)
        self.setCurrentIndex(0)

    def clear_content_frame(self):
        if hasattr(self, "content_frame"):
            self.mp_content_frame.hide()
            self.removeWidget(self.mp_content_frame)
            del self.mp_content_frame
        if isinstance(self.widget(0), BaseContentFrame):
            _w = self.widget(0)
            _w.hide()
            self.removeWidget(_w)
            del _w

    def reset_content_frame(self):
        self._new_content_frame()
        self.frame_size_ctrlr.conform_to_media()

    def start_fullscreen(self, qscreen):
        self.insertWidget(1, self.filler_frame)
        self.setCurrentIndex(1)
        self.mp_content_frame.configure_for_fullscreen(qscreen)

    def stop_fullscreen(self):
        self.mp_content_frame.configure_for_embedded()
        self.insertWidget(0, self.mp_content_frame)
        self.setCurrentIndex(0)
