import ctypes
import logging
import os
import sys
from importlib import import_module
from os import environ
from os.path import abspath, dirname, join

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
        from player.gui.style import initialize_style
        from player.util.logs import initialize_logging
        from player.util import config

        initialize_logging()
        config.state.load()
        initialize_style(self)

    @cached_property
    def vlcqt(self):
        if is_frozen():
            if platform.is_ubuntu():
                environ["PYTHON_VLC_LIB_PATH"] = self.get_resource("libvlc.so")
                environ["PYTHON_VLC_MODULE_PATH"] = self.get_resource("plugins")
            elif platform.is_windows():
                environ["PYTHON_VLC_LIB_PATH"] = self.get_resource("libvlc.dll")
                environ["PYTHON_VLC_MODULE_PATH"] = self.get_resource("plugins")
                # for windows/macOS, load libvlccore into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                ctypes.CDLL(self.get_resource("libvlccore.dll"))
            elif platform.is_mac():
                vlc_bin_dir = join(dirname(self.get_resource()), "MacOS")
                environ["PYTHON_VLC_LIB_PATH"] = join(vlc_bin_dir, "libvlc.dylib")
                environ["PYTHON_VLC_MODULE_PATH"] = join(vlc_bin_dir, "plugins")
                # for windows/macOS, load libvlccore into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                ctypes.CDLL(join(vlc_bin_dir, "libvlccore.dylib"))
            else:
                log.warning("Platform unsupported. App may launch if VLC is installed.")
                environ.unset("PYTHON_VLC_MODULE_PATH")
                environ.unset("PYTHON_VLC_LIB_PATH")
        return import_module(name="player.vlcqt")

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
        from player.window import AppWindow

        window = AppWindow(media_player=self.media_player, ffprobe_cmd=self.ffprobe_cmd)
        if is_frozen():
            media_paths = sys.argv[1:]
        else:
            media_paths = environ.get("_SEEVR_PLAYER_BUILD_LAUNCH_MEDIA", "").split(",")
        window.load_media(media_paths)
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
