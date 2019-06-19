import logging
from os.path import exists

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QShortcut,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from . import actions, buttons, config, picture, sliders, util, vlc_objects

log = logging.getLogger(__name__)


class MenuBase(QMenu):
    style_sheet = "font-size: 12pt;"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setStyleSheet(self.style_sheet)
        self.mp = vlc_objects.media_player


class ButtonBunch(QWidget):
    def __init__(self, parent, buttons=[]):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        for index, item in enumerate(buttons):
            self.layout.addWidget(item, index)


class MainMenu(MenuBase):
    def __init__(self, main_win: QMainWindow):
        super().__init__(parent=main_win)
        self.main_win = main_win

        # Open file
        self.open_file = QAction("Open file", self)
        self.open_file.triggered.connect(self._open_file)
        self.open_file.setShortcut("Ctrl+O")
        self.open_file.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.open_file.setShortcutVisibleInContextMenu(True)

        self.addAction(self.open_file)
        self.addMenu(actions.ZoomMenu(main_win=main_win))
        self.addAction(actions.StayOnTop(main_win=main_win))

    def _open_file(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(self, "Open file")
        if exists(file_path):
            vlc_objects.media_player.set_mrl(file_path)


class AppWindow(QMainWindow):
    initialized = pyqtSignal()

    def __init__(self, flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())
        self.qapp = QApplication.instance()
        self.mp = vlc_objects.media_player

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        self.create_components()
        self.add_components()

        self.media_frame.explicitresize.connect(self.on_explicitresize)

        self.initialized.emit()

    def create_components(self):
        self.media_frame = picture.MediaFrame(main_win=self)
        self.time_slider = sliders.PlaybackSlider(parent=self)
        self.main_menu = MainMenu(main_win=self)
        self.left_corner = ButtonBunch(self)
        self.time_buttons = ButtonBunch(
            parent=self,
            buttons=(
                buttons.SkipBackwardButton(parent=self, size=48),
                buttons.PlayPauseButton(parent=self, size=48),
                buttons.SkipForwardButton(parent=self, size=48),
            ),
        )
        self.main_buttons = ButtonBunch(
            parent=self,
            buttons=(
                buttons.PlaybackModeButton(parent=self, size=32),
                buttons.VolumeButton(parent=self, size=32),
                buttons.MainMenuButton(parent=self, size=48, main_menu=self.main_menu),
            ),
        )

    def add_components(self):
        # Main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        # Media frame
        self.layout.addWidget(self.media_frame, 1)

        # Controls layout
        self.ctrls_widget = QWidget(self)
        self.ctrls_layout = QGridLayout(self.ctrls_widget)
        self.ctrls_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ctrls_widget, 0)

        # Control components
        self.ctrls_layout.addWidget(self.time_slider, 0, 0, 1, -1)
        self.midside_spacer = QSpacerItem(20, 0)
        self.ctrls_layout.addWidget(self.left_corner, 1, 0, 1, 1, Qt.AlignLeft)
        self.ctrls_layout.addItem(self.midside_spacer, 1, 1, 1, 1)
        self.ctrls_layout.addWidget(self.time_buttons, 1, 2, 1, 1, Qt.AlignHCenter)
        self.ctrls_layout.addItem(self.midside_spacer, 1, 3, 1, 1)
        self.ctrls_layout.addWidget(self.main_buttons, 1, 4, 1, 1, Qt.AlignRight)

        self.ctrls_layout.setColumnStretch(2, 1)
        self.ctrls_layout.setColumnMinimumWidth(0, self.main_buttons.sizeHint().width())
        self.ctrls_layout.setColumnMinimumWidth(4, self.left_corner.sizeHint().width())

    # def create_window_shortcuts(self):
    #     self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
    #     # self.ctrl_plus = QShortcut(QKeySequence.ZoomIn, self, self.zoomer.zoom_in)
    #     # self.ctrl_i = QShortcut("Ctrl+I", self, self.zoomer.zoom_in)
    #     # self.ctrl_minus = QShortcut(QKeySequence.ZoomOut, self, self.zoomer.zoom_out)
    #     # self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

    def set_window_subtitle(self, subtitle):
        self.app_display_name = self.qapplication.applicationDisplayName()
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        if self.app_display_name and bool("python" != self.app_display_name):
            self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
        else:
            self.setWindowTitle(subtitle)

    def set_stay_on_top(self):
        _args = self.main_win.windowFlags() | Qt.WindowStaysOnTopHint
        self.main_win.setWindowFlags(_args)
        self.main_win.show()

    def calculate_resize_values(self, media_w, media_h) -> (int, int):
        """Calculate total window resize values from current compoment displacement"""
        self.layout.removeWidget(self.ctrls_widget)
        wo_other_qsize = self.layout.totalSizeHint()
        self.layout.addWidget(self.ctrls_widget)
        with_other_qsize = self.layout.totalSizeHint()
        wo_other_w = util.positive_threshold(wo_other_qsize.width())
        wo_other_h = util.positive_threshold(wo_other_qsize.height())
        with_other_w = util.positive_threshold(with_other_qsize.width())
        with_other_h = util.positive_threshold(with_other_qsize.height())
        total_disp_w = with_other_w - wo_other_w
        total_disp_h = with_other_h - wo_other_h
        targ_w = media_w + total_disp_w
        targ_h = media_h + total_disp_h
        return targ_w, targ_h

    @pyqtSlot(int, int)
    def on_explicitresize(self, media_w, media_h):
        targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def showEvent(self, e):
        if 1 < config.state.zoom:
            config.state.zoom = 1
        media_w, media_h = self.media_frame.get_zoomed_media_size()
        targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def sizeHint(self):
        try:
            return self.size_hint_qsize
        except AttributeError:
            media_w, media_h = self.media_frame.get_zoomed_media_size()
            targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
            self.size_hint_qsize = QSize(targ_w, targ_h)
        finally:
            return self.size_hint_qsize
