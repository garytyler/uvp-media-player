import logging

import vlc
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QIcon, QWindow
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QShortcut,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from . import display, events, viewpoint, vlc_facades, vlc_objects

log = logging.getLogger(__name__)


# def set_known_media_pos(self, position):
#     self.known_media_pos = position

# def on_timechanged(self):
#     # media_pos = int(self.mp.get_position() * 1000)
#     self.media_pos = int(self.mp.get_position() * 1000)
#     self.setValue(media_pos)

# def set_position(self):
#     """Set the movie position according to the position slider.

#     The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
#     integer variables, so you need a factor; the higher the factor, the
#     more precise are the results (1000 should suffice).
#     """
#     self.playtimer.stop()
#     pos = self.position_slider.value()
#     self.media_player.set_position(pos / 1000.0)
#     self.playtimer.start()

# def update_ui(self):
#     """Updates the user interface"""

#     # Set the slider's position to its corresponding media position
#     # Note that the setValue function only takes values of type int,
#     # so we must first convert the corresponding media position.
#     media_pos = int(self.media_player.get_position() * 1000)
#     self.position_slider.setValue(media_pos)

#     # No need to call this function if nothing is played
#     if not self.media_player.is_playing():
#         self.playtimer.stop()

#         # After the video finished, the play button stills shows "Pause",
#         # which is not the desired behavior of a media player.
#         # This fixes that "bug".
#         if not self.is_paused:
#             self.stop()


class PlayPauseButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player

        self.setToolTip("Play")

        self.play_icon = QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay))
        self.pause_icon = QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPause))
        self.on_playing() if self.mp.is_playing() else self.on_paused()

        self.clicked.connect(self.on_clicked)
        self.mp.playing.connect(self.on_playing)
        self.mp.paused.connect(self.on_paused)

    def on_clicked(self):
        if self.mp.is_playing():
            self.mp.pause()
        else:
            self.mp.play()

    def on_paused(self):
        self.setIcon(self.play_icon)

    def on_playing(self):
        self.setIcon(self.pause_icon)

    def sizeHint(self):
        return QSize(40, 40)


class StopButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player

        self.setToolTip("Stop")
        self.stop_icon = QIcon(QApplication.style().standardIcon(QStyle.SP_MediaStop))
        self.setIcon(self.stop_icon)

        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.mp.stop()

    def sizeHint(self):
        return QSize(30, 30)


class PositionSlider(QSlider):
    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Position")
        self.mp.mediachangedinfo.connect(self.on_mediachangedinfo)
        self.mp.positionchanged.connect(self.on_positionchanged)

    def on_mediachangedinfo(self, info):
        duration_secs = info["duration_ms"] / 1000
        fps = info["media_fps"]
        total_frames = duration_secs * fps
        self.set_length(total_frames)

    def set_length(self, value):
        self.length = value
        self.setMaximum(self.length)

    def on_positionchanged(self):
        self.setValue(self.mp.get_position() * self.length)

    def _update_pos_from_slider(self):
        """Set the movie position according to the position slider.

        The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        integer variables, so you need a factor; the higher the factor, the
        more precise are the results (1000 should suffice).
        """
        # self.playtimer.stop()
        pos = self.position_slider.value()
        self.media_player.set_position(pos / 1000.0)
        # self.playtimer.start()


class FrameResPositionSlider(PositionSlider):
    def __init__(self, parent):
        super().__init__(parent)
        self.mp.newframe.connect(self.on_newframe)

    def on_mediachangedinfo(self, info):
        duration_secs = info["duration_ms"] / 1000
        fps = info["media_fps"]
        self.total_frames = duration_secs * fps
        self.proportion_per_frame = 1 / self.total_frames
        self.set_length(self.total_frames)
        self.curr_pos = self.mp_pos = self.mp.get_position()

    def on_positionchanged(self):
        self.mp_pos = self.mp.get_position()

    def on_newframe(self):
        if self.mp_pos:
            self.curr_pos = self.mp_pos
            self.mp_pos = None
        else:
            self.curr_pos = self.curr_pos + self.proportion_per_frame
        self.setValue(self.curr_pos * self.length)


