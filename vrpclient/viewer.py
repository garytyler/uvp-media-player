"""Viewer class for playing full screen video"""
import os
import sys
import vlc
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize, QTimer
from PySide2 import QtGui


class VRPWindow(QMainWindow):
    def __init__(self, application_name="VRP Viewer"):
        QMainWindow.__init__(self)
        self.application_name = application_name
        self.setWindowTitle(self.application_name)

        self.create_shortcuts()
        # self.create_menubar()

    def set_window_subtitle(self, subtitle):
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        self.setWindowTitle(f"{self.application_name} - {subtitle}")

    def create_menubar(self):
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        self.menu_file = self.menubar.addMenu("File")

        # Exit menu action
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)
        self.action_exit.setShortcut("Ctrl+W")
        self.action_exit.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.menu_file.addAction(self.action_exit)

        # Fullscreen menu action
        self.action_fullscreen = QAction("Fullscreen", self)
        self.action_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.action_fullscreen.setShortcut("Ctrl+F")
        self.action_fullscreen.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.menu_file.addAction(self.action_fullscreen)

    def create_shortcuts(self):
        self.shortcut_exit = QShortcut("Ctrl+W", self, self.close)
        self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

    def toggle_fullscreen(self):
        raise NotImplementedError


class Viewer(VRPWindow):
    def __init__(self, vlc_media_player):
        VRPWindow.__init__(self)
        self.player = vlc_media_player

        self.create_videoframe()
        self.setCentralWidget(self.videoframe)

        # self.videoframe.sizeHint = lambda: QSize(
        #     self.videoframe.width() * self.track_aspectratio, self.videowidget.width()
        # )

    def create_videoframe(self):
        if sys.platform == "darwin":  # for MacOS
            self.videoframe = QMacCocoaViewContainer(0)
        else:
            self.videoframe = QFrame(self)

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        if sys.platform.startswith("linux"):  # for Linux X Server
            self.player.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.player.set_nsobject(int(self.videoframe.winId()))
        return self.videoframe

    def enter_fullscreen(self):
        try:
            self.menubar.setVisible(False)
        except AttributeError:
            pass
        self.setWindowState(Qt.WindowFullScreen)

    def exit_fullscreen(self):
        try:
            self.menubar.setVisible(True)
        except AttributeError:
            pass
        self.setWindowState(Qt.WindowNoState)

    def toggle_fullscreen(self, value=None):
        """
        Qt.WindowNoState 	The window has no state set (in normal state).
        Qt.WindowMinimized 	The window is minimized (i.e. iconified).
        Qt.WindowMaximized 	The window is maximized with a frame around it.
        Qt.WindowFullScreen 	The window fills the entire screen without any frame around it.
        Qt.WindowActive 	The window is the active window, i.e. it has keyboard focus.
        """
        is_fullscreen = bool(Qt.WindowFullScreen == self.windowState())
        if value or not is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()


def quick_play(path):
    mediaplayer = videolan.media_player_new()
    media = videolan.media_new(path)
    mediaplayer.set_media(media)
    mediaplayer.play()


if __name__ == "__main__":
    MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
    SAMPLE_MEDIA = {
        name: os.path.join(MEDIA_DIR, name) for name in os.listdir(MEDIA_DIR)
    }
    path = SAMPLE_MEDIA["360video_5sec.mp4"]

    app = QApplication(sys.argv)

    videolan = vlc.Instance()
    player = videolan.media_player_new()

    viewer = Viewer(vlc_media_player=player)
    viewer.show()
    player.set_mrl(path)
    player.play()

    sys.exit(app.exec_())
