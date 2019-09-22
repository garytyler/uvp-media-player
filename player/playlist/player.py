import logging

from PyQt5.QtCore import QModelIndex, QObject, pyqtSlot

from .. import vlcqt
from .model import MediaItem

log = logging.getLogger(__name__)


class PlaylistPlayer(QObject):
    def __init__(self, viewpoint_mngr, loop_mode_mngr):
        super().__init__()
        self.viewpoint_mngr = viewpoint_mngr
        self.loop_mode_mngr = loop_mode_mngr

        self.mp = vlcqt.media_player
        self._item = None
        self.mp.endreached.connect(self._handle_media_finished)

    def on_mp_endreached(self):
        self._handle_media_finished()

    @pyqtSlot(int)
    def on_playlist_rowCountChanged(self, count):
        """Enable/disable GUI elements when media is added or removed"""
        if count == 0:
            self.mp.stop()

    def current_index(self):
        return self._item.model().indexFromItem(self._item)

    def _handle_media_finished(self):
        """Perform next expected task when media is finished."""
        curr_index = self._item.index()
        next_index = curr_index.siblingAtRow(self._item.row() + 1)
        loop_mode = self.loop_mode_mngr.get_mode()
        if loop_mode == "one" and curr_index.isValid():
            self.mp.stop()
            self.mp.play()
        elif next_index.isValid():
            self.load_media(next_index)
            self.mp.play()
        else:
            self._handle_playlist_finished()

    def _handle_playlist_finished(self):
        """Perform next expected task when playlist is finished."""
        loop_mode = self.loop_mode_mngr.get_mode()
        if loop_mode == "off":
            self.mp.stop()
            return None
        elif loop_mode == "one":
            self.mp.set_position(0)
            if self._item.index().isValid():
                self.mp.play()
        elif loop_mode == "all":
            first_item_index = self._item.index().siblingAtRow(0)
            self.load_media(first_item_index, play=True)
            self.mp.play()

    def skip_previous(self):
        prev_index = self._item.index().siblingAtRow(self._item.row() - 1)
        is_playing = self.mp.is_playing()
        if prev_index.isValid():
            self._item = self._item.model().itemFromIndex(prev_index)
            self.load_media(prev_index)
        else:
            self.mp.set_time(0)
            log.info(f"LOAD PREV MEDIA Index Invalid row={prev_index.row()}")
        if is_playing:
            self.mp.play()

    def skip_next(self):
        is_playing = self.mp.is_playing()
        next_index = self._item.index().siblingAtRow(self._item.row() + 1)
        if next_index.isValid():
            self._item = self._item.model().itemFromIndex(next_index)
            self.load_media(next_index)
        else:
            log.info(f"LOAD NEXT MEDIA Index Invalid row={next_index.row()}")
            first_item_index = self._item.model().item(0).index()
            self.load_media(first_item_index)
        if is_playing:
            self.mp.play()

    def load_media(self, index: QModelIndex) -> bool:
        if not index.isValid():
            log.info(f"LOAD MEDIA Index Invalid row={index.row()}")
            return False
        else:
            self._item = index.model().itemFromIndex(index)
            mrl = index.data(MediaItem.PathRole)
            is_spherical = index.data(MediaItem.SphericalRole)
            self.viewpoint_mngr.enable_per_frame_updates(is_spherical)
            self.mp.stop()
            self.mp.set_mrl(mrl)
            return True

    def unload_media(self, items: list):
        """If current media is in 'items', unload it without loading any of the other
        items in 'items'.
        """
        if self._item not in items:
            return None

        curr_index = self._item.index()
        loop_mode = self.loop_mode_mngr.get_mode()

        # Get indexes after current index
        indexes = []
        index = curr_index.siblingAtRow(self._item.row() + 1)
        while index.isValid():
            indexes.append(index)
            index = index.siblingAtRow(index.row() + 1)

        # If loop mode is 'all', get indexes before current index
        if loop_mode == "all":
            index = curr_index.siblingAtRow(0)
            while index != curr_index:
                indexes.append(index)
                index = index.siblingAtRow(index.row() + 1)

        # Look for a valid item in collected indexes and load
        for index in indexes:
            item = index.model().itemFromIndex(index)
            if item not in items:
                if self.load_media(index):
                    return None  # Return if a valid item was loaded

        # Stop playing and let view handle controls state
        self.mp.stop()


def get_media_codec(vlc_media, track_num=0):
    track = [t for t in vlc_media.tracks_get()][track_num]
    description = vlcqt.libvlc_media_get_codec_description(track.type, track.codec)
    return description
