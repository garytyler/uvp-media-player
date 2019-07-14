from .. import vlcqt


class PlaylistController:
    def __init__(self, content_frame_layout, frame_size_ctrlr):
        self.playlist = None
        self.mp = vlcqt.media_player
        self.content_frame_layout = content_frame_layout
        self.frame_size_ctrlr = frame_size_ctrlr

        self.mp.endreached.connect(self.on_mp_endreached)

    def on_mp_endreached(self):
        self.index += 1
        self.load_item(self.index)
        self.mp.play()

    def load_previous(self):
        _index = self.index - 1
        self.load_item(_index)
        self.index = _index

    def load_next(self):
        _index = self.index + 1
        self.load_item(_index)
        self.index = _index

    def set_playlist(self, playlist):
        self.playlist = playlist
        self.load_item(index=0)

    def load_item(self, index):
        item = self.playlist.items[index]
        self.index = index
        self.content_frame_layout.clear_content_frame()
        self.mp.stop()
        self.mp.set_media(item)
        self.content_frame_layout.reset_content_frame()


class Playlist:
    def __init__(self, paths=None):
        self.index = 0
        self.items = []
        if paths:
            self.add_paths(paths)

    def add_paths(self, paths: list):
        for p in paths:
            self.items.append(vlcqt.Media(p))
