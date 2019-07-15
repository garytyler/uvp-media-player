import logging

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy, QStackedLayout

from .. import vlcqt
from ..util import config

log = logging.getLogger(__name__)


class ContentFrameItem:
    def __new__(cls, media=None):
        if media:
            return MediaFrameItem(media)
        else:
            return super().__new__(cls)

    def __init__(self, media=None):
        self.media = media
        pass

    def get_media_rate(self):
        return None

    def width(self):
        return 600

    def height(self):
        return 360


class MediaFrameItem(ContentFrameItem):
    def __new__(cls, media):
        if not media.is_parsed():
            media.parse()

        tracks = list(media.tracks_get())
        if tracks[0].type == vlcqt.TrackType.video:
            return super().__new__(VideoFrameItem)
        elif tracks[0].type == vlcqt.TrackType.audio:
            return super().__new__(AudioFrameItem)

    def __init__(self, media):
        super().__init__(media)
        self.media = media
        self.tracks = [t for t in self.media.tracks_get()]
        self.num_tracks = self.media.get_meta(vlcqt.Meta.TrackTotal)

    def get_media_rate(self):
        return 30


class AudioFrameItem(MediaFrameItem):
    def __init__(self, media):
        super().__init__(media)


class VideoFrameItem(MediaFrameItem):
    def __init__(self, media):
        super().__init__(media)
        self.track = self.tracks[0]

    def width(self):
        return self.tracks[0].video.contents.width

    def height(self):
        return self.tracks[0].video.contents.height

    def get_media_rate(self):
        return self.tracks[0].video.contents.frame_rate_num


class BaseContentFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mp = vlcqt.media_player
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_fill_color(0, 0, 0)

    def set_fill_color(self, r, g, b):
        p = self.palette()
        p.setColor(QPalette.Window, QColor(r, g, b))
        self.setPalette(p)


class FullscreenContentFrame(BaseContentFrame):
    def __init__(self, qscreen):
        super().__init__(parent=None)
        self.setWindowState(Qt.WindowFullScreen)  # Lets geo map to non-primary screens
        self.setGeometry(qscreen.geometry())
        self.showFullScreen()
        self.mp.set_output_widget(self)


class MainContentFrame(BaseContentFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.mp = vlcqt.media_player
        self.mp.set_output_widget(self)
        self.content_qsize = QSize()

    def sizeHint(self):
        # self.mp.get_media()
        w, h = self.frame_size_ctrlr.get_current_media_size()
        scale = config.state.view_scale
        self.content_qsize.setWidth(w * scale)
        self.content_qsize.setHeight(h * scale)
        return QSize(w, h)


class ContentFrameManager(QFrame):
    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__()
        self.setLayout(QStackedLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr
        self.filler_frame = BaseContentFrame(parent=self.main_win)
        self.layout().insertWidget(1, self.filler_frame)
        # self.filler_frame.hide()
        # self._new_main_content_frame()

    def _new_main_content_frame(self):
        self.clear_main_content_frame()
        new_mp_frame = MainContentFrame(
            main_win=self.main_win, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.mp_frame = new_mp_frame

        self.layout().insertWidget(0, self.mp_frame)
        self.layout().setCurrentIndex(0)

    def clear_main_content_frame(self):
        if hasattr(self, "main_content_frame"):
            self.mp_content_frame.hide()
            self.layout().removeWidget(self.mp_frame)
            del self.mp_content_frame
        if isinstance(self.layout().widget(0), BaseContentFrame):
            _w = self.layout().widget(0)
            _w.hide()
            self.layout().removeWidget(_w)
            del _w

    def reset_main_content_frame(self):
        self._new_main_content_frame()
        self.frame_size_ctrlr.conform_to_media()

    def start_fullscreen(self, qscreen):

        self.fs_frame = FullscreenContentFrame(qscreen)
        self.fs_frame.show()
        self.layout().setCurrentIndex(1)
        # del self.mp_frame

    #
    def stop_fullscreen(self):
        self.fs_frame.hide()
        self.layout().setCurrentIndex(0)
        # self.reset_main_content_frame()
        del self.fs_frame
