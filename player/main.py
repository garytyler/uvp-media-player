import logging
from typing import Tuple

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QShortcut,
    QSizePolicy,
    QStatusBar,
    QWidget,
)

from . import vlcqt
from .base.docking import DockableWidget, ToolBar
from .comm.client import IOController
from .comm.connect import ConnectStatusLabel, ConnectWideButtonBuilder
from .comm.socks import AutoReconnectSocket
from .gui.window import AlwaysOnTopAction
from .output.frame import MediaPlayerContentFrame
from .output.fullscreen import FullscreenManager, FullscreenMenu, FullscreenStatusLabel
from .output.orientation import OrientationStatusLabel, ViewpointManager
from .output.playback import (
    FrameResPlaybackSlider,
    LoopModeManager,
    PlayActions,
    PlaybackModeAction,
)
from .output.size import (
    FrameSizeManager,
    FrameZoomMenu,
    ZoomControlManager,
    ZoomInAction,
    ZoomOutAction,
)
from .output.sound import VolumeManager, VolumePopupButton
from .playlist.files import OpenMediaMenu
from .playlist.player import PlaylistPlayer
from .playlist.view import DockablePlaylist, PlaylistWidget
from .util.settings import OpenSettingsAction

log = logging.getLogger(__name__)


class AppWindow(QMainWindow):
    initialized = pyqtSignal()
    centralwidgetresized = pyqtSignal()

    def __init__(self, flags=None):

        QMainWindow.__init__(self, flags)
        self.qapp = QApplication.instance()
        self.media_player = vlcqt.media_player

        self.setDockNestingEnabled(True)

        self.create_interface()
        self.create_status_bar()
        self.create_playback_components()
        self.create_other_components()
        self.create_gui_layout()
        self.create_window_shortcuts()

        self.initialized.emit()

    def load_media(self, paths):
        self.playlist_widget.add_media(paths)

    def create_status_bar(self):
        self.status_bar = QStatusBar(parent=self)
        self.connect_status_label = ConnectStatusLabel(
            parent=self.status_bar, socket=self.socket
        )
        self.fullscreen_status_label = FullscreenStatusLabel(
            parent=self.status_bar, fullscreen_mngr=self.fullscreen_mngr
        )
        self.orientation_status_label = OrientationStatusLabel(
            viewpoint_mngr=self.viewpoint_mngr, parent=self.status_bar
        )
        self.status_bar.addPermanentWidget(self.fullscreen_status_label)
        self.status_bar.addPermanentWidget(self.connect_status_label)
        self.status_bar.addPermanentWidget(self.orientation_status_label)
        self.setStatusBar(self.status_bar)

    def create_interface(self):
        self.socket = AutoReconnectSocket()
        self.io_ctrlr = IOController(socket=self.socket)
        self.viewpoint_mngr = ViewpointManager(io_ctrlr=self.io_ctrlr)
        self.frame_size_mngr = FrameSizeManager(
            main_win=self, viewpoint_mngr=self.viewpoint_mngr
        )
        vlcqt.media_player_content_frame = MediaPlayerContentFrame(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        self.setCentralWidget(vlcqt.media_player_content_frame)
        self.zoom_ctrl_mngr = ZoomControlManager(
            main_win=self, frame_size_mngr=self.frame_size_mngr
        )
        self.fullscreen_mngr = FullscreenManager(
            main_content_frame=vlcqt.media_player_content_frame,
            viewpoint_mngr=self.viewpoint_mngr,
        )
        self.loop_mode_mngr = LoopModeManager(parent=self)
        self.vol_mngr = VolumeManager(parent=self)

    def create_playback_components(self):
        self.playlist_player = PlaylistPlayer(
            viewpoint_mngr=self.viewpoint_mngr, loop_mode_mngr=self.loop_mode_mngr
        )
        self.play_actions = PlayActions(
            parent=self, playlist_player=self.playlist_player
        )
        self.playlist_widget = PlaylistWidget(
            playlist_player=self.playlist_player,
            play_ctrls=self.play_actions,
            parent=self,
        )
        self.dockable_playlist = DockablePlaylist(
            parent=self, playlist_widget=self.playlist_widget
        )
        self.toggle_playlist_act = self.dockable_playlist.toggleViewAction()

        self.playback_mode_act = PlaybackModeAction(
            parent=self, loop_mode_mngr=self.loop_mode_mngr
        )
        self.always_on_top_act = AlwaysOnTopAction(main_win=self)
        self.zoom_in_act = ZoomInAction(parent=self, zoom_ctrl_mngr=self.zoom_ctrl_mngr)
        self.zoom_out_act = ZoomOutAction(
            parent=self, zoom_ctrl_mngr=self.zoom_ctrl_mngr
        )
        self.open_settings_act = OpenSettingsAction(main_win=self)

    def create_other_components(self):
        self.open_media_menu = OpenMediaMenu(
            parent=self, playlist_widget=self.playlist_widget
        )
        self.frame_scale_menu = FrameZoomMenu(
            main_win=self, zoom_ctrl_mngr=self.zoom_ctrl_mngr
        )
        self.fullscreen_menu = FullscreenMenu(
            main_win=self, fullscreen_mngr=self.fullscreen_mngr
        )
        self.vol_popup_bttn = VolumePopupButton(parent=self, vol_mngr=self.vol_mngr)
        self.pb_ctrls_slider = FrameResPlaybackSlider(parent=self)
        self.connect_wide_button_builder = ConnectWideButtonBuilder(
            parent=self, socket=self.socket
        )

    def create_gui_layout(self):
        self.media_toolbar = ToolBar(
            title="Media",
            objects=[self.open_media_menu, ToolBar.Separator, self.toggle_playlist_act],
            parent=self,
            collapsible=True,
            icon_size=32,
        )
        self.view_toolbar = ToolBar(
            title="View",
            objects=[
                self.frame_scale_menu,
                self.always_on_top_act,
                self.fullscreen_menu,
            ],
            parent=self,
            collapsible=True,
            icon_size=32,
        )
        self.connect_toolbar = ToolBar(
            title="Connect",
            objects=[self.connect_wide_button_builder, self.open_settings_act],
            parent=self,
            collapsible=True,
            icon_size=32,
        )
        self.connect_toolbar.setObjectName("borderedbuttons")

        button_bar_widget = QWidget(self)
        button_bar_widget.setContentsMargins(0, 0, 0, 0)
        button_bar_widget.setLayout(QGridLayout(button_bar_widget))
        button_bar_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_bar_widget.layout().addWidget(
            self.view_toolbar, 0, 0, 1, 1, Qt.AlignLeft
        )
        button_bar_widget.layout().addWidget(
            self.connect_toolbar, 0, 1, 1, 1, Qt.AlignCenter
        )
        button_bar_widget.layout().addWidget(
            self.media_toolbar, 0, 2, 1, 1, Qt.AlignRight
        )

        self.addToolBar(
            Qt.TopToolBarArea,
            ToolBar("Toolbar", parent=self, objects=[button_bar_widget]),
        )

        self.pb_ctrls_left_toolbar = ToolBar(
            title="Left Control",
            objects=[],
            collapsible=False,
            parent=self,
            icon_size=32,
        )
        self.pb_ctrls_middle_toolbar = ToolBar(
            title="Playback Controls",
            objects=self.play_actions.actions(),
            parent=self,
            collapsible=False,
            icon_size=60,
        )
        self.pb_ctrls_middle_toolbar.setObjectName("mainplaybuttons")
        self.pb_ctrls_right_toolbar = ToolBar(
            title="Right Controls",
            objects=[self.playback_mode_act, self.vol_popup_bttn],
            collapsible=False,
            parent=self,
            icon_size=32,
        )

        # Create filter controls panel
        filters_widget = QWidget(self)
        filters_widget.setContentsMargins(0, 0, 0, 0)
        filters_widget.setLayout(QHBoxLayout(filters_widget))
        filters_dock_widget = DockableWidget(
            title="Filters", parent=self, widget=filters_widget, w_titlebar=False
        )
        filters_dock_widget.setWidget(filters_widget)

        pb_ctrls_widget = QWidget(self)
        pb_ctrls_widget.setContentsMargins(0, 0, 0, 0)
        pb_ctrls_widget.setLayout(QGridLayout(pb_ctrls_widget))
        pb_ctrls_widget.layout().addWidget(self.pb_ctrls_slider, 1, 0, 1, -1)
        pb_ctrls_widget.layout().addWidget(
            self.pb_ctrls_left_toolbar, 2, 0, 1, 1, Qt.AlignJustify
        )
        pb_ctrls_widget.layout().addWidget(
            self.pb_ctrls_middle_toolbar, 2, 1, 1, 1, Qt.AlignHCenter
        )
        pb_ctrls_widget.layout().addWidget(
            self.pb_ctrls_right_toolbar, 2, 2, 1, 1, Qt.AlignJustify
        )

        pb_ctrls_dock_widget = DockableWidget(
            title="Playback", parent=self, widget=pb_ctrls_widget, w_titlebar=False
        )
        pb_ctrls_dock_widget.setWidget(pb_ctrls_widget)

        # Add lower dock widgets
        self.addDockWidget(Qt.BottomDockWidgetArea, pb_ctrls_dock_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, filters_dock_widget)
        self.tabifyDockWidget(pb_ctrls_dock_widget, filters_dock_widget)
        pb_ctrls_dock_widget.raise_()

        # Add playlist dock widget
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockable_playlist)

    def create_window_shortcuts(self):
        self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
        self.ctrl_plus = QShortcut(
            QKeySequence.ZoomIn, self, self.zoom_ctrl_mngr.zoom_in
        )
        self.ctrl_i = QShortcut("Ctrl+I", self, self.zoom_ctrl_mngr.zoom_in)
        self.ctrl_minus = QShortcut(
            QKeySequence.ZoomOut, self, self.zoom_ctrl_mngr.zoom_out
        )

    def screen_size_threshold_filter(self, target_width, target_height):
        main_win_geo = self.geometry()
        screen = self.qapp.screenAt(main_win_geo.center())
        screen_geo = screen.geometry()
        screen_w = screen_geo.width()
        screen_h = screen_geo.height()
        w = target_width if target_width < screen_w else screen_w
        h = target_height if target_height < screen_h else screen_h
        return w, h

    def get_proper_win_size(self, scale) -> Tuple[int, int]:
        """Calculate total window resize values from current compoment displacement"""
        media_w, media_h = vlcqt.libvlc_video_get_size(vlcqt.media_player, 0)
        layout_size = self.layout().totalSizeHint()
        layout_h = layout_size.height()
        if media_h:
            return media_w * scale, media_h * scale + layout_h
        else:
            return 600 * scale, 360 * scale + layout_h

    @pyqtSlot(int, int)
    def resize_to_media(self, scale):
        win_w, win_h = self.get_proper_win_size(scale)
        targ_w, targ_h = self.screen_size_threshold_filter(win_w, win_h)
        self.showNormal()
        self.resize(targ_w, targ_h)
        self._size_hint = QSize(targ_w, targ_h)

    def showEvent(self, e):
        scale = self.frame_size_mngr.get_media_scale()
        self.resize_to_media(scale)

    def sizeHint(self):
        try:
            return self._size_hint
        except AttributeError:
            scale = self.frame_size_mngr.get_media_scale()
            self._size_hint = QSize(*self.get_proper_win_size(scale))
        finally:
            return self._size_hint
