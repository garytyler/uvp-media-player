import logging
import sys

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QAction, QFrame, QSizePolicy, QVBoxLayout, QWidget

from . import vlcqt

log = logging.getLogger(__name__)


class BaseMediaFrame(QFrame):
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


class MainMediaFrame(BaseMediaFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(main_win=main_win, frame_size_ctrlr=frame_size_ctrlr)

    def activate(self):
        self.mp = vlcqt.media_player
        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mp.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mp.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mp.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

    def start_fullscreen(self, qscreen):
        self.setVisible(False)
        self.setParent(None)
        wingeo = self.geometry()
        targetgeo = qscreen.geometry()
        wingeo.moveCenter(targetgeo.center())
        self.setGeometry(wingeo)
        self.showFullScreen()
        self.setWindowState(Qt.WindowFullScreen)
        self.setVisible(True)

    def stop_fullscreen(self):
        self.setVisible(False)
        self.setParent(self.main_win)
        self.setWindowState(Qt.WindowNoState)
        self.setVisible(True)


class MainMediaFrameLayout(QVBoxLayout):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__()
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.media_frame = MainMediaFrame(
            main_win=self.main_win, frame_size_ctrlr=frame_size_ctrlr
        )
        self.addWidget(self.media_frame)
        self.media_frame.activate()
        self.replacement = BaseMediaFrame(
            main_win=self.main_win, frame_size_ctrlr=frame_size_ctrlr
        )

    def start_fullscreen_media_frame(self, qscreen):
        self.replacement.hide()
        self.replaceWidget(self.media_frame, self.replacement)
        self.replacement.show()
        self.media_frame.start_fullscreen(qscreen)

    def stop_fullscreen_media_frame(self):
        self.media_frame.stop_fullscreen()
        self.media_frame.hide()
        self.replaceWidget(self.replacement, self.media_frame)
        self.media_frame.show()


class FullscreenController(QObject):
    fullscreenstarted = pyqtSignal(QAction)
    fullscreenstopped = pyqtSignal()

    def __init__(self, mf_layout):
        super().__init__()
        self.mf_layout = mf_layout
        self.replacement = QWidget()

    def start(self, action):
        qscreen = action.qscreen
        self.mf_layout.start_fullscreen_media_frame(qscreen)
        self.fullscreenstarted.emit(action)

    def stop(self):
        self.mf_layout.stop_fullscreen_media_frame()
        self.fullscreenstopped.emit()
