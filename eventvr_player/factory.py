import vlc
from PyQt5.QtCore import Qt

from . import display, viewpoint, vlc_facades, vlc_objects, window


class PlayerFactory:
    """Temp factory for VLC and Qt objects"""

    vpmanager: viewpoint.ViewpointManager = None

    def __init__(self, media_paths=None, url=None, vlc_args=[]):
        # self.vlc_facades.instantiate_vlc(vlc_args)
        self.media_paths = media_paths
        self.url = url
        self.vlc_args = vlc_args
        self.player_win = window.PlayerWindow(
            flags=Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        )
        self.video_frame = display.DisplayFrame(parent=self.player_win)
        self.player_win.video_layout.addWidget(self.video_frame, 0)
        vlc_facades.Instance(self.vlc_args)

        if media_paths:
            self.media_player = vlc_objects.media_player
            self.media_player.set_mrl(media_paths[0])
            self.video_frame.set_media_player(media_player=self.media_player)

            # Temp
            # self.list_events = events.ListSignals(self.list_player)

            self.player_win.controls_widget.set_vlc_media_player(self.media_player)
            # self.vpmanager = viewpoint.ViewpointManager(self.media_player, self.url)
