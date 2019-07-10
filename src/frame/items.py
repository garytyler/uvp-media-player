# from PyQt5.QtCore import QObject, Qt, pyqtSignal
# from PyQt5.QtWidgets import QAction, QFileDialog, QWidget

from .. import vlcqt


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

        track_one = [t for t in media.tracks_get()][0]
        if track_one.type == track_one.type.video:
            return super().__new__(VideoFrameItem)
        elif track_one.type == track_one.type.audio:
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


def get_media_size(vlc_media):
    if not vlc_media.is_parsed():
        vlc_media.parse()
    media_tracks = vlc_media.tracks_get()
    if not media_tracks:  # Possibly not necessary. Does all media have a track?
        return None
    track = [t for t in media_tracks][0]
    return track.video.contents.width, track.video.contents.height


def get_media_track(vlc_media):
    if not vlc_media.is_parsed():
        vlc_media.parse()
    media_tracks = vlc_media.tracks_get()
    if not media_tracks:  # Possibly not necessary. Does all media have a track?
        return None
    return [t for t in media_tracks][0]
