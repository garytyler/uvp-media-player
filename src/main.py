import logging

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QShortcut,
    QSizePolicy,
    QWidget,
)

from . import vlcqt
from .base.docking import DockableTabbedWidget, ToolBar
from .comm.client import RemoteInputManager
from .comm.connect import ConnectToServerAction
from .comm.socks import AutoConnectSocket
from .gui.window import AlwaysOnTopAction
from .output.frame import MediaPlayerContentFrame
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
    ZoomInAction,
    ZoomOutAction,
)
from .output.sound import VolumeManager, VolumeSliderPopupButton
from .output.status import StatusBar
from .playlist.files import OpenMediaMenu
from .playlist.player import PlaylistPlayer
from .playlist.view import DockablePlaylist, PlaylistView
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

        self.setDockNestingEnabled(True)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)

        self.setStatusBar(StatusBar(self))

        self.create_interface()
        self.create_actions()
        self.create_other_components()
        self.create_gui_layout()
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
        self.mp_content_frame = MediaPlayerContentFrame(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        self.setCentralWidget(self.mp_content_frame)
        self.frame_zoom_mngr = FrameZoomManager(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        self.fullscreen_mngr = FullscreenManager(
            main_content_frame=self.mp_content_frame,
            status_widget=self.statusBar().fullscreen_status_widget,
            viewpoint_manager=self.vp_manager,
        )
        self.playback_mode_mngr = PlaybackModeManager(parent=self)
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

    def create_other_components(self):
        self.open_media_menu = OpenMediaMenu(
            parent=self, playlist_view=self.playlist_view
        )
        self.frame_scale_menu = FrameZoomMenu(
            main_win=self, frame_zoom_mngr=self.frame_zoom_mngr
        )
        self.fullscreen_menu = FullscreenMenu(
            main_win=self, fullscreen_mngr=self.fullscreen_mngr
        )
        self.vol_slider_popup_bttn = VolumeSliderPopupButton(
            vol_mngr=self.vol_mngr, parent=self, size=32
        )
        self.pb_slider = FrameResPlaybackSlider(parent=self)

    def create_gui_layout(self):
        ##############
        # Upper area #
        ##############

        self.media_tbar = ToolBar(
            title="Media",
            objects=[
                self.toggle_playlist_act,
                ToolBar.Separator,
                self.open_media_menu,
                ToolBar.Separator,
            ],
            parent=self,
            collapsible=True,
            icon_size=32,
        )
        self.view_tbar = ToolBar(
            title="View",
            objects=[
                self.zoom_out_act,
                self.zoom_in_act,
                self.frame_scale_menu,
                ToolBar.Separator,
                self.always_on_top_act,
                ToolBar.Separator,
                self.fullscreen_menu,
            ],
            parent=self,
            collapsible=True,
            icon_size=32,
        )
        self.corner_tbar = ToolBar(
            title="corner",
            objects=[
                ToolBar.Separator,
                self.connect_to_server_act,
                ToolBar.Separator,
                self.open_settings_act,
            ],
            parent=self,
            collapsible=True,
            icon_size=32,
        )

        bttns_widget = QWidget(self)
        bttns_widget.setContentsMargins(0, 0, 0, 0)
        bttns_widget.setLayout(QHBoxLayout(bttns_widget))
        bttns_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bttns_widget.layout().addWidget(self.media_tbar, 0, Qt.AlignLeft)
        bttns_widget.layout().addWidget(self.view_tbar, 2, Qt.AlignCenter)
        bttns_widget.layout().addWidget(self.corner_tbar, 0, Qt.AlignRight)

        self.addToolBar(
            Qt.TopToolBarArea, ToolBar("Toolbar", parent=self, objects=[bttns_widget])
        )

        ##############
        # Lower area #
        ##############

        self.pb_ctrls_tbar = ToolBar(
            title="Playback Controls",
            objects=[self.prev_media_act, self.play_pause_act, self.next_media_act],
            parent=self,
            collapsible=False,
            icon_size=52,
        )
        self.pb_options_tbar = ToolBar(
            title="Playback Options",
            objects=[
                self.playback_mode_act,
                ToolBar.Spacer,
                self.vol_slider_popup_bttn,
            ],
            collapsible=False,
            parent=self,
            icon_size=32,
        )

        # Create filter controls panel
        filters_widget = QWidget(self)
        filters_widget.setContentsMargins(0, 0, 0, 0)
        filters_widget.setLayout(QHBoxLayout(filters_widget))
        filters_dock_widget = DockableTabbedWidget(title="Filters", parent=self)
        filters_dock_widget.setWidget(filters_widget)

        pb_widget = QWidget(self)
        pb_widget.setContentsMargins(0, 0, 0, 0)
        pb_widget.setLayout(QGridLayout(pb_widget))
        pb_widget.layout().addWidget(self.pb_slider, 1, 0, 1, -1)
        pb_widget.layout().addWidget(self.pb_ctrls_tbar, 2, 1, 1, 1, Qt.AlignHCenter)
        pb_widget.layout().addWidget(self.pb_options_tbar, 2, 2, 1, 1, Qt.AlignBottom)

        pb_dock_widget = DockableTabbedWidget(title="Playback", parent=self)
        pb_dock_widget.setWidget(pb_widget)

        # Add lower dock widgets
        self.addDockWidget(Qt.BottomDockWidgetArea, pb_dock_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, filters_dock_widget)
        self.tabifyDockWidget(pb_dock_widget, filters_dock_widget)
        pb_dock_widget.raise_()

        # Add playlist dock widget
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockable_playlist)

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
