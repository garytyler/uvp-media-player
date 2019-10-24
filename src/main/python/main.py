import ctypes
import logging
import os
import sys
from importlib import import_module
from os import environ
from os.path import abspath, join

from fbs_runtime import platform
from fbs_runtime.application_context import cached_property, is_frozen
from fbs_runtime.application_context.PyQt5 import ApplicationContext

log = logging.getLogger(__name__)


class _AppContext(ApplicationContext):
    def __init__(self, args=[]):
        super().__init__()
        self.vlcqt.initialize(args=args)

        # TODO These imports should be fine to import globally, but leaving them here
        # while refactoring other modules is safe, to be sure dependencies are
        # initialized beforehand.
        from gui.style import initialize_style
        from util.logs import initialize_logging
        from util import config

        initialize_logging()
        config.state.load()
        initialize_style(self)

    @cached_property
    def vlcqt(self):
        if is_frozen():
            vlc_resource_dir = self.get_resource("vlc")
            if platform.is_windows():
                environ["PYTHON_VLC_LIB_PATH"] = join(vlc_resource_dir, "libvlc.dll")
                environ["PYTHON_VLC_MODULE_PATH"] = join(vlc_resource_dir)
                # for windows/macOS, load vlccore.dylib into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                ctypes.CDLL(join(vlc_resource_dir, "libvlccore.dll"))
            elif platform.is_ubuntu():
                environ["PYTHON_VLC_MODULE_PATH"] = join(vlc_resource_dir)
                environ["PYTHON_VLC_LIB_PATH"] = join(vlc_resource_dir, "libvlc.so.5")
            elif platform.is_mac():
                environ["PYTHON_VLC_MODULE_PATH"] = join(vlc_resource_dir)
                environ["PYTHON_VLC_LIB_PATH"] = join(vlc_resource_dir, "libvlc.dylib")
                # for windows/macOS, load vlccore.dylib into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                ctypes.CDLL(join(vlc_resource_dir, "libvlccore.dylib"))
            else:
                log.warning("Platform unsupported. App may launch if VLC is installed.")
                environ.unset("PYTHON_VLC_MODULE_PATH")
                environ.unset("PYTHON_VLC_LIB_PATH")
        return import_module("vlcqt")

    @cached_property
    def ffprobe_cmd(self) -> str:
        """Return command to invoke ffprobe binary. If frozen, use path to binary."""
        if is_frozen():
            if platform.is_windows():
                return abspath(self.get_resource(f"ffmpeg/ffprobe.exe"))
            else:
                return abspath(self.get_resource(f"ffmpeg/ffprobe"))
        return "ffprobe"

    @cached_property
    def media_player(self):
        return self.vlcqt.MediaPlayer()

    @cached_property
    def window(self):
        from window import AppWindow

        window = AppWindow(media_player=self.media_player, ffprobe_cmd=self.ffprobe_cmd)
        window.load_media(sys.argv[1:])
        return window

    def run(self):
        self.window.show()
        return self.app.exec_()


def main():
    vlc_args = os.environ.get("VLC_ARGS", default="").split(",")
    app_context = _AppContext(args=vlc_args)

    # Set working dir to user home after context init and before any i/o operations
    os.chdir(os.path.expanduser("~"))

    exit_code = app_context.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
