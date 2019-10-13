import logging

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QSplitter, QStackedLayout

import vlcqt

log = logging.getLogger(__name__)


class BaseContentFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("output_surface")
        self.mp = vlcqt.media_player
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.black_color = QColor(0, 0, 0)
        self.fill_black()

    def fill_black(self):
        p = self.palette()
        p.setColor(QPalette.Window, self.black_color)
        self.setPalette(self.palette())

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)


class FullscreenContentFrame(BaseContentFrame):
    def __init__(self, qscreen):
        super().__init__(parent=None)
        self.setWindowState(Qt.WindowFullScreen)  # Lets geo map to non-primary screens
        self.setGeometry(qscreen.geometry())
        self.showFullScreen()
        self.mp.set_output_widget(self)


class MediaPlayerContentFrame(BaseContentFrame):
    def __init__(self, main_win, frame_size_mngr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_mngr = frame_size_mngr
        self.mp = vlcqt.media_player
        self.mp.set_output_widget(self)
        self.content_qsize = QSize()

    def start_fullscreen(self, qscreen):
        self.setParent(None)
        self.setWindowState(Qt.WindowFullScreen)  # Lets geo map to non-primary screens
        self.setGeometry(qscreen.geometry())
        self.showFullScreen()

    def stop_fullscreen(self):
        self.hide()
        self.main_win.setCentralWidget(self)
        self.show()


class MainContentFrame(QFrame):
    def __init__(self, main_win, frame_size_mngr):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(QStackedLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.main_win = main_win
        self.frame_size_mngr = frame_size_mngr
        self.filler_frame = BaseContentFrame(parent=self.main_win)
        self.layout().insertWidget(1, self.filler_frame)
        self.filler_frame.hide()
        self._new_mp_content_frame()

    def _new_mp_content_frame(self):
        self.clear_main_content_frame()
        new_mp_content_frame = MediaPlayerContentFrame(
            main_win=self.main_win, frame_size_mngr=self.frame_size_mngr
        )
        self.mp_content_frame = new_mp_content_frame
        self.layout().insertWidget(0, self.mp_content_frame)
        self.layout().setCurrentIndex(0)

    def clear_main_content_frame(self):
        if hasattr(self, "main_content_frame"):
            self.mp_content_frame.hide()
            self.layout().removeWidget(self.mp_content_frame)
            del self.mp_content_frame
        if isinstance(self.layout().widget(0), BaseContentFrame):
            _w = self.layout().widget(0)
            _w.hide()
            self.layout().removeWidget(_w)
            del _w

    def reset_main_content_frame(self):
        self._new_mp_content_frame()
        self.frame_size_mngr.conform_to_media()

    def start_fullscreen(self, qscreen):
        self.fs_frame = FullscreenContentFrame(qscreen)
        self.fs_frame.show()
        self.layout().setCurrentIndex(1)

    def stop_fullscreen(self):
        self.fs_frame.hide()
        self.layout().setCurrentIndex(0)
        del self.fs_frame


class SplitView(QSplitter):
    def __init__(self, playlist_editor, main_content_frame, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.playlist_editor = playlist_editor
        self.main_content_frame = main_content_frame
        self.setStretchFactor(0, 0)

        self.insertWidget(0, self.playlist_editor)
        self.setStretchFactor(1, 1)

        self.insertWidget(1, self.main_content_frame)
        self.orig_state = self.saveState()

    def toggle_playlist(self, value):

        for n in range(self.count()):
            w = self.widget(n)
            if w:
                w.setParent(None)
        if value:
            self.insertWidget(0, self.playlist_editor)
            self.insertWidget(1, self.main_content_frame)
            self.moveSplitter(self.playlist_editor.sizeHint().width(), 0)
        else:
            self.insertWidget(0, self.main_content_frame)
            self.moveSplitter(0, 0)
        self.main_content_frame.reset_main_content_frame()
