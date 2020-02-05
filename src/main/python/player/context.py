import ctypes
import logging
import os
import sys
from player.common.utils import cached_property
from importlib import import_module
from os import environ
from os.path import abspath, dirname, join

from fbs_runtime import platform
from fbs_runtime.application_context import is_frozen
from fbs_runtime.application_context.PyQt5 import ApplicationContext

log = logging.getLogger(__name__)


class AppContext(ApplicationContext):
    def __init__(self, args=[]):
        super().__init__()
        self.app.setOrganizationName(self.build_settings["org_name"])
        self.app.setApplicationName(self.build_settings["app_name"])
        self.initialize_logging()
        log.info(
            f"Launching: {self.app.organizationName()}/{self.app.applicationName()}"
        )
        self.initialize_vlcqt()

    def initialize_vlcqt(self):
        vlc_args = os.environ.get("VLC_ARGS", default=None)
        self.vlcqt.initialize(args=vlc_args.split() if vlc_args else [])

    def initialize_logging(self):
        # Set player log file
        player_log_file = os.getenv("VR_PLAYER_LOG_FILE", None)
        if player_log_file:
            dirpath, filename = os.path.split(player_log_file)
            if dirpath:
                os.makedirs(os.path.dirname(dirpath), exist_ok=True)
            logger = logging.getLogger()
            logger.addHandler(logging.FileHandler(player_log_file))
            logger.info(f"INIT LOGGING")

        # Set player log levels
        player_log_levels = os.getenv("VR_PLAYER_LOG_LEVELS", "")
        for name, level in (i.split(":") for i in player_log_levels.split(",") if i):
            logger = logging.getLogger(name)
            logger.setLevel(level)
            logger.info(f"SET LOGGER LOG LEVEL name={name} level={level}")

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
    def settings(self):
        from player import config
        from player.config import state
        from player.gui.style import initialize_style

        settings = config.Settings(
            self.app.organizationName(), self.app.applicationName()
        )
        log.info(f"Configuration file: {settings.fileName()}")
        state.load(settings)
        initialize_style(self.app, self.stylesheet)
        return settings

    @cached_property
    def stylesheet(self):
        with open(self.get_resource("style/dark.qss")) as stylesheet:
            return stylesheet.read()

    @cached_property
    def main_win(self):
        from player.window import AppWindow

        window = AppWindow(
            media_player=self.media_player,
            ffprobe_cmd=self.ffprobe_cmd,
            settings=self.settings,
            stylesheet=self.stylesheet,
        )
        if is_frozen():
            media_paths = sys.argv[1:]
        else:
            media_paths = environ.get("_SEEVR_PLAYER_BUILD_LAUNCH_MEDIA", "").split(",")
        window.load_media(media_paths)
        return window

    def run(self):
        self.main_win.show()
        return self.app.exec_()
