import logging

from PyQt5.QtCore import Qt

from .. import vlcqt

log = logging.getLogger(__name__)


class PlaylistPlayer:
    def __init__(self, content_frame_manager, frame_size_ctrlr):
        self.content_frame_manager = content_frame_manager
        self.frame_size_ctrlr = frame_size_ctrlr
        self.mp = vlcqt.media_player
        self.index = None
        self.mp.endreached.connect(self.on_mp_endreached)

    def on_mp_endreached(self):
        self.load_next()

    def load_previous(self):
        assert self.index
        prev_index = self.index.siblingAtRow(self.index.row() - 1)
        if not prev_index.isValid():
            log.info(f"LOAD PREV MEDIA Index Invalid row={prev_index.row()}")
        else:
            self.index = prev_index
            self.load_media(self.index)

    def load_next(self):
        assert self.index
        next_index = self.index.siblingAtRow(self.index.row() + 1)
        if not next_index.isValid():
            log.info(f"LOAD NEXT MEDIA Index Invalid row={next_index.row()}")
        else:
            self.index = next_index
            self.load_media(self.index)

    def load_media(self, index):
        if not index.isValid():
            log.info(f"LOAD MEDIA Index Invalid row={index.row()}")
        else:
            self.index = index
            media = self.index.data(Qt.UserRole)
            # media = self.index.data(Qt.UserRole)
            print(media)
            self.content_frame_manager.clear_main_content_frame()
            self.mp.stop()
            self.mp.set_media(media)
            self.content_frame_manager.reset_main_content_frame()
            self.mp.play()
