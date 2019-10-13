import logging
from ctypes.util import find_library

import vlc

log = logging.getLogger(__name__)


def log_build_info():
    vlc_version = vlc.__version__
    vlclib_library = find_library("vlc")
    vlclib_version = vlc.libvlc_get_version()
    ffmpeg_library = find_library("ffmpeg")
    log.info(
        f"BUILD INFO vlc_version={vlc_version}, vlclib_library={vlclib_library}, vlclib_version={vlclib_version}, ffmpeg_library={ffmpeg_library},"
    )
