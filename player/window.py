import logging

import qtawesome as qta
from PyQt5.QtCore import QMetaMethod, QSize, Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QBoxLayout,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from . import picture, util, vlc_objects, vlc_signals

log = logging.getLogger(__name__)


class PlayerControlButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setFlat(True)
        self.set_size(QSize(64, 64))

    def set_size(self, qsize):
        self.setIconSize(qsize)
        self.sizeHint = lambda: qsize


class SkipForwardButton(PlayerControlButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(qta.icon("mdi.skip-forward"))


class SkipBackwardButton(PlayerControlButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(qta.icon("mdi.skip-backward"))


class PlayPauseButton(PlayerControlButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Play")

        self.play_icon = qta.icon("mdi.play")
        self.pause_icon = qta.icon("mdi.pause")

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


class StopButton(PlayerControlButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Stop")
        self.setIcon(qta.icon("mdi.stop"))

        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.mp.stop()


# class PositionSlider(QSlider):
#     def __init__(self, parent):
#         super().__init__(Qt.Horizontal, parent)
#         self.mp = vlc_objects.media_player
#         self.setToolTip("Position")

#         self.mp.mediachanged.connect(self.on_mediachanged)
#         self.mp.positionchanged.connect(self.on_positionchanged)
#         self.mp.endreached.connect(self.on_endreached)

#     def on_endreached(self):
#         self.setValue(-1)

#     def on_positionchanged(self):
#         self.setValue(self.mp.get_position() * self.length)

#     def on_mediachanged(self, info):
#         media = self.mp.get_media()
#         self.fps = util.get_media_fps(media)
#         duration_secs = media.get_duration() / 1000
#         self.total_frames = duration_secs * self.fps
#         self.set_length(self.total_frames)

#     def mousePressEvent(self, e):
#         if e.button() != Qt.LeftButton:
#             return super().mousePressEvent(self, e)
#         e.accept()
#         self.mp.positionchanged.disconnect()
#         as_proportion, as_slider_val = self.get_mouse_pos(e)
#         self.mp.set_position(as_proportion)
#         self.setValue(as_slider_val)

#     def mouseMoveEvent(self, e):
#         e.accept()
#         as_proportion, as_slider_val = self.get_mouse_pos(e)
#         self.mp.set_position(as_proportion)
#         self.setValue(as_slider_val)

#     def mouseReleaseEvent(self, e):
#         if e.button() != Qt.LeftButton:
#             return super().mousePressEvent(self, e)
#         e.accept()
#         self.mp.positionchanged.connect(self.on_positionchanged)

#     def set_length(self, value):
#         self.setMinimum(0)
#         self.setMaximum(value)
#         self.length = self.maximum() - self.minimum()
#         self.setTickInterval(1 / self.length)
#         self.setTickPosition(QSlider.TicksAbove)

#     def get_mouse_pos(self, e):
#         slider_min, slider_max = self.minimum(), self.maximum()
#         slider_range = slider_max - slider_min
#         pos_as_proportion = e.pos().x() / self.width()
#         pos_as_slider_val = slider_range * pos_as_proportion + slider_min
#         return pos_as_proportion, pos_as_slider_val


class FrameResPositionSlider(QSlider):
    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Position")

        self.mp.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)
        self.mp.endreached.connect(self.on_endreached)

        self.newframe_conn = self.mp.newframe.connect(self.on_newframe)
        self.curr_pos = self.mp.get_position()
        self.mp_pos = None
        self.mouse_down = False

    def setValue(self, value):
        if not self.mouse_down:
            super().setValue(value)

    @pyqtSlot()
    def on_endreached(self):
        self.setValue(-1)

    @pyqtSlot()
    def on_mediachanged(self):
        media = self.mp.get_media()
        fps = util.get_media_fps(media)
        duration_secs = media.get_duration() / 1000
        self.total_frames = duration_secs * fps
        self.proportion_per_frame = 1 / self.total_frames
        self.set_length(self.total_frames)
        self.curr_pos = self.mp_pos = self.mp.get_position()

    @pyqtSlot()
    def on_positionchanged(self):
        self.mp_pos = self.mp.get_position()
        self.mouse_down = False

    @pyqtSlot()
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
        self.mouse_down = True
        self.mp.positionchanged.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        super().setValue(as_slider_val)
        self.mp_pos = as_proportion

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.mp_pos = as_proportion
        super().setValue(as_slider_val)

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


class PlaybackSliderComponents(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout = QVBoxLayout(self)
        self.slider = FrameResPositionSlider(parent=self)
        self.layout.addWidget(self.slider)


class PlaybackButtons(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(SkipBackwardButton(parent=self))
        self.layout.addWidget(PlayPauseButton(parent=self))
        self.layout.addWidget(SkipForwardButton(parent=self))


class LeftSideComponents(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)


class RightSideComponents(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)


class LowerComponents(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # self.layout.addLayout(LeftSideComponentsLayout(self), 1, 1)
        # # self.layout.addItem(PlaybackButtons(parent=self), 0, 1)
        # self.layout.addLayout(RightSideComponentsLayout(self), 0, 2)

        self.layout.addWidget(LeftSideComponents(self), 0, 0, Qt.AlignLeft)
        self.layout.addWidget(PlaybackButtons(parent=self), 0, 1, Qt.AlignHCenter)
        self.layout.addWidget(RightSideComponents(self), 0, 2, Qt.AlignRight)

        # self.layout.addWidget(PlaybackButtons(parent=self), Qt.AlignHCenter)

        # self.volume_slider = QSlider(Qt.Horizontal, self)
        # self.volume_slider.setToolTip("Volume")
        # self.volume_slider.setMaximum(100)
        # self.volume_slider.setMinimumWidth(100)
        # self.volume_slider.setMaximumWidth(400)

        # self.buttons_layout.addWidget(PlaybackButtons(parent=self))
        # self.buttons_layout.addStretch(4)
        # self.buttons_layout.addWidget(QLabel("Volume"))
        # self.buttons_layout.addWidget(self.volume_slider, stretch=1)


# class LowerComponents(QWidget):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.layout = QVBoxLayout(self)
#         self.layout.addWidget(FrameResPositionSlider(parent=self))
#         self.layout.addWidget(BottomMenu())


class PlayerWindow(QMainWindow):
    def __init__(self, flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        # Main window assets
        self.create_shortcuts()
        self.create_menubar()

        # Main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        # Video layout
        self.media_frame_widget = picture.MediaFrame(parent=self)
        self.media_frame_layout = QVBoxLayout(self.media_frame_widget)
        self.media_frame_layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.media_frame_widget)
        self.layout.addWidget(PlaybackSliderComponents(parent=self), 1, Qt.AlignBottom)
        self.layout.addWidget(LowerComponents(parent=self), 0, Qt.AlignBottom)

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
