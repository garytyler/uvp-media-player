import logging
import sys

import vlc

from . import _facades

log = logging.getLogger(__name__)


vlc.logger.setLevel(0)


__module = sys.modules[__name__]
for key, val in vlc.__dict__.items():
    setattr(__module, key, val)


Instance = _facades.QtVLCInstance
MediaPlayer = _facades.QtVLCMediaPlayer
Media = _facades.QtVLCMedia


def initialize(args: list) -> None:
    """Helper function that initializes the VLC instance singleton with cli args"""
    Instance(args)


log.info(
    f"New QtVLC instance - vlc.plugin_path={vlc.plugin_path}, vlc.dll._name={vlc.dll._name}"
)
