from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QFileDialog, QWidget

from .. import vlcqt
from ..gui import icons


class FileLoader(QObject):
    def __init__(self, content_frame_layout, frame_size_ctrlr):
        super().__init__()
        self.content_frame_layout = content_frame_layout
        self.frame_size_ctrlr = frame_size_ctrlr
        self.lp = vlcqt.list_player
        self.mp = vlcqt.media_player

    def load_media_paths(self, paths: list):
        self.media_list = vlcqt.MediaList(paths)
        self.load_media_list(self.media_list)

    def load_media_list(self, media_list: vlcqt.MediaList):
        self.media_list = media_list

        self.content_frame_layout.clear_content_frame()
        self.lp.stop()
        self.lp.set_media_list(media_list)
        self.content_frame_layout.reset_content_frame()
        self.lp.stop()
        first_list_item = self.media_list.item_at_index(0)
        self.frame_size_ctrlr.conform_to_media(first_list_item)


class OpenFileAction(QAction):
    def __init__(self, parent, media_loader):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_loader = media_loader
        self.setIcon(icons.open_file)
        self.setText("Open file")
        self.setShortcut("Ctrl+O")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(
            self.parent, self.text(), directory="media"
        )
        self.media_loader.load_media_paths([file_path])


class OpenMultipleFilesAction(QAction):
    def __init__(self, parent, media_loader):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_loader = media_loader
        self.setIcon(icons.open_multiple)
        self.setText("Open multiple files")
        self.setShortcut("Ctrl+M")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_paths, filter_desc = QFileDialog.getOpenFileNames(
            self.parent, self.text(), directory="media"
        )
        self.media_loader.load_media_paths(file_paths)


class FrameView:
    def __new__(cls, media: vlcqt.Media):
        if media:
            return MediaView(media)
        else:
            return super().__new__(cls)

    def __init__(self, media: vlcqt.Media = None):
        self.media = media
        pass

    def get_media_rate(self):
        return None

    def width(self):
        return 600

    def height(self):
        return 360


class MediaView(FrameView):
    def __new__(cls, media: vlcqt.Media):
        if not media.is_parsed():
            media.parse()

        track_one = [t for t in media.tracks_get()][0]
        if track_one.type == track_one.type.video:
            return super().__new__(VideoView)
        elif track_one.type == track_one.type.audio:
            return super().__new__(AudioView)

    def __init__(self, media: vlcqt.Media):
        super().__init__(media)
        self.media = media
        self.tracks = [t for t in self.media.tracks_get()]
        self.num_tracks = self.media.get_meta(vlcqt.Meta.TrackTotal)

    def get_media_rate(self):
        return 30


class AudioView(MediaView):
    def __init__(self, media: vlcqt.Media):
        super().__init__(media)


class VideoView(MediaView):
    def __init__(self, media: vlcqt.Media):
        super().__init__(media)
        self.track = self.tracks[0]

    def width(self):
        return self.tracks[0].video.contents.width

    def height(self):
        return self.tracks[0].video.contents.height

    def get_media_rate(self):
        return self.tracks[0].video.contents.frame_rate_num


def get_media_size(vlc_media: vlcqt.Media):
    if not vlc_media.is_parsed():
        vlc_media.parse()
    media_tracks = vlc_media.tracks_get()
    if not media_tracks:  # Possibly not necessary. Does all media have a track?
        return None
    track = [t for t in media_tracks][0]
    return track.video.contents.width, track.video.contents.height


def get_media_track(vlc_media: vlcqt.Media):
    if not vlc_media.is_parsed():
        vlc_media.parse()
    media_tracks = vlc_media.tracks_get()
    if not media_tracks:  # Possibly not necessary. Does all media have a track?
        return None
    return [t for t in media_tracks][0]
