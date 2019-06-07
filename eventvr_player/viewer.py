"""Viewer class for playing full screen video"""
import logging
import sys
from typing import Optional

import vlc
from eventvr_player import comm
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QSize, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QPalette, QResizeEvent
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QMainWindow,
    QMenuBar,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

"""
player.get_state()

{0: 'NothingSpecial',
 1: 'Opening',
 2: 'Buffering',
 3: 'Playing',
 4: 'Paused',
 5: 'Stopped',
 6: 'Ended',
 7: 'Error'}

"""


log = logging.getLogger(__name__)


def get_media_dimensions(media: vlc.Media) -> dict:
    if not media.is_parsed():
        media.parse()
    track = [t for t in media.tracks_get()][0]
    return {
        "framerate": track.video.contents.frame_rate_num,
        "width": track.video.contents.width,
        "height": track.video.contents.height,
        "aspect_ratio": track.video.contents.width / track.video.contents.height,
    }


def get_media_size(media: vlc.Media) -> QSize:
    details = get_media_dimensions(media)
    if details:
        return QSize(details["width"], details["height"])


class ViewpointManager:
    """Handles setting viewpoint in VLC media player object. Uses Qt only for timer."""

    def __init__(self, mediaplayer, url):

        self.mediaplayer = mediaplayer

        self.frame_timer = QTimer()
        self.frame_timer.setTimerType(Qt.PreciseTimer)  # Qt.CoarseTimer
        self.frame_timer.setInterval(1000 / 30)  # TODO Use media rate
        self.frame_timer.timeout.connect(self.on_new_frame)

        self.client = comm.RemoteInputClient(url=url)
        self.client.socket.connected.connect(self.frame_timer.start)
        self.client.socket.disconnected.connect(self.frame_timer.stop)

        self.curr_yaw = self.curr_pitch = self.curr_roll = 0

    def on_new_frame(self):
        new_motion_state = self.client.get_new_motion_state()
        if new_motion_state:
            self.set_new_viewpoint(*new_motion_state)

    def set_new_viewpoint(self, yaw, pitch, roll):
        self.vp = vlc.VideoViewpoint()
        self.vp.field_of_view = 80
        self.vp.yaw, self.vp.pitch, self.vp.roll = yaw, pitch, roll
        errorcode = self.mediaplayer.video_update_viewpoint(
            p_viewpoint=self.vp, b_absolute=True
        )
        if errorcode != 0:
            log.error("Error setting viewpoint")

    def trigger_redraw(self):
        """Force an if-needed reset of the pixel aspect ratio of a 360 video frame.

        This is triggered by a hacky solution of setting a new viewpoint that has an
        unobservably minimal value differential.
        """
        differential = 0.01 ** 20  # (0.01 ** 22) is max effective differential
        self.set_new_viewpoint(
            self.curr_yaw + differential, self.curr_pitch, self.curr_roll
        )


class MediaFrame(QFrame, QObject):
    mediaplayer: vlc.MediaPlayer = None

    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent=self.parent)
        self.setAutoFillBackground(True)
        self.set_fill_color(150, 150, 150)
        self.adjustSize()

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, QtGui.QColor(r, g, b))
        self.setPalette(p)

    def sizeHint(self, *args, **kwargs):
        if self.mediaplayer:
            return self.get_current_media_size()
        w, h = self.width(), self.height()
        if w >= 200:
            return QSize(w, w / 1.77)
        elif h >= 100:
            return QSize(h, h * 1.77)
        else:
            return QSize(640, 360)

    def get_current_media_size(self) -> QSize:
        media = self.mediaplayer.get_media()
        if not media.is_parsed():
            media.parse()
        track = [t for t in media.tracks_get()][0]
        return QSize(track.video.contents.width, track.video.contents.height)

    def set_vlc_mediaplayer(self, mediaplayer):
        self.mediaplayer = mediaplayer
        if sys.platform.startswith("linux"):  # for Linux X Server
            self.mediaplayer.set_xwindow(self.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

        self.set_fill_color(0, 0, 0)

        # TODO Move to a button
        self.mediaplayer.play()


class PlayerWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        # Set main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Set video layout
        self.videolayout = QVBoxLayout()
        # self.videolayout.setContentsMargins(0, 0, 0, 0)
        self.videowidget = QWidget(self)
        self.videowidget.setLayout(self.videolayout)
        self.layout.addWidget(self.videowidget)

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
        """Move qwindow to given qscreen. If no qscreen is given, try to move it to the
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


class PlayerFactory(PlayerWindow):
    """Incorporates a mediaplayer object and implements methods that depend on it"""

    """Facade for VLC and Qt objects"""

    vpmanager: ViewpointManager = None

    def __init__(self, mediaplayer=None, url=None):
        PlayerWindow.__init__(self)
        self.frame = MediaFrame(parent=self)
        self.videolayout.addWidget(self.frame, 0)

        if mediaplayer:
            self.vpmanager = ViewpointManager(mediaplayer, url)
            self.frame.set_vlc_mediaplayer(mediaplayer)

    def resizeEvent(self, event):
        if self.vpmanager:
            self.vpmanager.trigger_redraw()
