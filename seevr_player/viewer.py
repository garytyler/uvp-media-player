"""Viewer class for playing full screen video"""
import os
import sys
import vlc
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5 import QtGui
import system, comm

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


def get_media_size(media: vlc.Media) -> QSize:
    details = get_media_details(media)
    if details:
        return QSize(details["width"], details["height"])


def get_media_details(media: vlc.Media) -> dict:
    if not media.is_parsed():
        media.parse()
    track = [t for t in media.tracks_get()][0]
    return {
        "framerate": track.video.contents.frame_rate_num,
        "width": track.video.contents.width,
        "height": track.video.contents.height,
        "aspect_ratio": track.video.contents.width / track.video.contents.height,
    }


class ViewpointManager(comm.ClientConnectionBase):
    def __init__(self, mediaplayer, url):
        comm.ClientConnectionBase.__init__(self, url)
        self.mediaplayer = mediaplayer

        self.curr_yaw = self.curr_pitch = self.curr_roll = 0
        self.latest_data = None

        self.frame_timer = QTimer()
        self.frame_timer.setTimerType(Qt.PreciseTimer)  # Qt.CoarseTimer
        self.frame_timer.setInterval(1000 / 30)  # TODO Use media rate
        self.frame_timer.timeout.connect(self.on_new_frame)

    def received(self, data):
        print(f"Latest: {data}", flush=True)
        self.latest_data = data

    def connected(self):
        self.connect_timer.stop()
        self.frame_timer.start()

    def disconnected(self):
        self.frame_timer.stop()

    def on_new_frame(self, coordtype="gn_euler"):
        if self.latest_data:
            self.set_new_viewpoint(
                yaw=-self.latest_data[coordtype]["alpha"],
                pitch=-self.latest_data[coordtype]["beta"],
                roll=-self.latest_data[coordtype]["gamma"],
            )

    def set_new_viewpoint(self, yaw, pitch, roll, coordtype="gn_euler"):
        if (yaw, pitch, roll) == (self.curr_yaw, self.curr_pitch, self.curr_roll):
            return

        self.vp = vlc.VideoViewpoint()
        self.vp.field_of_view = 80
        self.vp.yaw = self.curr_yaw = yaw
        self.vp.pitch = self.curr_pitch = pitch
        self.vp.roll = self.curr_roll = roll
        errorcode = self.mediaplayer.video_update_viewpoint(
            p_viewpoint=self.vp, b_absolute=True
        )
        if errorcode != 0:
            raise RuntimeError("Error setting viewpoint")
        return errorcode


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

    def sizeHint(self, *args, **kwargs):
        media = self.player.get_media()
        details = get_media_details(media)
        return QSize(details["width"], details["height"])


class _ViewerWindow(QMainWindow):
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
        self.videolayout.setContentsMargins(0, 0, 0, 0)
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


class VRPViewer(_ViewerWindow):
    """Incorporates a player object and implements methods that depend on it"""

    """Facade for VLC and Qt objects"""

    def __init__(self, player, url):
        _ViewerWindow.__init__(self)

        self.player = player
        self.vpmanager = ViewpointManager(self.player, url)

        # Create videoframe add add to video layout
        self.frame = MediaFrame(player=self.player, parent=self.widget)
        self.videolayout.addWidget(self.frame, 0)

        self.show()

    def update_360_aspect_ratio(self):
        """Force an if-needed reset of the pixel aspect ratio of a 360 video frame.

        This is triggered by a hacky solution of setting a new viewpoint that has an
        unobservably minimal value differential.
        """
        differential = 0.01 ** 20  # (0.01 ** 22) is max effective differential
        self.vpmanager.set_new_viewpoint(
            self.vpmanager.curr_yaw + differential,
            self.vpmanager.curr_pitch,
            self.vpmanager.curr_roll,
        )

    def resizeEvent(self, event):
        self.update_360_aspect_ratio()

    def play(self):
        self.player.play()
        self.update_360_aspect_ratio()


def play(path, url, args=["--no-qt-privacy-ask"]):
    app = QApplication(sys.argv)

    mediaplayer = vlc.MediaPlayer(path)
    viewer = VRPViewer(mediaplayer, url)
    viewer.play()

    sys.exit(app.exec_())


if __name__ == "__main__":
    MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
    SAMPLE_MEDIA = {
        name: os.path.join(MEDIA_DIR, name) for name in os.listdir(MEDIA_DIR)
    }
    path = SAMPLE_MEDIA["360video_2min.mp4"]
    url = "wss://seevr.herokuapp.com/player"
    # url = "ws://127.0.0.1:5000/player"
    play(path, url)
