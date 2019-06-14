from . import vlc_facades


Instance = vlc_facades.Instance


class MediaPlayer(vlc_facades.MediaPlayerFacade):
    def __init__(self):
        super().__init__()
        self.stopped.connect(self.stop)


media_player = MediaPlayer()
