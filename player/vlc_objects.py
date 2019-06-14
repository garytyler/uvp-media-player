from . import vlc_facades


class MediaPlayer(vlc_facades.MediaPlayerFacade):
    def __init__(self):
        super().__init__()
        # self.stopped.connect(self.stop)


media_player = MediaPlayer()
