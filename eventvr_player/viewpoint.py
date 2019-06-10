import logging

import vlc
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from . import comm

# from PyQt5.QtGui import QColor, QPalette
# from PyQt5.QtWidgets import QFrame


log = logging.getLogger(__name__)


class FrameTimer(QTimer):
    new_frame = pyqtSignal()
    list_player_next_item_set = pyqtSignal()

    def __init__(self, list_player, parent=None):
        QTimer.__init__(self, parent)
        self.setTimerType(Qt.PreciseTimer)

        self.list_player = list_player
        self.media_player = self.list_player.get_media_player()

        self.list_player.event_manager().event_attach(
            vlc.EventType.MediaListPlayerNextItemSet, self.on_list_player_next_item_set
        )
        self.list_player_next_item_set.connect(self.initialize_new_media)

        self.media = self.media_state = self.media_event_manager = None
        if self.media_player.get_media():  # Should be None, but check
            self.initialize_new_media()
        self.timeout.connect(self.on_timeout)

    def on_timeout(self):
        if self.media_state == vlc.State.Playing:
            self.new_frame.emit()

    def on_media_state_changed(self, e):
        log.debug(f"MEDIA STATE CHANGED media.state={self.media_state}")
        self.media_state = self.list_player.get_state()

    def on_list_player_next_item_set(self, e):
        log.debug(f"NEXT ITEM SET event.type={e.type}")
        self.list_player_next_item_set.emit()
        # self.initialize_new_media()

    def initialize_new_media(self):
        # Unregister old media event
        if self.media_event_manager:
            self.media_event_manager.event_detach(vlc.EventType.MediaStateChanged)

        # register new media event
        self.media = self.media_player.get_media()
        self.media_event_manager = self.media.event_manager()
        self.media_event_manager.event_attach(
            vlc.EventType.MediaStateChanged, self.on_media_state_changed
        )

        # Set timer interval to media fps
        play_rate_quotient = self.media_player.get_rate()
        fps = self.get_media_fps(self.media)
        self.setInterval(1000 / (fps * play_rate_quotient))

    @staticmethod
    def get_media_fps(media: vlc.Media) -> float:
        if not media:
            return None
        if not media.is_parsed():
            media.parse()
        track = [t for t in media.tracks_get()][0]
        return track.video.contents.frame_rate_num


class ViewpointManager:
    """Handles setting viewpoint in VLC media player object. Uses Qt only for timer."""

    def __init__(self, list_player, url):
        self.list_player = list_player
        self.media_player = self.list_player.get_media_player()
        self.curr_yaw = self.curr_pitch = self.curr_roll = 0

        self.frame_timer = FrameTimer(self.list_player)
        self.frame_timer.new_frame.connect(self.on_new_frame)
        self.frame_timer.list_player_next_item_set.connect(self.trigger_redraw)

        self.client = comm.RemoteInputClient(url=url)
        self.client.socket.connected.connect(self.frame_timer.start)
        self.client.socket.disconnected.connect(self.frame_timer.stop)

    def on_new_frame(self):
        new_motion_state = self.client.get_new_motion_state()
        if new_motion_state:
            self.set_new_viewpoint(*new_motion_state)

    def set_new_viewpoint(self, yaw, pitch, roll):
        self.vp = vlc.VideoViewpoint()
        self.vp.field_of_view = 80
        self.vp.yaw, self.vp.pitch, self.vp.roll = -yaw, -pitch, -roll
        errorcode = self.media_player.video_update_viewpoint(
            p_viewpoint=self.vp, b_absolute=True
        )
        if errorcode != 0:
            log.error("Error setting viewpoint")

    def trigger_redraw(self):
        """Force a redraw of the video frame to correct the displayed aspect ratio
        of a 360 video.

        The redraw is triggered by a hack... setting a new viewpoint with an
        unobservable differential applied to the yaw value. This is probably only
        necessary because of the the implementation of viewpoints in vlclib 3.0, and will hopefully be unnecessary in 4.0.
        """
        differential = 0.01 ** 20  # (0.01 ** 22) is max effective differential
        self.set_new_viewpoint(
            self.curr_yaw + differential, self.curr_pitch, self.curr_roll
        )
