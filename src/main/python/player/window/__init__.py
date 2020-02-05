import logging
from typing import Tuple

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QShortcut,
    QSizePolicy,
    QStatusBar,
    QWidget,
)

from player.common.docking import DockableWidget, ToolBar
from player.comms.client import IOController
from player.comms.connect import ConnectStatusLabel, ConnectWideButtonBuilder
from player.comms.socks import AutoReconnectSocket
from player.config.widgets import OpenSettingsDialogAction
from player.gui.ontop import AlwaysOnTopAction
from player.gui.style import initialize_style
from player.output.frame import MediaPlayerContentFrame
from player.output.fullscreen import (
    FullscreenManager,
    FullscreenMenu,
    FullscreenStatusLabel,
)
from player.output.orientation import OrientationStatusLabel, ViewpointManager
from player.output.playback import (
    FrameResolutionTimeSlider,
    LoopModeManager,
    PlayActions,
    PlaybackModeAction,
)
from player.output.size import (
    FrameSizeManager,
    FrameZoomMenu,
    ZoomControlManager,
    ZoomInAction,
    ZoomOutAction,
)
from player.output.sound import VolumeManager, VolumePopupButton
from player.playlist.files import OpenMediaMenu
from player.playlist.player import MediaListPlayer
from player.playlist.view import DockablePlaylist, PlaylistWidget
from player.window.adjustments import OpenAdjustmentsPopupWindowAction

log = logging.getLogger(__name__)


