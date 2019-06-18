import logging

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QShortcut,
    QSpacerItem,
    QWidget,
)

from . import buttons, picture, sliders, user, vlc_objects

log = logging.getLogger(__name__)


class ButtonSet(QWidget):
    def __init__(self, parent, buttons=[]):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        for index, item in enumerate(buttons):
            self.layout.addWidget(item, index)


class MainMenu(QMenu):
    def __init__(self, main_win: QMainWindow):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.setStyleSheet("font-size: 12pt;")

        # Exit
        exit_app = QAction("Exit", self)
        exit_app.triggered.connect(self.main_win.close)
        exit_app.setShortcut("Ctrl+W")
        exit_app.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        # Open file
        open_file = QAction("Open file", self)
        open_file.triggered.connect(self.open_file)
        open_file.setShortcut("Ctrl+O")
        open_file.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        # Stay on top
        stay_on_top = QAction("Stay on top", self)
        stay_on_top.triggered.connect(self.open_file)

        # Fullscreen
        fullscreen = QAction("Fullscreen", self)
        fullscreen.triggered.connect(self.open_file)
        fullscreen.setShortcut("Ctrl+F")
        fullscreen.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        self.addAction(exit_app)
        self.addAction(open_file)
        self.addAction(stay_on_top)
        self.addAction(fullscreen)

    def open_file(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(self, "Open file")
        vlc_objects.media_player.set_mrl(file_path)


class MediaPlayerMainWindow(QMainWindow):
    """Implements a grid layout with a media frame element and functionality for window
    resizing in accordance with media size"""

    def __init__(self, flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())
        self.widget = QWidget(self)
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        self.media_frame = picture.MediaFrame(main_win=self)
        self.media_frame.mediachanged.connect(self.on_media_frame_mediachanged)

    @pyqtSlot()
    def on_media_frame_mediachanged(self):
        self.conform_to_current_media()

    def get_media_adjusted_win_size(self):
        w, h = self.media_frame.get_media_size()
        return w, h + super().sizeHint().height()

    def conform_to_current_media(self):
        _size = self.get_media_adjusted_win_size()
        self.resize(*_size)

    def showEvent(self, e):
        self.conform_to_current_media()

    def sizeHint(self):
        _size = self.get_media_adjusted_win_size()
        return QSize(*_size)


class AppWindow(MediaPlayerMainWindow):
    def __init__(self, flags=None):
        MediaPlayerMainWindow.__init__(self, flags=flags)
        self.mp = vlc_objects.media_player

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        self.create_components()
        self.add_components()

    def create_components(self):
        self.media_frame = picture.MediaFrame(main_win=self)
        self.time_slider = sliders.PlaybackSlider(parent=self)
        self.main_menu = MainMenu(main_win=self)
        self.left_corner = ButtonSet(self)
        self.time_buttons = ButtonSet(
            parent=self,
            buttons=(
                buttons.SkipBackwardButton(parent=self),
                buttons.PlayPauseButton(parent=self),
                buttons.SkipForwardButton(parent=self),
                buttons.PlaybackModeButton(parent=self),
            ),
        )
        self.main_buttons = ButtonSet(
            parent=self,
            buttons=(
                buttons.VolumeButton(parent=self),
                buttons.MainMenuButton(parent=self, main_menu=self.main_menu),
            ),
        )

    def add_components(self):
        self.layout.addWidget(self.media_frame, 0, 0, 1, -1)
        self.layout.setRowStretch(0, 1)
        self.layout.addWidget(self.time_slider, 1, 0, 1, -1)

        # Lower buttons
        self.midside_spacer = QSpacerItem(50, 0)
        self.layout.addWidget(self.left_corner, 2, 0, 1, 1, Qt.AlignLeft)
        self.layout.addItem(self.midside_spacer, 2, 1, 1, 1)
        self.layout.addWidget(self.time_buttons, 2, 2, 1, 1, Qt.AlignHCenter)
        self.layout.addItem(self.midside_spacer, 2, 3, 1, 1)
        self.layout.addWidget(self.main_buttons, 2, 4, 1, 1, Qt.AlignRight)

        # Lower button symmetry
        self.layout.setColumnMinimumWidth(1, self.main_buttons.sizeHint().width())
        self.layout.setColumnMinimumWidth(1, self.left_corner.sizeHint().width())

    def create_shortcuts(self):
        self.shortcut_exit = QShortcut("Ctrl+W", self, self.close)
        # self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

    def set_window_subtitle(self, subtitle):
        self.app_display_name = self.qapplication.applicationDisplayName()
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        if self.app_display_name and bool("python" != self.app_display_name):
            self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
        else:
            self.setWindowTitle(subtitle)
