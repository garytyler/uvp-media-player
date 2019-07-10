import logging
from os.path import exists

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import vlcqt
from .comm import client
from .controls import base, connect, files, playback, scale, screen, sound, window
from .controls.screen import FullscreenController
from .frame.layout import MainContentFrameLayout
from .frame.viewpoint import ViewpointManager
from .gui import icons
from .util import config

log = logging.getLogger(__name__)


class MainMenuButton(QToolButton):
    def __init__(self, parent, menu, size):
        super().__init__(parent=parent)

        self.menu = menu
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = base.OpenMenuAction(
            icon=icons.main_menu_button, text=menu.title(), menu=self.menu, button=self
        )

        self.action.setToolTip("More Options")
        self.setCheckable(False)
        self.setDefaultAction(self.action)


class PlaybackSliderComponents(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        l, t, r, b = self.layout.getContentsMargins()
        self.layout.setContentsMargins(l, 0, r, 0)
        self.slider = playback.FrameResPlaybackSlider(parent=parent)
        self.layout.addWidget(self.slider)


class MainMenu(QMenu):
    def __init__(self, main_win: QMainWindow):
        super().__init__(parent=main_win)
        self.main_win = main_win

        self.addAction(window.StayOnTop(main_win=main_win))


class AppWindow(QMainWindow):
    url = "wss://eventvr.herokuapp.com/mediaplayer"
    initialized = pyqtSignal()

    def __init__(self, media_paths=[], flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())
        self.qapp = QApplication.instance()
        self.mp = vlcqt.media_player

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        self.create_components()
        self.add_components()

        self.media_loader.load_media_paths(media_paths)

        self.initialized.emit()

    def create_components(self):
        self.client = client.RemoteInputClient(url=self.url)
        self.vp_manager = ViewpointManager(client=self.client)
        self.connection_action = connect.ServerConnectionAction(
            client=self.client, viewpoint_manager=self.vp_manager, parent=self
        )
        self.connection_button = connect.ServerConnectionButton(
            action=self.connection_action, parent=self, size=32
        )
        self.frame_size_ctrlr = scale.FrameSizeController(
            main_win=self, viewpoint_manager=self.vp_manager
        )
        self.frame_scale_ctrlr = scale.FrameScaleController(
            main_win=self, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.frame_scale_menu = scale.FrameScaleMenu(
            main_win=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )
        self.content_frame_layout = MainContentFrameLayout(
            main_win=self, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.fullscreen_ctrlr = FullscreenController(
            content_frame_layout=self.content_frame_layout,
            viewpoint_manager=self.vp_manager,
        )
        self.screens_menu = screen.ScreensMenu(
            main_win=self, fullscreen_ctrlr=self.fullscreen_ctrlr
        )
        self.fullscreen_button = screen.FullscreenButton(
            parent=self,
            menu=self.screens_menu,
            fullscreen_ctrlr=self.fullscreen_ctrlr,
            size=40,
        )
        self.playback_slider_components = PlaybackSliderComponents(self)
        self.prev_media_button = playback.PreviousMediaButton(parent=self, size=48)
        self.play_pause_button = playback.PlayPauseButton(parent=self, size=48)
        self.next_media_button = playback.NextMediaButton(parent=self, size=48)

        self.playback_mode_button = playback.TogglePlaybackModeButton(
            parent=self, size=32
        )
        self.frame_scale_menu_button = scale.FrameScaleMenuButton(
            parent=self, frame_scale_menu=self.frame_scale_menu, size=32
        )
        self.zoom_out_button = scale.ZoomOutButton(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr, size=32
        )
        self.zoom_in_button = scale.ZoomInButton(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr, size=32
        )
        self.vol_ctrlr = sound.VolumeController(parent=self)
        self.vol_button = sound.VolumePopUpButton(
            vol_ctrlr=self.vol_ctrlr, parent=self, size=32
        )
        self.media_loader = files.FileLoader(
            content_frame_layout=self.content_frame_layout,
            frame_size_ctrlr=self.frame_size_ctrlr,
        )
        self.open_file_action = files.OpenFileAction(self, self.media_loader)
        self.open_multiple_action = files.OpenMultipleAction(self, self.media_loader)
        self.open_file_button = files.OpenFileButton(
            parent=self, size=32, action=self.open_file_action
        )
        self.open_multiple_button = files.OpenMultipleButton(
            parent=self, size=32, action=self.open_multiple_action
        )

        self.main_menu = MainMenu(main_win=self)
        self.main_menu_button = MainMenuButton(
            parent=self, size=48, menu=self.main_menu
        )

    def add_components(self):

        # Main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        # Media frame
        self.layout.addLayout(self.content_frame_layout, 0)

        # Controls layout
        self.ctrls_widget = QWidget(self)
        self.ctrls_layout = QGridLayout(self.ctrls_widget)
        self.ctrls_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ctrls_widget, 0, Qt.AlignBottom)

        self.frame_ctrls = QWidget(self)
        self.frame_ctrls_lo = QHBoxLayout(self.frame_ctrls)
        self.frame_ctrls_lo.setContentsMargins(0, 0, 0, 0)
        self.frame_ctrls_lo.addWidget(self.connection_button, Qt.AlignLeft)
        self.ctrls_layout.addWidget(self.frame_ctrls, 1, 0, 1, -1, Qt.AlignBottom)

        self.ctrls_layout.addWidget(self.playback_slider_components, 2, 0, 1, -1)

        self.playback_bttns = QWidget(self)
        self.playback_bttns_lo = QHBoxLayout(self.playback_bttns)
        self.playback_bttns_lo.setContentsMargins(0, 0, 0, 0)
        self.playback_bttns_lo.addWidget(self.prev_media_button)
        self.playback_bttns_lo.addWidget(self.play_pause_button)
        self.playback_bttns_lo.addWidget(self.next_media_button)
        self.ctrls_layout.addWidget(self.playback_bttns, 3, 0, 1, -1, Qt.AlignCenter)

        self.lower_bttns = QWidget(self)
        self.lower_bttns_lo = QHBoxLayout(self.lower_bttns)
        self.lower_bttns_lo.setContentsMargins(0, 0, 0, 0)
        self.lower_bttns_lo.addWidget(self.fullscreen_button, 1, Qt.AlignLeft)

        self.lower_bttns_lo.addWidget(self.zoom_out_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.zoom_in_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.frame_scale_menu_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.playback_mode_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.vol_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.open_file_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.open_multiple_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.main_menu_button, 0, Qt.AlignRight)

        self.ctrls_layout.addWidget(self.lower_bttns, 4, 0, 1, -1, Qt.AlignBottom)

    # def create_window_shortcuts(self):
    #     self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
    # self.ctrl_plus = QShortcut(QKeySequence.ZoomIn, self, self.zoomer.zoom_in)
    # self.ctrl_i = QShortcut("Ctrl+I", self, self.zoomer.zoom_in)
    # self.ctrl_minus = QShortcut(QKeySequence.ZoomOut, self, self.zoomer.zoom_out)
    # self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

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

    @staticmethod
    def positive_threshold(value: int):
        return value if value > 0 else 0

    def calculate_resize_values(self, media_w, media_h) -> (int, int):
        """Calculate total window resize values from current compoment displacement"""
        self.layout.removeWidget(self.ctrls_widget)
        wo_other_qsize = self.layout.totalSizeHint()
        self.layout.addWidget(self.ctrls_widget)
        with_other_qsize = self.layout.totalSizeHint()
        wo_other_w = self.positive_threshold(wo_other_qsize.width())
        wo_other_h = self.positive_threshold(wo_other_qsize.height())
        with_other_w = self.positive_threshold(with_other_qsize.width())
        with_other_h = self.positive_threshold(with_other_qsize.height())
        total_disp_w = with_other_w - wo_other_w
        total_disp_h = with_other_h - wo_other_h
        targ_w = media_w + total_disp_w
        targ_h = media_h + total_disp_h
        return targ_w, targ_h

    def screen_size_threshold_filter(self, target_width, target_height):
        main_win_geo = self.geometry()
        screen = self.qapp.screenAt(main_win_geo.center())
        screen_geo = screen.geometry()
        screen_w = screen_geo.width()
        screen_h = screen_geo.height()
        w = target_width if target_width < screen_w else screen_w
        h = target_height if target_height < screen_h else screen_h
        return w, h

    @pyqtSlot(int, int)
    def resize_to_media(self, media_w, media_h):
        win_w, win_h = self.calculate_resize_values(media_w, media_h)
        targ_w, targ_h = self.screen_size_threshold_filter(win_w, win_h)
        self.showNormal()
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def showEvent(self, e):
        if 1 < config.state.view_scale:
            scale = config.state.view_scale = 1
        else:
            scale = config.state.view_scale
        media_w, media_h = self.frame_size_ctrlr.get_current_media_size()
        targ_w, targ_h = self.calculate_resize_values(media_w * scale, media_h * scale)
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def sizeHint(self):
        try:
            return self.size_hint_qsize
        except AttributeError:
            media_w, media_h = self.frame_size_ctrlr.get_current_media_size()
            scale = config.state.view_scale
            targ_w, targ_h = self.calculate_resize_values(
                media_w * scale, media_h * scale
            )
            self.size_hint_qsize = QSize(targ_w, targ_h)
        finally:
            return self.size_hint_qsize