class AppWindow(QMainWindow):
    initialized = pyqtSignal()
    centralwidgetresized = pyqtSignal()

    def __init__(self, media_player, ffprobe_cmd, settings, stylesheet, flags=None):
        QMainWindow.__init__(self, flags)
        self.settings = settings
        self._window_state = None
        self.qapp = QApplication.instance()
        initialize_style(self.qapp, stylesheet)

        self.media_player = media_player
        self.ffprobe_cmd = ffprobe_cmd

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
        self.viewpoint_mngr = ViewpointManager(
            io_ctrlr=self.io_ctrlr, media_player=self.media_player
        )
        self.loop_mode_mngr = LoopModeManager(parent=self)
        self.listplayer = MediaListPlayer(
            viewpoint_mngr=self.viewpoint_mngr,
            loop_mode_mngr=self.loop_mode_mngr,
            media_player=self.media_player,
        )
        self.frame_size_mngr = FrameSizeManager(
            main_win=self,
            viewpoint_mngr=self.viewpoint_mngr,
            listplayer=self.listplayer,
        )
        self.media_player_content_frame = MediaPlayerContentFrame(
            main_win=self,
            frame_size_mngr=self.frame_size_mngr,
            media_player=self.media_player,
        )
        self.setCentralWidget(self.media_player_content_frame)
        self.zoom_ctrl_mngr = ZoomControlManager(
            main_win=self,
            frame_size_mngr=self.frame_size_mngr,
            media_player=self.media_player,
        )
        self.fullscreen_mngr = FullscreenManager(
            main_content_frame=self.media_player_content_frame,
            viewpoint_mngr=self.viewpoint_mngr,
        )

    def create_playback_components(self):
        # self.playback_ctrls_slider = BasicPlaybackSlider(
        #     parent=self, listplayer=self.listplayer, media_player=self.media_player
        # )
        self.playback_ctrls_slider = FrameResolutionTimeSlider(
            parent=self, listplayer=self.listplayer, media_player=self.media_player
        )
        self.vol_mngr = VolumeManager(
            parent=self, listplayer=self.listplayer, media_player=self.media_player
        )
        self.play_actions = PlayActions(
            parent=self, listplayer=self.listplayer, media_player=self.media_player
        )
        self.playlist_widget = PlaylistWidget(
            listplayer=self.listplayer,
            play_ctrls=self.play_actions,
            ffprobe_cmd=self.ffprobe_cmd,
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
        self.open_settings_act = OpenSettingsDialogAction(main_win=self)
        self.open_adjustments_act = OpenAdjustmentsPopupWindowAction(
            main_win=self, media_player=self.media_player
        )

    def create_other_components(self):
        self.open_media_menu = OpenMediaMenu(
            parent=self, playlist_widget=self.playlist_widget
        )
        self.frame_scale_menu = FrameZoomMenu(
            main_win=self,
            zoom_ctrl_mngr=self.zoom_ctrl_mngr,
            listplayer=self.listplayer,
            media_player=self.media_player,
        )
        self.fullscreen_menu = FullscreenMenu(
            main_win=self, fullscreen_mngr=self.fullscreen_mngr
        )
        self.vol_popup_bttn = VolumePopupButton(parent=self, vol_mngr=self.vol_mngr)

        self.connect_wide_button_builder = ConnectWideButtonBuilder(
            parent=self, socket=self.socket
        )

    def create_gui_layout(self):
        # self.setDockOptions(DockOption.AllowNestedDocks | DockOption.AllowTabbedDocks)
        self.setDockNestingEnabled(True)
        # self.setUnifiedTitleAndToolBarOnMac(False)
        # self.setTabbedDock(True)
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

        self.button_bar_widget = QWidget(self)
        self.button_bar_widget.setContentsMargins(0, 0, 0, 0)
        self.button_bar_widget.setLayout(QGridLayout(self.button_bar_widget))
        self.button_bar_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.button_bar_widget.layout().addWidget(
            self.view_toolbar, 0, 0, 1, 1, Qt.AlignLeft
        )
        self.button_bar_widget.layout().addWidget(
            self.connect_toolbar, 0, 1, 1, 1, Qt.AlignCenter
        )
        self.button_bar_widget.layout().addWidget(
            self.media_toolbar, 0, 2, 1, 1, Qt.AlignRight
        )
        self.addToolBar(
            Qt.TopToolBarArea,
            ToolBar("Toolbar", parent=self, objects=[self.button_bar_widget]),
        )

        self.playback_slider_widget = QWidget(self)
        self.playback_slider_widget.setContentsMargins(0, 0, 0, 0)
        self.playback_slider_widget.setLayout(QGridLayout(self.playback_slider_widget))
        self.playback_slider_widget.layout().addWidget(
            self.playback_ctrls_slider, 0, 0, 1, -1, Qt.AlignTop
        )
        self.playback_bttns_left = ToolBar(
            title="Left Control",
            objects=[],
            collapsible=False,
            parent=self,
            icon_size=32,
        )
        self.playback_bttns_middle = ToolBar(
            title="Playback Controls",
            objects=self.play_actions.actions(),
            parent=self,
            collapsible=False,
            icon_size=60,
        )
        self.playback_bttns_middle.setObjectName("mainplaybuttons")
        self.playback_bttns_right = ToolBar(
            title="Right Controls",
            objects=[
                self.vol_popup_bttn,
                self.playback_mode_act,
                self.open_adjustments_act,
            ],
            collapsible=False,
            parent=self,
            icon_size=32,
        )
        self.playback_ctrls_widget = QWidget(self)
        self.playback_ctrls_widget.setContentsMargins(0, 0, 0, 0)
        self.playback_ctrls_widget.setLayout(QGridLayout(self.playback_ctrls_widget))
        self.playback_ctrls_widget.layout().addWidget(
            self.playback_slider_widget, 0, 0, 1, -1, Qt.AlignTop
        )
        self.playback_ctrls_widget.layout().addWidget(
            self.playback_bttns_left, 1, 0, 1, 1, Qt.AlignHCenter | Qt.AlignVCenter
        )
        self.playback_ctrls_widget.layout().addWidget(
            self.playback_bttns_middle, 1, 1, 1, 1, Qt.AlignHCenter | Qt.AlignVCenter
        )
        self.playback_ctrls_widget.layout().addWidget(
            self.playback_bttns_right, 1, 2, 1, 1, Qt.AlignJustify | Qt.AlignVCenter
        )
        self.playback_ctrls_dock_widget = DockableWidget(
            title="Playback",
            parent=self,
            widget=self.playback_ctrls_widget,
            w_titlebar=False,
        )

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockable_playlist)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.playback_ctrls_dock_widget)

    def create_window_shortcuts(self):
        self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
        self.ctrl_plus = QShortcut(
            QKeySequence.ZoomIn, self, self.zoom_ctrl_mngr.zoom_in
        )
        self.ctrl_i = QShortcut("Ctrl+I", self, self.zoom_ctrl_mngr.zoom_in)
        self.ctrl_minus = QShortcut(
            QKeySequence.ZoomOut, self, self.zoom_ctrl_mngr.zoom_out
        )

    def _screen_size_threshold_filter(self, target_width, target_height):
        main_win_geo = self.geometry()
        screen = self.qapp.screenAt(main_win_geo.center())
        screen_geo = screen.geometry()
        screen_w = screen_geo.width()
        screen_h = screen_geo.height()
        w = target_width if target_width < screen_w else screen_w
        h = target_height if target_height < screen_h else screen_h
        return w, h

    def _get_win_size(self, media_w, media_h, scale) -> Tuple[int, int]:
        """Calculate total window resize values from current compoment displacement"""
        layout_h = self.layout().totalSizeHint().height()
        return media_w * scale, media_h * scale + layout_h

    def resize_to_media(self, media_w, media_h, scale):
        playlist_is_visible = self.dockable_playlist.isVisible()
        if playlist_is_visible:
            self.dockable_playlist.setVisible(False)

        win_w, win_h = self._get_win_size(media_w, media_h, scale)
        self.resize(win_w, win_h)

        if playlist_is_visible:
            self.dockable_playlist.setVisible(True)

    def showEvent(self, e):
        scale = self.frame_size_mngr.get_media_scale()
        media_w, media_h = self.frame_size_mngr.get_media_size()
        self.resize_to_media(media_w, media_h, scale)
        return super().showEvent(e)

    def sizeHint(self):
        try:
            return self._size_hint
        except AttributeError:
            scale = self.frame_size_mngr.get_media_scale()
            media_w, media_h = self.frame_size_mngr.get_media_size()
            self._size_hint = QSize(*self._get_win_size(media_w, media_h, scale))
        finally:
            return self._size_hint
