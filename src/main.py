import logging

from PyQt5.QtCore import QEvent, QPoint, QRect, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence, QPainter, QStaticText, QTextOption
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QButtonGroup,
    QDockWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QProxyStyle,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QStyle,
    QStyleOption,
    QStyleOptionTab,
    QStyleOptionToolBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import vlcqt
from .base.buttons import ActionButton, MenuButton
from .base.docking import DockableWidget, ToolBar
from .base.popup import PopupMenuAction
from .comm.client import RemoteInputManager
from .comm.connect import ConnectToServerAction
from .comm.socks import AutoConnectSocket
from .gui import icons
from .gui.window import AlwaysOnTopAction
from .output.frame import MainContentFrame, MediaPlayerContentFrame, SplitView
from .output.fullscreen import FullscreenManager, FullscreenMenu
from .output.orientation import ViewpointManager
from .output.playback import (
    FrameResPlaybackSlider,
    NextMediaAction,
    PlaybackModeAction,
    PlaybackModeManager,
    PlayPauseAction,
    PreviousMediaAction,
)
from .output.size import (
    FrameSizeManager,
    FrameZoomManager,
    FrameZoomMenu,
    FrameZoomMenuButton,
    ZoomInAction,
    ZoomOutAction,
)
from .output.sound import VolumeManager, VolumeSliderPopupButton
from .output.status import StatusBar
from .playlist.files import OpenFileAction, OpenMultipleAction
from .playlist.player import PlaylistPlayer
from .playlist.view import (
    DockablePlaylist,
    OpenPlaylistAction,
    PlaylistView,
    PopupPlaylistAction,
)
from .util import config
from .util.settings import OpenSettingsAction

log = logging.getLogger(__name__)


