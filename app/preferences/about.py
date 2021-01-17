import logging
from ctypes.util import find_library

from PyQt5 import QtWidgets

from app import vlcqt

log = logging.getLogger(__name__)


def vlclib_library():
    return find_library("vlc")


def ffmpeg_library():
    return find_library("ffmpeg")


def vlc_version():
    return vlcqt.__version__


def libvlc_version():
    return vlcqt.libvlc_get_version().decode("utf-8")


class AboutTextLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        versions_text = f"""VLC: {vlc_version()}
libVLC: {libvlc_version()}"""
        self.setText(versions_text)
