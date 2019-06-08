"""Viewer class for playing full screen video"""
import logging
import sys
from typing import Optional

import vlc
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QSize, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QPalette, QResizeEvent
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QShortcut,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from . import comm

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

        self.curr_yaw = self.curr_pitch = self.curr_roll = 0

        self.frame_timer = QTimer()
        self.frame_timer.setTimerType(Qt.PreciseTimer)  # Qt.CoarseTimer
        self.frame_timer.setInterval(1000 / 30)  # TODO Use media rate
        self.frame_timer.timeout.connect(self.on_new_frame)

        self.client = comm.RemoteInputClient(url=url)
        self.client.socket.connected.connect(self.frame_timer.start)
        self.client.socket.disconnected.connect(self.frame_timer.stop)

        # self.client.attempt_open_on_interval(url=url)

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
        # self.adjustSize()

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QtGui.QPalette.Window, QtGui.QColor(r, g, b))
        self.setPalette(p)

    def sizeHint(self, *args, **kwargs):
        if self.mediaplayer:
            media_size = self.get_current_media_size()
            if media_size:
                return media_size
        w, h = self.width(), self.height()
        if w >= 200:
            return QSize(w, w / 1.77)
        elif h >= 100:
            return QSize(h, h * 1.77)
        else:
            return QSize(640, 360)

    def get_current_media_size(self) -> Optional[QSize]:
        media = self.mediaplayer.get_media()
        # if not media:
        #     return None
        # el
        if not media.is_parsed():
            media.parse()
        media_tracks = media.tracks_get()
        if not media_tracks:
            return None
        track = [t for t in media_tracks][0]
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


class PositionSlider(QSlider):
    def __init__(self, mediaplayer, parent=None):
        QSlider.__Init__(Qt.Horizontal, parent)

        self.setToolTip("Position")
        self.setMaximum(1000)
        self.sliderMoved.connect(self.set_position)
        self.sliderPressed.connect(self.set_position)


