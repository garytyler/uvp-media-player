import logging

from PyQt5.QtCore import QModelIndex, QObject, Qt, QTimer, pyqtSignal, pyqtSlot

from player import config
from player.playlist.model import MediaItem

log = logging.getLogger(__name__)


class _ListPlayer(QObject):
    mediachanged = pyqtSignal(MediaItem)

    def __init__(self, viewpoint_mngr, loop_mode_mngr, media_player):
        super().__init__()
        self.viewpoint_mngr = viewpoint_mngr
        self.loop_mode_mngr = loop_mode_mngr
        self.mp = media_player
        self._item = None
        self.mp.endreached.connect(self._handle_media_finished)

    def on_mp_endreached(self):
        self._handle_media_finished()

    @pyqtSlot(int)
    def on_playlist_rowCountChanged(self, count):
        """Enable/disable GUI elements when media is added or removed"""
        if count == 0:
            self.mp.stop()

    def index(self):
        return self._item.model().indexFromItem(self._item)

    def item(self):
        return self._item

    def _handle_media_finished(self):
        """Perform next expected task when media is finished."""
        curr_index = self._item.index()
        next_index = curr_index.sibling(self._item.row() + 1, 0)
        loop_mode = config.state.loop_mode
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
        loop_mode = config.state.loop_mode
        if loop_mode == "off":
            self.mp.stop()
            return None
        elif loop_mode == "one":
            self.mp.set_position(0)
            if self._item.index().isValid():
                self.mp.play()
        elif loop_mode == "all":
            first_item_index = self._item.index().sibling(0, 0)
            self.load_media(first_item_index)
            self.mp.play()

    def skip_previous(self):
        prev_index = self._item.index().sibling(self._item.row() - 1, 0)
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
        next_index = self._item.index().sibling(self._item.row() + 1, 0)
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
        item = index.model().itemFromIndex(index)
        if not isinstance(item, MediaItem):
            log.error(f"Unexpected item type '{type(item)}'. Expected MediaItem.")
            return False
        else:
            self._item = index.model().itemFromIndex(index)
            path = self._item.path()
            is_spherical = self._item.is_spherical()
            self.viewpoint_mngr.set_redraw_every_frame(is_spherical)
            self.mp.stop()
            self.mp.set_mrl(path)
            self.mediachanged.emit(self._item)
            self.mp.play()
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
        index = curr_index.sibling(self._item.row() + 1, 0)
        while index.isValid():
            indexes.append(index)
            index = index.sibling(index.row() + 1, 0)

        # If loop mode is 'all', get indexes before current index
        if loop_mode == "all":
            index = curr_index.sibling(0, 0)
            while index != curr_index:
                indexes.append(index)
                index = index.sibling(index.row() + 1, 0)

        # Look for a valid item in collected indexes and load
        for index in indexes:
            item = index.model().itemFromIndex(index)
            if item not in items:
                if self.load_media(index):
                    return None  # Return if a valid item was loaded

        # Stop playing and let view handle controls state
        self.mp.stop()


class MediaListPlayer(_ListPlayer):
    """WIP to provide most vlc.MediaPlayer functionality in the one class with the
    playlist.
    """

    newframe = pyqtSignal()
    slider_precision = 100

    def __init__(self, viewpoint_mngr, loop_mode_mngr, media_player):
        super().__init__(
            viewpoint_mngr=viewpoint_mngr,
            loop_mode_mngr=loop_mode_mngr,
            media_player=media_player,
        )
        self.timer = QTimer()
        self.timer.setTimerType(Qt.CoarseTimer)
        self.timer.timeout.connect(self.on_timeout)

        self.mp.playing.connect(self.timer.start)
        self.mp.stopped.connect(self.timer.stop)
        self.mp.paused.connect(self.timer.stop)

        self.mediachanged.connect(self.on_mediachanged)

    def on_timeout(self):
        self.newframe.emit()

    @pyqtSlot(MediaItem)
    def on_mediachanged(self, media_item: MediaItem):
        media_info = media_item.info()
        media_fps = media_info["avg_frame_rate"]
        self.timer.setInterval(media_fps)
