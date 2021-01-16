import logging
import os
import sys

import config
from info import BuildInformation
from PyQt5.QtWidgets import QApplication
from utils import cached_property

log = logging.getLogger(__name__)


class BaseAppContext:
    @cached_property
    def base_dir(self):
        if self.is_frozen:
            raise RuntimeError("base_dir not allowed in freeze or release")
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @cached_property
    def is_frozen(self):
        return hasattr(sys, "frozen") and hasattr(sys, "_MEIPASS")

    def get_resource(self, *path_parts):
        bundle_dir = getattr(
            sys, "_MEIPASS", os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        )
        return os.path.join(bundle_dir, *path_parts)


class AppContext(BaseAppContext):
    def __init__(self, args=[]):
        super().__init__()
        self.app = QApplication(args)
        self.app.setOrganizationName(self.build_info["organization"])
        self.app.setApplicationName(self.build_info["name"])
        self.init_logging()
        log.info(
            f"Launching: {self.app.organizationName()}/{self.app.applicationName()}"
        )
        self.init_settings()
        self.init_vlc()

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
        window.load_media(sys.argv[1:])

        return window

    @cached_property
    def build_info(self):
        return BuildInformation(self.get_resource("build.json"))

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

    def init_vlc(self):
        import vlc

        vlc_args = os.environ.get("VLC_ARGS", default="").split()
        vlc.Instance(vlc_args)

    @cached_property
    def ffprobe_cmd(self) -> str:
        """Return command to invoke ffprobe binary. If frozen, use path to binary."""
        if not self.is_frozen:
            return os.environ["FFPROBE_BINARY_PATH"]
        return self.get_resource(
            "ffprobe.exe" if sys.platform.startswith("win") else "ffprobe"
        )

    @cached_property
    def media_player(self):
        import vlcqt

        return vlcqt.MediaPlayer()

    @cached_property
    def stylesheet(self):
        qss_path = self.get_resource("style", "dark.qss")
        with open(qss_path) as stylesheet:
            return stylesheet.read()
