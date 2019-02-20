"""Viewer class for playing full screen video"""
import os
import sys
import vlc
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QSize, QTimer
from PySide2 import QtGui
from vrpclient import system
from vrpclient import client


class VRPWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.create_shortcuts()
        self.create_menubar()

    def set_window_subtitle(self, subtitle):
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        if self.app_display_name and bool("python" != self.app_display_name):
            self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
        else:
            self.setWindowTitle(subtitle)

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

    def move_to_qscreen(self, qscreen=None):
        """Move qwindow to given qscreen. If not qscreen is given, try to move it to the
        largest qscreen that is not it's current active qscreen. Call after show()
        method.
        """
        wingeo = self.geometry()
        if qscreen:
            targscreen = qscreen
        elif len(self.qapplication.screens()) <= 1:
            return
        else:
            currscreen = self.qapplication.screenAt(wingeo.center())
            for s in self.qapplication.screens():
                if s is not currscreen:
                    targscreen = s
        targpos = targscreen.geometry().center()
        wingeo.moveCenter(targpos)
        self.setGeometry(wingeo)

    def showEvent(self, event):
        self.move_to_qscreen()

    def toggle_fullscreen(self):
        raise NotImplementedError


class MediaFrame(QFrame):
    def __init__(self, player, parent):
        self.parent = parent
        super().__init__(parent=self.parent)
        self.player = player

        self.palette = self.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)

        if sys.platform.startswith("linux"):  # for Linux X Server
            self.player.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.player.set_nsobject(int(self.winId()))

    def current_screen_size(self):
        wincenter = self.geometry().center()
        curscreen = QApplication.instance().screenAt(wincenter)
        screengeo = curscreen.geometry()
        return screengeo.size()

    def size_by_media(self, media):
        details = get_media_details(media)
        if details:
            ar = details["aspect_ratio"]
            return QSize(details["width"], details["height"])

    def sizeHint(self):
        return self.current_screen_size()


class Viewer(VRPWindow):
    def __init__(self, vlc_media_player, fullscreen=True):
        VRPWindow.__init__(self)
        self.player = vlc_media_player

        self.videolayout = QVBoxLayout()
        self.videolayout.setContentsMargins(0, 0, 0, 0)
        self.videowidget = QWidget(self)
        self.videowidget.setLayout(self.videolayout)
        self.layout.addWidget(self.videowidget)

        # Create videoframe
        self.frame = MediaFrame(player=self.player, parent=self.widget)
        self.videolayout.addWidget(self.frame, 0)

        self.toggle_fullscreen(value=fullscreen)

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
        is_fullscreen = bool(Qt.WindowFullScreen == self.windowState())
        if value or not is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

    def current_screen_size(self):
        wincenter = self.geometry().center()
        curscreen = self.qapplication.screenAt(wincenter)
        screengeo = curscreen.geometry()
        return screengeo.size()


def get_media_details(media: vlc.Media) -> dict:
    media.parse()
    track = [t for t in media.tracks_get()][0].video
    return {
        "framerate": track.contents.frame_rate_num,
        "width": track.contents.width,
        "height": track.contents.height,
        "aspect_ratio": track.contents.width / track.contents.height,
    }


def play(path):
    try:
        client.connect()
    except Exception as e:
        print(e)
    app = QApplication(sys.argv)
    videolan = vlc.Instance()
    player = videolan.media_player_new()
    viewer = Viewer(vlc_media_player=player)
    viewer.show()
    player.set_mrl(path)
    player.play()
    sys.exit(app.exec_())


if __name__ == "__main__":
    MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
    SAMPLE_MEDIA = {
        name: os.path.join(MEDIA_DIR, name) for name in os.listdir(MEDIA_DIR)
    }
    path = SAMPLE_MEDIA["360video_5sec.mp4"]
    play(path)
