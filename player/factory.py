from PyQt5.QtCore import Qt

from . import viewpoint, vlc_objects, window


class PlayerFactory:
    """Temp factory for VLC and Qt objects"""

    vpmanager: viewpoint.ViewpointManager = None

    def __init__(self, media_paths=None, url=None, vlc_args=[]):
        self.media_paths = media_paths
        self.url = url
        self.vlc_args = vlc_args

        self.player_win = window.PlayerWindow(
            flags=Qt.WindowFlags(Qt.WindowStaysOnTopHint)
        )

        vlc_objects.Instance(self.vlc_args)

        if media_paths:
            self.media_player = vlc_objects.media_player
            self.media_player.set_mrl(media_paths[0])
            # self.vpmanager = viewpoint.ViewpointManager(self.media_player, self.url)
