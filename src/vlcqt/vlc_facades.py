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


class MediaListPlayerFacade(vlc_signals.MediaListPlayerVlclibSignals):
    _vlc_obj: vlc.MediaListPlayer = None

    def __init__(self):
        self._vlc_obj = vlc.MediaListPlayer(Instance())
        super().__init__(vlc_media_list_player=self._vlc_obj)

    def __getattr__(self, attribute):
        return getattr(self._vlc_obj, attribute)


class MediaFacade(vlc_signals.MediaVlclibSignals):
    def __init__(self, mrl, *options):
        self._vlc_obj = vlc.Media(mrl, *options)
        super().__init__(vlc_media=self._vlc_obj)

    def __getattr__(self, attribute):
        try:
            return getattr(self._vlc_obj, attribute)
        except Exception as e:
            raise e