class AppWindow(QMainWindow):
    initialized = pyqtSignal()
    centralwidgetresized = pyqtSignal()

    def __init__(self, media_paths=[], flags=None):

        QMainWindow.__init__(self, flags)
        self.qapp = QApplication.instance()
        self.mp = vlcqt.media_player

        self.setStatusBar(StatusBar(self))

        self.setDockNestingEnabled(True)

        self.create_interface()
        self.create_menus()
        self.create_actions()
        self.add_main_layouts()
        self.setup_dock_panels()
        self.setup_toolbars()
        self.create_window_shortcuts()

        self.playlist_view.add_media(media_paths)

        self.initialized.emit()

    def create_interface(self):
        self.auto_connect_socket = AutoConnectSocket()
        self.remote_input_mngr = RemoteInputManager()
        self.vp_manager = ViewpointManager(remote_input_mngr=self.remote_input_mngr)
        self.frame_size_mngr = FrameSizeManager(
            main_win=self, viewpoint_manager=self.vp_manager
        )
        self.frame_zoom_mngr = FrameZoomManager(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        self.mp_content_frame = MediaPlayerContentFrame(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        # self.main_content_frame = MainContentFrame(
        #     main_win=self, frame_size_mngr=self.frame_size_mngr
        # )
        self.playback_mode_mngr = PlaybackModeManager(parent=self)
        self.fullscreen_mngr = FullscreenManager(
            main_content_frame=self.mp_content_frame,
            status_widget=self.statusBar().fullscreen_status_widget,
            viewpoint_manager=self.vp_manager,
        )
        self.vol_mngr = VolumeManager(parent=self)
        self.playlist_player = PlaylistPlayer(
            vp_manager=self.vp_manager, playback_mode_mngr=self.playback_mode_mngr
        )
        self.playlist_view = PlaylistView(
            playlist_player=self.playlist_player, parent=self
        )
        self.dockable_playlist = DockablePlaylist(
            parent=self, playlist_view=self.playlist_view
        )
        self.toggle_playlist_act = self.dockable_playlist.toggleViewAction()

    def create_actions(self):
        self.playback_mode_act = PlaybackModeAction(
            parent=self, playback_mode_mngr=self.playback_mode_mngr
        )
        self.open_file_action = OpenFileAction(self, self.playlist_view)
        self.open_multiple_act = OpenMultipleAction(self, self.playlist_view)
        self.always_on_top_act = AlwaysOnTopAction(main_win=self)
        self.play_pause_act = PlayPauseAction(
            parent=self, playlist_player=self.playlist_player
        )
        self.prev_media_act = PreviousMediaAction(
            parent=self, playlist_player=self.playlist_player
        )
        self.next_media_act = NextMediaAction(
            parent=self, playlist_player=self.playlist_player
        )
        self.zoom_in_act = ZoomInAction(
            parent=self, frame_zoom_mngr=self.frame_zoom_mngr
        )
        self.zoom_out_act = ZoomOutAction(
            parent=self, frame_zoom_mngr=self.frame_zoom_mngr
        )
        self.open_settings_act = OpenSettingsAction(main_win=self)
        self.connect_to_server_act = ConnectToServerAction(
            auto_connect_socket=self.auto_connect_socket,
            connect_status_widget=self.statusBar().connect_status_widget,
            parent=self,
        )

    def create_menus(self):
        self.frame_scale_menu = FrameZoomMenu(
            main_win=self, frame_zoom_mngr=self.frame_zoom_mngr
        )
        self.fullscreen_menu = FullscreenMenu(
            main_win=self, fullscreen_mngr=self.fullscreen_mngr
        )

        self.vol_slider_popup_bttn = VolumeSliderPopupButton(
            vol_mngr=self.vol_mngr, parent=self, size=32
        )

    def add_main_layouts(self):
        self.setCentralWidget(self.mp_content_frame)

    def get_pb_dock_widget(self):
        pb_widget = QWidget(self)
        pb_layout = QGridLayout(pb_widget)

        # Slider
        pb_slider = FrameResPlaybackSlider(parent=pb_widget)
        pb_layout.addWidget(pb_slider, 1, 0, 1, -1)

        # Buttons layout
        main_bttns_layout = QHBoxLayout(pb_widget)
        main_bttns_layout.setContentsMargins(0, 0, 0, 0)
        pb_layout.addLayout(main_bttns_layout, 2, 0, 1, -1, Qt.AlignHCenter)

        # Buttons
        for playback_button in [
            ActionButton(parent=pb_widget, action=self.prev_media_act, size=48),
            ActionButton(parent=pb_widget, action=self.play_pause_act, size=48),
            ActionButton(parent=pb_widget, action=self.next_media_act, size=48),
        ]:
            main_bttns_layout.addWidget(playback_button)

        pb_dock_widget = DockableWidget(title="Playback", parent=self)
        pb_dock_widget.setWidget(pb_widget)
        return pb_dock_widget

    def get_filter_dock_widget(self):
        filter_ctrls = QWidget(self)
        filter_ctrls_lo = QHBoxLayout(filter_ctrls)
        filter_ctrls_lo.setContentsMargins(0, 0, 0, 0)

        # filter_ctrls_lo.addWidget(self.frame_scale_menu_bttn, Qt.AlignCenter)
        # filter_ctrls_lo.addWidget(self.fullscreen_menu_bttn, Qt.AlignCenter)
        # filter_ctrls_lo.addWidget(self.vol_slider_popup_bttn, Qt.AlignCenter)

        filter_dock = DockableWidget(title="Other", parent=self)
        filter_dock.setWidget(filter_ctrls)
        return filter_dock

    def setup_dock_panels(self):
        pb_dock_widget = self.get_pb_dock_widget()
        self.addDockWidget(Qt.BottomDockWidgetArea, pb_dock_widget)

        filter_dock_widget = self.get_filter_dock_widget()
        self.addDockWidget(Qt.BottomDockWidgetArea, filter_dock_widget)

        self.tabifyDockWidget(pb_dock_widget, filter_dock_widget)
        pb_dock_widget.raise_()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockable_playlist)

    def setup_toolbars(self):
        media_toolbar = ToolBar(
            title="Media",
            objects=[
                self.toggle_playlist_act,
                self.open_file_action,
                self.open_multiple_act,
            ],
            parent=self,
        )
        view_toolbar = ToolBar(
            title="View",
            objects=[
                self.zoom_out_act,
                self.zoom_in_act,
                self.frame_scale_menu,
                ToolBar.Separator,
                self.always_on_top_act,
                self.fullscreen_menu,
            ],
            parent=self,
        )
        other_toolbar = ToolBar(
            title="Other",
            objects=[self.open_settings_act, self.connect_to_server_act],
            parent=self,
        )
        playback_toolbar = ToolBar(
            title="playback", objects=[self.playback_mode_act], parent=self
        )
        self.addToolBar(Qt.TopToolBarArea, media_toolbar)
        self.addToolBar(Qt.TopToolBarArea, view_toolbar)
        self.addToolBar(Qt.TopToolBarArea, other_toolbar)
        self.addToolBar(Qt.TopToolBarArea, playback_toolbar)

    def create_window_shortcuts(self):
        self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
        self.ctrl_plus = QShortcut(
            QKeySequence.ZoomIn, self, self.frame_zoom_mngr.zoom_in
        )
        self.ctrl_i = QShortcut("Ctrl+I", self, self.frame_zoom_mngr.zoom_in)
        self.ctrl_minus = QShortcut(
            QKeySequence.ZoomOut, self, self.frame_zoom_mngr.zoom_out
        )

    def calculate_resize_values(self, scale) -> (int, int):
        """Calculate total window resize values from current compoment displacement"""
        media_w, media_h = vlcqt.libvlc_video_get_size(self.mp, 0)
        layout_size = self.layout().totalSizeHint()
        layout_h = layout_size.height()
        return media_w * scale, media_h * scale + layout_h

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
    def resize_to_media(self, scale):
        win_w, win_h = self.calculate_resize_values(scale)
        targ_w, targ_h = self.screen_size_threshold_filter(win_w, win_h)
        self.showNormal()
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def showEvent(self, e):
        if 1 < config.state.view_scale:
            scale = config.state.view_scale = 1
        else:
            scale = config.state.view_scale
        media_w, media_h = vlcqt.libvlc_video_get_size(self.mp, 0)
        targ_w, targ_h = self.calculate_resize_values(scale)
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def sizeHint(self):
        try:
            return self.size_hint_qsize
        except AttributeError:
            media_w, media_h = vlcqt.libvlc_video_get_size(self.mp, 0)
            scale = config.state.view_scale
            targ_w, targ_h = self.calculate_resize_values(scale)
            self.size_hint_qsize = QSize(targ_w, targ_h)
        finally:
            return self.size_hint_qsize
