import logging

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import vlcqt
from .comm.client import RemoteInputClient
from .controls.base import OpenMenuAction
from .controls.connect import ServerConnectionAction, ServerConnectionButton
from .controls.files import FileListLoader, OpenFileAction, OpenMultipleAction
from .controls.fullscreen import (
    FullscreenController,
    FullscreenLabeledButton,
    FullscreenMenu,
)
from .controls.playback import (  # PlaybackModeAction,
    FrameResPlaybackSlider,
    NextMediaAction,
    PlayPauseAction,
    PreviousMediaAction,
)
from .controls.scale import (
    FrameScaleController,
    FrameScaleMenu,
    FrameScaleMenuButton,
    FrameSizeController,
    ZoomInAction,
    ZoomOutAction,
)
from .controls.sound import VolumeController, VolumeSliderPopUpButton
from .controls.window import AlwaysOnTopAction
from .frame.layout import MainContentFrameLayout
from .frame.viewpoint import ViewpointManager
from .gui import icons
from .gui.buttons import (  # PlaybackModeButton,
    AlwaysOnTopButton,
    NextMediaButton,
    OpenFileButton,
    OpenMultipleButton,
    PlayPauseButton,
    PreviousMediaButton,
    ZoomInButton,
    ZoomOutButton,
)
from .playlist.interf import PlaylistController
from .util import config

log = logging.getLogger(__name__)


class MainMenuButton(QToolButton):
    def __init__(self, parent, menu, size):
        super().__init__(parent=parent)
        self.menu = menu

        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = OpenMenuAction(
            icon=icons.main_menu_button, text=menu.title(), menu=self.menu, parent=self
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
        self.slider = FrameResPlaybackSlider(parent=parent)
        self.layout.addWidget(self.slider)


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

        self.create_interface_components()
        self.create_menus()
        self.create_menu_buttons()
        self.create_actions()
        self.create_main_menu()
        self.create_action_buttons()
        self.create_main_window()

        self.file_loader.load_media_paths(media_paths)

        self.initialized.emit()

    def create_interface_components(self):
        self.client = RemoteInputClient(url=self.url)
        self.vp_manager = ViewpointManager(client=self.client)
        self.frame_size_ctrlr = FrameSizeController(
            main_win=self, viewpoint_manager=self.vp_manager
        )
        self.frame_scale_ctrlr = FrameScaleController(
            main_win=self, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.content_frame_layout = MainContentFrameLayout(
            window=self, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.fullscreen_ctrlr = FullscreenController(
            content_frame_layout=self.content_frame_layout,
            viewpoint_manager=self.vp_manager,
        )
        self.playback_slider_components = PlaybackSliderComponents(self)
        self.vol_ctrlr = VolumeController(parent=self)
        self.connection_action = ServerConnectionAction(
            client=self.client, viewpoint_manager=self.vp_manager, parent=self
        )
        self.connection_button = ServerConnectionButton(
            action=self.connection_action, parent=self, size=32
        )
        self.playlist_ctrlr = PlaylistController(
            content_frame_layout=self.content_frame_layout,
            frame_size_ctrlr=self.frame_size_ctrlr,
        )
        self.file_loader = FileListLoader(
            content_frame_layout=self.content_frame_layout,
            frame_size_ctrlr=self.frame_size_ctrlr,
            playlist_ctrlr=self.playlist_ctrlr,
        )

    def create_menus(self):
        self.frame_scale_menu = FrameScaleMenu(
            main_win=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )
        self.fullscreen_menu = FullscreenMenu(
            main_win=self, fullscreen_ctrlr=self.fullscreen_ctrlr
        )

    def create_menu_buttons(self):
        self.frame_scale_menu_button = FrameScaleMenuButton(
            parent=self, frame_scale_menu=self.frame_scale_menu, size=32
        )
        self.fullscreen_menu_button = FullscreenLabeledButton(
            parent=self,
            menu=self.fullscreen_menu,
            fullscreen_ctrlr=self.fullscreen_ctrlr,
            size=40,
        )
        self.vol_slider_popup_button = VolumeSliderPopUpButton(
            vol_ctrlr=self.vol_ctrlr, parent=self, size=32
        )

    def create_actions(self):
        # self.playback_mode_action = PlaybackModeAction(parent=self)
        self.open_file_action = OpenFileAction(self, self.file_loader)
        self.open_multiple_action = OpenMultipleAction(self, self.file_loader)
        self.always_on_top_action = AlwaysOnTopAction(main_win=self)
        self.play_pause_action = PlayPauseAction(parent=self)
        self.prev_media_action = PreviousMediaAction(
            parent=self, playlist_ctrlr=self.playlist_ctrlr
        )
        self.next_media_action = NextMediaAction(
            parent=self, playlist_ctrlr=self.playlist_ctrlr
        )
        self.zoom_in_action = ZoomInAction(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )
        self.zoom_out_action = ZoomOutAction(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )

    def create_main_menu(self):
        self.main_menu = QMenu(parent=self)
        self.main_menu.addMenu(self.fullscreen_menu)
        self.main_menu.addMenu(self.frame_scale_menu)
        self.main_menu_button = MainMenuButton(
            parent=self, size=48, menu=self.main_menu
        )

    def create_action_buttons(self):
        self.prev_media_button = PreviousMediaButton(
            parent=self, action=self.prev_media_action, size=48
        )
        self.play_pause_button = PlayPauseButton(
            parent=self, action=self.play_pause_action, size=48
        )
        self.next_media_button = NextMediaButton(
            parent=self, action=self.next_media_action, size=48
        )
        # self.playback_mode_button = PlaybackModeButton(
        #     parent=self, action=self.playback_mode_action, size=32
        # )
        self.open_file_button = OpenFileButton(
            parent=self, action=self.open_file_action, size=32
        )
        self.open_multiple_button = OpenMultipleButton(
            parent=self, action=self.open_multiple_action, size=32
        )
        self.always_on_top_button = AlwaysOnTopButton(
            parent=self, action=self.always_on_top_action, size=32
        )
        self.zoom_out_button = ZoomOutButton(
            parent=self, action=self.zoom_in_action, size=32
        )
        self.zoom_in_button = ZoomInButton(
            parent=self, action=self.zoom_out_action, size=32
        )

    def create_main_window(self):
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
        self.lower_bttns_lo.addWidget(self.fullscreen_menu_button, 1, Qt.AlignLeft)

        self.lower_bttns_lo.addWidget(self.zoom_out_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.zoom_in_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.frame_scale_menu_button, 0, Qt.AlignRight)
        # self.lower_bttns_lo.addWidget(self.playback_mode_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.vol_slider_popup_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.open_file_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.open_multiple_button, 0, Qt.AlignRight)
        self.lower_bttns_lo.addWidget(self.always_on_top_button, 0, Qt.AlignRight)
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
