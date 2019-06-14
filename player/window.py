import logging

import qtawesome
from PyQt5.QtCore import QPoint, QSize, Qt, pyqtSlot
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
    QMenu,
    QMenuBar,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSlider,
    QStyle,
    QStyleOption,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import picture, util, vlc_objects

log = logging.getLogger(__name__)


class SquareIconPushButton(QPushButton):
    def __init__(self, parent, size: int = 64):
        super().__init__(parent=parent)
        self.setFlat(True)
        qsize = QSize(size, size)
        self.setIconSize(qsize)
        self.sizeHint = lambda: qsize


class SquareIconToolButton(QToolButton):
    def __init__(self, parent, size: int = 64):
        super().__init__(parent=parent)
        # self.setFlat(True)
        # self.setArrowType(Qt.NoArrow)
        # self.setPopupMode(QToolButton.DelayedPopup)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        qsize = QSize(size, size)
        self.setIconSize(qsize)
        self.sizeHint = lambda: qsize


class SkipForwardButton(SquareIconPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(qtawesome.icon("mdi.skip-forward"))


class SkipBackwardButton(SquareIconPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setIcon(qtawesome.icon("mdi.skip-backward"))


class PlayPauseButton(SquareIconPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Play")

        self.play_icon = qtawesome.icon("mdi.play")
        self.pause_icon = qtawesome.icon("mdi.pause")

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


class StopButton(SquareIconPushButton):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Stop")
        self.setIcon(qtawesome.icon("mdi.stop"))

        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.mp.stop()


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

    def get_mouse_pos(self, e):
        slider_min, slider_max = self.minimum(), self.maximum()
        slider_range = slider_max - slider_min
        pos_as_proportion = e.pos().x() / self.width()
        pos_as_slider_val = slider_range * pos_as_proportion + slider_min
        return pos_as_proportion, pos_as_slider_val


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


class PlaybackSlider(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout = QVBoxLayout(self)
        self.slider = FrameResPositionSlider(parent=self)
        self.layout.addWidget(self.slider)


class ButtonSet(QWidget):
    def __init__(self, parent, buttons=[]):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.layout = QHBoxLayout(self)

        for index, item in enumerate(buttons):
            self.layout.addWidget(item, index)


class VolumeSlider(QSlider):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip("Volume")
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())

    def set_volume(self, value):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(value)
        self.volumeslider.setValue(value)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())


class VolumeButton(SquareIconPushButton):
    """
    "mdi.volume-low"
    "mdi.volume-medium"
    "mdi.volume-high"

    "mdi.volume-minus"
    "mdi.volume-plus"

    "mdi.volume-mute"
    "mdi.volume-off"
    """

    def __init__(self, parent):
        super().__init__(parent=parent, size=48)
        self.setIcon(qtawesome.icon("mdi.volume-off"))


class MainMenuButton(SquareIconPushButton):
    def __init__(self, main_menu: QMenu, parent):
        super().__init__(parent=parent)
        self.setIcon(qtawesome.icon("mdi.dots-vertical"))
        self.main_menu = main_menu
        self.clicked.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.main_menu.sizeHint()
        x = self.pos().x() - menu_size.width()
        y = self.pos().y() - menu_size.height()
        self.main_menu.popup(self.mapToGlobal(QPoint(x, y)))


class MainMenu(QMenu):
    def __init__(self, main_win: QMainWindow):
        super().__init__(parent=main_win)
        # qtawesome.load_font("fontawesome5-regular-webfont.ttf")
        self.main_win = main_win

        # Exit menu action
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.main_win.close)
        self.action_exit.setShortcut("Ctrl+W")
        self.action_exit.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.addAction(self.action_exit)

        # Fullscreen menu action
        self.action_fullscreen = QAction("Fullscreen", self)
        # self.action_fullscreen.triggered.connect(self.main_win.toggle_fullscreen)
        self.action_fullscreen.setShortcut("Ctrl+F")
        self.action_fullscreen.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        # self.addAction(self.action_fullscreen)


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

        # Add a main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        # Upper layout
        self.upper_layout = QVBoxLayout()
        self.upper_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.upper_layout)

        # Upper components
        self.upper_layout.addWidget(picture.MediaFrame(parent=self))
        self.upper_layout.addWidget(PlaybackSlider(parent=self), 1, Qt.AlignBottom)

        # Lower layout
        self.lower_layout = QGridLayout()
        self.lower_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.lower_layout)

        playback_buttons = (
            SkipBackwardButton(parent=self),
            PlayPauseButton(parent=self),
            SkipForwardButton(parent=self),
        )
        self.playback_button_set = ButtonSet(parent=self, buttons=playback_buttons)

        main_buttons = (
            VolumeButton(parent=self),
            MainMenuButton(main_menu=MainMenu(main_win=self), parent=self),
        )
        self.main_button_set = ButtonSet(parent=self, buttons=main_buttons)

        self.lower_layout.addWidget(QWidget(self), 0, 0, Qt.AlignLeft)
        self.lower_layout.addWidget(self.playback_button_set, 0, 1, Qt.AlignHCenter)
        self.lower_layout.addWidget(self.main_button_set, 0, 2, Qt.AlignRight)

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
        # self.action_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.action_fullscreen.setShortcut("Ctrl+F")
        self.action_fullscreen.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.menu_file.addAction(self.action_fullscreen)

    def create_shortcuts(self):
        self.shortcut_exit = QShortcut("Ctrl+W", self, self.close)
        # self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)