class VideoControls(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.playtimer = QTimer(self)
        self.playtimer.setInterval(100)
        self.playtimer.timeout.connect(self.update_ui)

        # Controls
        self.position_slider = QSlider(Qt.Horizontal, self)
        self.position_slider.setToolTip("Position")
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.sliderPressed.connect(self.set_position)
        self.layout.addWidget(self.position_slider, stretch=0)

        # Player buttons
        self.play_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.play_buttons_layout, stretch=0)

        self.play_button = QPushButton("Play", self)
        self.play_button.setToolTip("Play")
        self.play_button.clicked.connect(self.play_pause_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setToolTip("Stop")
        self.stop_button.clicked.connect(self.stop)

        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.setMaximum(100)
        self.volume_slider.setMinimumWidth(100)
        self.volume_slider.setMaximumWidth(400)

        self.play_buttons_layout.addWidget(self.play_button)
        self.play_buttons_layout.addWidget(self.stop_button)
        self.play_buttons_layout.addStretch(2)
        self.play_buttons_layout.addWidget(QLabel("Volume"))
        self.play_buttons_layout.addWidget(self.volume_slider, stretch=1)

    def set_vlc_media_player(self, mediaplayer):
        self.mediaplayer = mediaplayer
        self.position_slider.mediaplayer = self.mediaplayer
        self.volume_slider.setValue(self.mediaplayer.audio_get_volume())

    def set_position(self):
        """Set the movie position according to the position slider.

        The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        integer variables, so you need a factor; the higher the factor, the
        more precise are the results (1000 should suffice).
        """
        self.playtimer.stop()
        pos = self.position_slider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.playtimer.start()

        self.eventmanager = self.mediaplayer.event_manager()
        self.eventmanager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_end_reached, self.playtimer
        )

    def on_end_reached(self, e, timer):
        self.mediaplayer.set_position(0)
        self.play_button.setText("Play")
        self.is_paused = True

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.position_slider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.playtimer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.play_button.setText("Play")

    def play_pause_button(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_button.setText("Play")
            self.is_paused = True
            self.playtimer.stop()
        else:
            if self.mediaplayer.play() == -1:
                # Not sure what this does, but I removed open_file() so disabled it for now
                # self.open_file()
                return
            self.mediaplayer.play()
            self.play_button.setText("Pause")
            self.playtimer.start()
            self.is_paused = False


class PlayerWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        # Main layout
        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        # Video layout
        self.video_layout = QVBoxLayout()
        # self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_widget = QWidget(self)
        self.video_widget.setLayout(self.video_layout)
        self.central_layout.addWidget(self.video_widget)

        # Controls layout
        # self.time_controls_layout = QVBoxLayout()
        # self.time_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.time_controls_widget = VideoControls()
        # self.time_controls_widget.setLayout(self.time_controls_layout)
        self.central_layout.addWidget(self.time_controls_widget)


class PlayerFactory(PlayerWindow):
    """Temp facade for VLC and Qt objects"""

    vpmanager: ViewpointManager = None

    def __init__(self, media_path=None, url=None):
        PlayerWindow.__init__(self)

        self.frame = MediaFrame(parent=self)
        self.video_layout.addWidget(self.frame, 0)

        if media_path:
            self.mediaplayer = vlc.MediaPlayer(media_path)
            self.vpmanager = ViewpointManager(self.mediaplayer, url)
            self.frame.set_vlc_mediaplayer(self.mediaplayer)
            self.time_controls_widget.set_vlc_media_player(self.mediaplayer)

    def resizeEvent(self, event):
        if self.vpmanager:
            self.vpmanager.trigger_redraw()


# class PlayerWindow(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)

#         # Set window title
#         self.qapplication = QApplication.instance()
#         self.app_display_name = self.qapplication.applicationDisplayName().strip()
#         self.setWindowTitle(self.app_display_name)

#         # Set main layout
#         self.widget = QWidget(self)
#         self.layout = QVBoxLayout()
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.widget.setLayout(self.layout)
#         self.setCentralWidget(self.widget)

#         # Set video layout
#         self.videolayout = QVBoxLayout()
#         self.videowidget = QWidget(self)
#         self.videowidget.setLayout(self.videolayout)
#         self.layout.addWidget(self.videowidget)

#         self.create_shortcuts()
#         self.create_menubar()

#     def set_window_subtitle(self, subtitle):
#         if not subtitle.strip():
#             raise ValueError("set_window_subtitle() requires a str value")
#         if self.app_display_name and bool("python" != self.app_display_name):
#             self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
#         else:
#             self.setWindowTitle(subtitle)

#     def create_menubar(self):
#         self.menubar = QMenuBar()
#         self.setMenuBar(self.menubar)
#         self.menu_file = self.menubar.addMenu("File")

#         # Exit menu action
#         self.action_exit = QAction("Exit", self)
#         self.action_exit.triggered.connect(self.close)
#         self.action_exit.setShortcut("Ctrl+W")
#         self.action_exit.setShortcutContext(Qt.WidgetWithChildrenShortcut)
#         self.menu_file.addAction(self.action_exit)

#         # Fullscreen menu action
#         self.action_fullscreen = QAction("Fullscreen", self)
#         self.action_fullscreen.triggered.connect(self.toggle_fullscreen)
#         self.action_fullscreen.setShortcut("Ctrl+F")
#         self.action_fullscreen.setShortcutContext(Qt.WidgetWithChildrenShortcut)
#         self.menu_file.addAction(self.action_fullscreen)

#     def create_shortcuts(self):
#         self.shortcut_exit = QShortcut("Ctrl+W", self, self.close)
#         self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

#     def move_to_qscreen(self, qscreen=None):
#         """Move qwindow to given qscreen. If no qscreen is given, try to move it to the
#         largest qscreen that is not it's current active qscreen. Call after show()
#         method.
#         """
#         wingeo = self.geometry()
#         if qscreen:
#             targscreen = qscreen
#         elif len(self.qapplication.screens()) <= 1:
#             return
#         else:
#             currscreen = self.qapplication.screenAt(wingeo.center())
#             for s in self.qapplication.screens():
#                 if s is not currscreen:
#                     targscreen = s
#         targpos = targscreen.geometry().center()
#         wingeo.moveCenter(targpos)
#         self.setGeometry(wingeo)

#     def showEvent(self, event):
#         self.move_to_qscreen()

#     def enter_fullscreen(self):
#         try:
#             self.menubar.setVisible(False)
#         except AttributeError:
#             pass
#         self.setWindowState(Qt.WindowFullScreen)

#     def exit_fullscreen(self):
#         try:
#             self.menubar.setVisible(True)
#         except AttributeError:
#             pass
#         self.setWindowState(Qt.WindowNoState)

#     def toggle_fullscreen(self, value=None):
#         is_fullscreen = bool(Qt.WindowFullScreen == self.windowState())
#         if value or not is_fullscreen:
#             self.enter_fullscreen()
#         else:
#             self.exit_fullscreen()
