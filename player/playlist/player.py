import logging

from PyQt5.QtCore import pyqtSignal

from .. import vlcqt
from .model import MediaItem

log = logging.getLogger(__name__)


class PlaylistPlayer:
    listplayerstatechanged = pyqtSignal()

    def __init__(self, viewpoint_mngr, loop_mode_mngr):
        self.viewpoint_mngr = viewpoint_mngr
        self.loop_mode_mngr = loop_mode_mngr
        self.mp = vlcqt.media_player
        self.index = None
        self.mp.endreached.connect(self.on_mp_endreached)

    def on_mp_endreached(self):
        self.handle_media_end_reached()

    def handle_media_end_reached(self):
        next_index = self.index.siblingAtRow(self.index.row() + 1)
        if not next_index.isValid():
            self.handle_playlist_end_reached()
        else:
            self.index = next_index
            self.load_media(self.index)

    def handle_playlist_end_reached(self):
        playback_mode = self.loop_mode_mngr.get_mode()
        if playback_mode == "off":
            self.mp.stop()
        elif playback_mode == "one":
            self.mp.set_position(0)
            # self.load_media(self.index, play=True)
        elif playback_mode == "all":
            first_item_index = self.index.model().item(0).index()
            self.load_media(first_item_index, play=True)

    def skip_previous(self):
        prev_index = self.index.siblingAtRow(self.index.row() - 1)
        if not prev_index.isValid():
            self.mp.set_time(0)
            log.info(f"LOAD PREV MEDIA Index Invalid row={prev_index.row()}")
        else:
            self.index = prev_index
            self.load_media(self.index)

    def skip_next(self):
        next_index = self.index.siblingAtRow(self.index.row() + 1)
        if not next_index.isValid():
            log.info(f"LOAD NEXT MEDIA Index Invalid row={next_index.row()}")
            first_item_index = self.index.model().item(0).index()
            self.load_media(first_item_index)
        else:
            self.index = next_index
            self.load_media(self.index)

    def load_media(self, index, play=True):
        if not index.isValid():
            log.info(f"LOAD MEDIA Index Invalid row={index.row()}")
        else:
            self.index = index
            mrl = self.index.data(MediaItem.PathRole)
            is_spherical = self.index.data(MediaItem.SphericalRole)
            self.viewpoint_mngr.enable_per_frame_updates(is_spherical)
            self.mp.stop()
            self.mp.set_mrl(mrl)
            if play:
                self.mp.play()


def get_media_codec(vlc_media, track_num=0):
    track = [t for t in vlc_media.tracks_get()][track_num]
    description = vlcqt.libvlc_media_get_codec_description(track.type, track.codec)
    return description
