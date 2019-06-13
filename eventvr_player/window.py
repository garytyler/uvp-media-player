import logging

from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QIcon
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

from . import display, util, vlc_objects

log = logging.getLogger(__name__)


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
        self.mp.stopped.connect(self.on_paused)

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

        self.mp.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)
        self.mp.endreached.connect(self.on_endreached)

    def on_endreached(self):
        self.setValue(-1)

    def on_positionchanged(self):
        self.setValue(self.mp.get_position() * self.length)

    def on_mediachanged(self, info):
        media = self.mp.get_media()
        self.fps = util.get_media_fps(media)
        duration_secs = media.get_duration() / 1000
        self.total_frames = duration_secs * self.fps
        self.set_length(self.total_frames)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.connect(self.on_positionchanged)

    def set_length(self, value):
        self.setMinimum(0)
        self.setMaximum(value)
        self.length = self.maximum() - self.minimum()
        self.setTickInterval(1 / self.length)
        self.setTickPosition(QSlider.TicksAbove)

    def get_mouse_pos(self, e):
        slider_min, slider_max = self.minimum(), self.maximum()
        slider_range = slider_max - slider_min
        pos_as_proportion = e.pos().x() / self.width()
        pos_as_slider_val = slider_range * pos_as_proportion + slider_min
        return pos_as_proportion, pos_as_slider_val


class FrameResPositionSlider(PositionSlider):
    def __init__(self, parent):
        super().__init__(parent)
        self.mp.newframe.connect(self.on_newframe)
        self.curr_pos = self.mp_pos = self.mp.get_position()
        self.connect_newframe_on_positionchange = False

    def on_mediachanged(self, info):
        media = self.mp.get_media()
        fps = util.get_media_fps(media)
        duration_secs = media.get_duration() / 1000
        self.total_frames = duration_secs * fps
        self.proportion_per_frame = 1 / self.total_frames
        self.set_length(self.total_frames)
        self.curr_pos = self.mp_pos = self.mp.get_position()

    def on_positionchanged(self):
        self.mp_pos = self.mp.get_position()

        if self.connect_newframe_on_positionchange:
            self.mp.newframe.connect(self.on_newframe)
            self.connect_newframe_on_positionchange = False

    def on_newframe(self):
        if self.mp_pos:
            self.curr_pos = self.mp_pos
            self.mp_pos = None
        else:
            self.curr_pos = self.curr_pos + self.proportion_per_frame
        self.setValue(self.curr_pos * self.length)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.disconnect()
        self.mp.newframe.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)
        self.mp_pos = as_proportion

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)
        self.mp_pos = as_proportion

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.connect_newframe_on_positionchange = True
        self.mp.positionchanged.connect(self.on_positionchanged)


class PlaybackControls(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.media_player = vlc_objects.media_player

        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.position_slider = FrameResPositionSlider(parent=self)
        self.layout.addWidget(self.position_slider, stretch=0)

        self.play_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.play_buttons_layout, stretch=0)

        self.play_button = PlayPauseButton(parent=self)
        self.stop_button = StopButton(parent=self)

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
        # self.media_frame_widget = QWidget(self)
        self.media_frame_widget = display.DisplayFrame(parent=self)
        self.media_frame_layout = QVBoxLayout(self.media_frame_widget)
        self.media_frame_layout.setContentsMargins(0, 0, 0, 0)

        # Controls layout
        self.playback_controls_widget = PlaybackControls()
        self.central_layout.addWidget(self.media_frame_widget, 1)
        self.central_layout.addWidget(self.playback_controls_widget, 0, Qt.AlignBottom)

        # Main window assets
        self.create_shortcuts()
        self.create_menubar()

    def set_window_subtitle(self, subtitle):
        self.app_display_name = self.qapplication.applicationDisplayName()
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
