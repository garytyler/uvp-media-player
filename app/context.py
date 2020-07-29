import ctypes
import logging
import os
import sys
from importlib import import_module
from os import environ
from os.path import abspath, dirname, join

import config
from PyQt5.QtWidgets import QApplication

# from fbs_runtime.application_context import is_frozen
from utils import cached_property

log = logging.getLogger(__name__)


class AppContext:
    def __init__(self, base_dir, args=[]):
        super().__init__()
        self.base_dir = base_dir
        self.app = QApplication(args)
        self.app.setOrganizationName("UVP")
        self.app.setApplicationName("SeeVR Player")
        self.init_logging()
        log.info(
            f"Launching: {self.app.organizationName()}/{self.app.applicationName()}"
        )
        self.init_settings()
        self.init_vlcqt()

    def init_logging(self):
        # Set player log file
        player_log_file = os.getenv("VR_PLAYER_LOG_FILE", None)
        if player_log_file:
            dirpath, filename = os.path.split(player_log_file)
            if dirpath:
                os.makedirs(os.path.dirname(dirpath), exist_ok=True)
            logger = logging.getLogger()
            logger.addHandler(logging.FileHandler(player_log_file))
            logger.info("INIT LOGGING")

        # Set player log levels
        player_log_levels = os.getenv("VR_PLAYER_LOG_LEVELS", "")
        for name, level in (i.split(":") for i in player_log_levels.split(",") if i):
            logger = logging.getLogger(name)
            logger.setLevel(level)
            logger.info(f"SET LOGGER LOG LEVEL name={name} level={level}")

    def init_settings(self):
        settings = config.Settings(
            self.app.organizationName(), self.app.applicationName()
        )
        log.info(f"Configuration file: {settings.fileName()}")
        config.state.load(settings)

    def init_vlcqt(self):
        vlc_args = os.environ.get("VLC_ARGS", default="").split()
        disable_hw_accel_arg = "--avcodec-hw=none"
        already = bool(disable_hw_accel_arg in vlc_args)
        if config.state.hw_accel and not already:
            vlc_args.append(disable_hw_accel_arg)
        self.vlcqt.initialize(args=vlc_args)

    @cached_property
    def vlcqt(self):
        # if is_frozen():
        #     if sys.platform.startswith("linux"):
        #         environ["PYTHON_VLC_LIB_PATH"] = self.get_resource("libvlc.so")
        #         environ["PYTHON_VLC_MODULE_PATH"] = self.get_resource("plugins")
        #     elif sys.platform == "win64":
        #         environ["PYTHON_VLC_LIB_PATH"] = self.get_resource("libvlc.dll")
        #         environ["PYTHON_VLC_MODULE_PATH"] = self.get_resource("plugins")
        #         # for windows/macOS, load libvlccore into mem before llibvlc.dylib
        #         # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
        #         ctypes.CDLL(self.get_resource("libvlccore.dll"))
        #     elif sys.platform == "darwin":
        #         vlc_bin_dir = join(dirname(self.get_resource()), "MacOS")
        #         environ["PYTHON_VLC_LIB_PATH"] = join(vlc_bin_dir, "libvlc.dylib")
        #         environ["PYTHON_VLC_MODULE_PATH"] = join(vlc_bin_dir, "plugins")
        #         # for windows/macOS, load libvlccore into mem before llibvlc.dylib
        #         # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
        #         ctypes.CDLL(join(vlc_bin_dir, "libvlccore.dylib"))
        #     else:
        #         log.warning("Platform unsupported. App may launch if VLC is installed.")
        #         environ.unset("PYTHON_VLC_MODULE_PATH")
        #         environ.unset("PYTHON_VLC_LIB_PATH")
        return import_module(name="vlcqt")

    @cached_property
    def ffprobe_cmd(self) -> str:
        """Return command to invoke ffprobe binary. If frozen, use path to binary."""
        # if is_frozen():
        #     if sys.platform == "win64":
        #         return abspath(os.path.join(self.base_dir, "ffmpeg", "ffprobe.exe"))
        #     else:
        #         return abspath(os.path.join(self.base_dir, "ffmpeg", "ffprobe"))
        return "ffprobe"

    @cached_property
    def media_player(self):
        return self.vlcqt.MediaPlayer()

    @cached_property
    def stylesheet(self):
        qss_path = os.path.join(self.base_dir, "resources", "style", "dark.qss")
        with open(qss_path) as stylesheet:
            return stylesheet.read()

    @cached_property
    def main_win(self):
        from mainwindow import MainWindow

        window = MainWindow(
            media_player=self.media_player,
            ffprobe_cmd=self.ffprobe_cmd,
            stylesheet=self.stylesheet,
        )
        window.load_media(media_path_args())
        return window

    def run(self):
        self.main_win.show()
        return self.app.exec_()


def media_path_args():
    # if not is_frozen():
    build_script_run_args = environ.get("_BUILD_SCRIPT_RUN_ARGS", "").split(",")
    media_paths = [i for i in build_script_run_args if i.strip()]
    if media_paths:
        return media_paths
    return sys.argv[1:]