class VideoControls(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.playtimer = QTimer(self)
        self.playtimer.setInterval(100)
        # self.playtimer.timeout.connect(self.update_ui)

        # Controls
        # self.position_slider = QSlider(Qt.Horizontal, self)
        # self.position_slider.setToolTip("Position")
        # self.position_slider.setMaximum(1000)
        # self.position_slider.sliderMoved.connect(self.set_position)
        # self.position_slider.sliderPressed.connect(self.set_position)

        self.position_slider = PositionSlider(parent=self)
        # self.position_slider = FrameResPositionSlider(parent=self)
        self.layout.addWidget(self.position_slider, stretch=0)

        # Player buttons
        self.play_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.play_buttons_layout, stretch=0)

        self.play_button = PlayPauseButton(parent=self)
        self.stop_button = StopButton(parent=self)

        # self.stop_button = QPushButton("Stop", self)
        # self.stop_button.setToolTip("Stop")
        # self.stop_button.clicked.connect(self.stop)

        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.setMaximum(100)
        self.volume_slider.setMinimumWidth(100)
        self.volume_slider.setMaximumWidth(400)

        self.play_buttons_layout.addWidget(self.play_button)
        self.play_buttons_layout.addWidget(self.stop_button)
        self.play_buttons_layout.addStretch(4)
        self.play_buttons_layout.addWidget(QLabel("Volume"))
        self.play_buttons_layout.addWidget(self.volume_slider, stretch=1)

    def set_vlc_media_player(self, media_player):
        self.media_player = media_player
        # self.position_slider.media_player = self.media_player
        self.volume_slider.setValue(self.media_player.audio_get_volume())

    def set_position(self):
        """Set the movie position according to the position slider.

        The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        integer variables, so you need a factor; the higher the factor, the
        more precise are the results (1000 should suffice).
        """
        self.playtimer.stop()
        pos = self.position_slider.value()
        self.media_player.set_position(pos / 1000.0)
        self.playtimer.start()

        # self.media_player.endreached.connect(self.on_end_reached, self.playtimer)
        # self.eventmanager = self.media_player.event_manager()
        # self.eventmanager.event_attach(
        #     vlc.EventType.MediaPlayerEndReached, self.on_end_reached, self.playtimer
        # )

    def on_end_reached(self, e, timer):
        self.media_player.set_position(0)
        self.play_button.setText("Play")
        self.is_paused = True

    # def stop(self):
    #     """Stop player
    #     """
    #     self.media_player.stop()
    #     self.play_button.setText("Play")


class PlayerWindow(QMainWindow):
    def __init__(self, flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        # Main layout
        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)

        # Video layout
        self.video_widget = QWidget(self)
        self.video_layout = QVBoxLayout(self.video_widget)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        # Controls layout
        self.controls_widget = VideoControls()
        self.central_layout.addWidget(self.video_widget, 1)
        self.central_layout.addWidget(self.controls_widget, 0, Qt.AlignBottom)

        # Main window assets
        self.create_shortcuts()
        self.create_menubar()

    def set_window_subtitle(self, subtitle):
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        if self.app_display_name and bool("python" != self.app_display_name):
            self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
        else:
            self.setWindowTitle(subtitle)

    def create_shortcuts(self):
        self.shortcut_exit = QShortcut("Ctrl+W", self, self.close)
        self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

    def enter_fullscreen(self):
        self.menubar.setVisible(False)
        self.setWindowState(Qt.WindowFullScreen)

    def exit_fullscreen(self):
        self.menubar.setVisible(True)
        self.setWindowState(Qt.WindowNoState)

    def toggle_fullscreen(self, value=None):
        is_fullscreen = bool(Qt.WindowFullScreen == self.windowState())
        if value or not is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

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
