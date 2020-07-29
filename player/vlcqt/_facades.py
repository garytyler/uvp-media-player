import logging
import sys

import vlc

from . import _signals

log = logging.getLogger(__name__)


class QtVLCInstance:
    _vlc_obj = None

    def __new__(cls, args=[]):
        args = [i for i in args if i.strip()]
        if cls._vlc_obj:
            return cls._vlc_obj
        cls._vlc_obj = vlc.Instance(args)

    def __init__(self, args=[]):
        pass


class QtVLCMediaPlayer(_signals.MediaPlayerSignals):
    _vlc_obj = None

    def __init__(self):
        self._vlc_obj = vlc.MediaPlayer(QtVLCInstance())
        super().__init__(vlc_media_player=self._vlc_obj)

    def __getattr__(self, attribute):
        return getattr(self._vlc_obj, attribute)

    def _set_output_to_widget(self, widget):
        if sys.platform.startswith("linux"):  # for Linux X Server
            self.set_xwindow(widget.winId())
        elif sys.platform == "win32":  # for Windows
            self.set_hwnd(widget.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.set_nsobject(int(widget.winId()))
        else:
            raise EnvironmentError("Could not determine platform")

    def set_output_widget(self, widget):
        state = self.get_state()
        time = self.get_time()
        if state in [vlc.State.Buffering, vlc.State.Playing]:
            time = self.get_time()
            self.stop()
            self._set_output_to_widget(widget=widget)
            self.play()
            self.set_time(time)
        elif state in [vlc.State.Opening]:
            self.stop()
            self._set_output_to_widget(widget=widget)
            self.play()
        elif state in [vlc.State.Paused]:
            self.stop()
            self._set_output_to_widget(widget=widget)
            self.play()
            self.set_time(time)
            self.pause()
        elif state in [vlc.State.Ended]:
            self.stop()
            self._set_output_to_widget(widget=widget)
            self.play()
            self.pause()
            self.set_time(-1)
        elif state in [vlc.State.Stopped, vlc.State.Error, vlc.State.NothingSpecial]:
            self.play()
            self._set_output_to_widget(widget=widget)
            self.stop()


class QtVLCMedia(_signals.MediaVlclibSignals):
    def __init__(self, mrl, *options):
        self._vlc_obj = vlc.Media(mrl, *options)
        super().__init__(vlc_media=self._vlc_obj)

    def __getattr__(self, attribute):
        try:
            return getattr(self._vlc_obj, attribute)
        except Exception as e:
            raise e
