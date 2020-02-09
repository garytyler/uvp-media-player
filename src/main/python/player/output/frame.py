import logging
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QSplitter

# from player.output import fullscreen

log = logging.getLogger(__name__)


class BaseContentFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("output_surface")
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


class MediaPlayerContentFrame(BaseContentFrame):
    def __init__(self, main_win, frame_size_mngr, media_player):
        super().__init__(parent=main_win)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.main_win = main_win
        self.frame_size_mngr = frame_size_mngr
        self.mp = media_player
        self.mp.set_output_widget(self)
        self.content_qsize = QSize()

    def start_fullscreen(self, qscreen):
        self.setParent(None)
        self.setGeometry(qscreen.geometry())
        # TODO: On mac, check if qscreen is main OS screen w/ dock + top bar. If so,
        # use fullscreen instead of maximized.
        if sys.platform == "darwin":
            self.setWindowState(Qt.WindowMaximized)
            self.showMaximized()
        else:
            self.setWindowState(Qt.WindowFullScreen)
            self.showFullScreen()

    def stop_fullscreen(self):
        self.hide()
        self.main_win.setCentralWidget(self)
        self.show()


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
