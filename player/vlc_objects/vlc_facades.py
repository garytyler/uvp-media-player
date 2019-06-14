import logging

import vlc

from . import vlc_signals

log = logging.getLogger(__name__)


class Instance:
    _vlc_obj: vlc.Instance = None

    def __new__(cls, args=[]):
        return cls._vlc_obj if cls._vlc_obj else vlc.Instance(args)

    def __init__(self, args=[]):
        pass


class MediaPlayerFacade(vlc_signals.MediaPlayerSignals):
    _vlc_obj: vlc.MediaPlayer = None

    def __init__(self):
        self._vlc_obj = vlc.MediaPlayer(Instance())
        super().__init__(vlc_media_player=self._vlc_obj)

    def __getattr__(self, attribute):
        return getattr(self._vlc_obj, attribute)


def vlcqtsetter(f):
    def wrapper(self, *args):
        obj = getattr(args[0], "_vlc_obj", args[0])
        f(self, obj)

    return wrapper
