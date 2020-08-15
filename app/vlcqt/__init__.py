import logging
import sys

import vlc

from . import _facades

log = logging.getLogger(__name__)


vlc.logger.setLevel(0)


__module = sys.modules[__name__]
for key, val in vlc.__dict__.items():
    setattr(__module, key, val)


MediaPlayer = _facades.QtVLCMediaPlayer
Media = _facades.QtVLCMedia
