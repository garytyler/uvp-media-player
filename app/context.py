import ctypes
import logging
import os
import sys
from importlib import import_module
from os import environ

from PyQt5.QtWidgets import QApplication

import config
from utils import cached_property, platform

log = logging.getLogger(__name__)


class BaseAppContext:
    @cached_property
    def base_dir(self):
        if self.is_frozen:
            raise RuntimeError("base_dir not allowed in freeze or release")
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @cached_property
    def is_frozen(self):
        result = getattr(sys, "frozen", False)
        return result

    @cached_property
    def is_not_installed(self):
        return True if os.environ.get("NOT_INSTALLED", False) else False

    def get_resource(self, *path_parts):
        if not self.is_frozen:
            resources_dir = self.base_dir
        elif self.is_not_installed:
            resources_dir = (
                os.path.join(os.path.dirname(sys.executable))
                if not platform.is_linux
                else self.base_dir
            )
        elif platform.is_linux:
            resources_dir = os.path.join("/", "usr", "share", "seevr-player")
        else:
            resources_dir = os.path.join(os.path.dirname(sys.executable))
        return os.path.join(resources_dir, *path_parts)

    def get_frozen_resource(self, *path_parts):
        if platform.is_linux:
            resources_dir = os.path.join("/", "usr", "share", "seevr-player")
        else:
            resources_dir = os.path.join(os.path.dirname(sys.executable))
        return os.path.join(resources_dir, *path_parts)


class AppContext(BaseAppContext):
    def __init__(self, args=[]):
        super().__init__()
        self.app = QApplication(args)
        self.app.setOrganizationName("UVP")
        self.app.setApplicationName("SeeVR-Player")
        self.init_logging()
        log.info(
            f"Launching: {self.app.organizationName()}/{self.app.applicationName()}"
        )
        self.init_settings()
        self.init_vlcqt()

    def run(self):
        self.main_win.show()
        return self.app.exec_()

    @cached_property
    def main_win(self):
        from mainwindow import MainWindow

        window = MainWindow(
            media_player=self.media_player,
            ffprobe_cmd=self.ffprobe_cmd,
            stylesheet=self.stylesheet,
        )

        if self.is_frozen:
            media_paths = sys.argv[1:]
        else:
            build_script_run_args = environ.get("_BUILD_SCRIPT_RUN_ARGS", "").split(",")
            media_paths = [i for i in build_script_run_args if i.strip()]

        window.load_media(media_paths)
        return window

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
        self.vlcqt.initialize(args=vlc_args)

    @cached_property
    def vlcqt(self):
        if self.is_frozen:
            if platform.is_linux:  # bundled vlc
                for i in ["PYTHON_VLC_MODULE_PATH", "PYTHON_VLC_LIB_PATH"]:
                    try:
                        del os.environ[i]
                    except KeyError:
                        pass

            elif platform.is_windows:  # bundled vlc
                environ["PYTHON_VLC_LIB_PATH"] = self.get_resource("libvlc.dll")
                environ["PYTHON_VLC_MODULE_PATH"] = self.get_resource("plugins")
                # for windows/macOS, load libvlccore into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                ctypes.CDLL(self.get_frozen_resource("libvlccore.dll"))
            elif platform.is_mac:  # separate vlc installation required
                for i in ["PYTHON_VLC_MODULE_PATH", "PYTHON_VLC_LIB_PATH"]:
                    try:
                        del os.environ[i]
                    except KeyError:
                        pass
                # for windows/macOS with bundled vlc, load libvlccore into mem before llibvlc.dylib
                # see python-vlc source: v3.0.7110, vlc.py, find_lib, line 178
                # # ctypes.CDLL(os.path.join(vlc_bin_dir, "libvlccore.dylib"))
            else:
                for i in ["PYTHON_VLC_MODULE_PATH", "PYTHON_VLC_LIB_PATH"]:
                    try:
                        del os.environ[i]
                    except KeyError:
                        pass
                log.warning(
                    f"Platform unsupported: '{sys.platform}'"
                    "If problems, try installing VLC."
                )

        return import_module(name="vlcqt")

    @cached_property
    def ffprobe_cmd(self) -> str:
        """Return command to invoke ffprobe binary. If frozen, use path to binary."""
        if not self.is_frozen:
            return os.environ["FFPROBE_BINARY_PATH"]
        elif platform.is_linux:
            return "ffprobe"
        else:
            return self.get_resource(
                "ffmpeg", "ffprobe.exe" if platform.is_windows else "ffprobe"
            )

    @cached_property
    def media_player(self):
        return self.vlcqt.MediaPlayer()

    @cached_property
    def stylesheet(self):

        qss_path = self.get_resource("style", "dark.qss")
        with open(qss_path) as stylesheet:
            return stylesheet.read()
