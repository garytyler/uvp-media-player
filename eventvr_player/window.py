import logging

import vlc
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QWindow
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
    QVBoxLayout,
    QWidget,
)

from . import display, events, viewpoint

log = logging.getLogger(__name__)


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

    def set_vlc_list_player(self, list_player):
        self.list_player = list_player
        self.media_player = list_player.get_media_player()
        self.position_slider.list_player = self.media_player
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

        self.eventmanager = self.media_player.event_manager()
        self.eventmanager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_end_reached, self.playtimer
        )

    def on_end_reached(self, e, timer):
        self.media_player.set_position(0)
        self.play_button.setText("Play")
        self.is_paused = True

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.media_player.get_position() * 1000)
        self.position_slider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.media_player.is_playing():
            self.playtimer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def stop(self):
        """Stop player
        """
        self.list_player.stop()
        self.play_button.setText("Play")

    def play_pause_button(self):
        """Toggle play/pause status
        """
        if self.list_player.is_playing():
            self.list_player.pause()
            self.play_button.setText("Play")
            self.is_paused = True
            self.playtimer.stop()
        else:
            if self.list_player.play() == -1:
                # Not sure what this does, but I removed open_file() so disabled it for now
                # self.open_file()
                return
            self.list_player.play()
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
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_widget = QWidget(self)
        self.video_widget.setLayout(self.video_layout)
        self.central_layout.addWidget(self.video_widget)

        # Controls layout
        self.time_controls_widget = VideoControls()
        self.central_layout.addWidget(self.time_controls_widget)

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


class PlayerFactory:
    """Temp facade for VLC and Qt objects"""

    vpmanager: viewpoint.ViewpointManager = None
    instance = vlc.Instance()

    def __init__(self, media_paths=None, url=None):
        self.media_paths = media_paths
        self.url = url
        self.player_win = PlayerWindow()
        self.video_frame = display.DisplayFrame(parent=self.player_win)
        self.player_win.video_layout.addWidget(self.video_frame, 0)

        if media_paths:
            self.add_media_paths(media_paths)

    def add_media_paths(self, media_paths):

        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_list(vlc.MediaList(media_paths))

        self.media_player = self.list_player.get_media_player()
        self.video_frame.set_media_player(media_player=self.media_player)

        # Temp
        self.list_events = events.ListSignals(self.list_player)

        self.player_win.time_controls_widget.set_vlc_list_player(self.list_player)
        # self.vpmanager = viewpoint.ViewpointManager(self.list_player, self.url)
