import os
import sys

from PyQt5.QtWidgets import QApplication
from src import config, vlcqt
from src.gui.main import AppWindow
from src.gui.style import initialize_style
from src.logs import initialize_logging


def main():
    initialize_logging()
    config.state.load()

    vlc_args = os.environ.get("VLC_ARGS", default="").split(",")
    vlcqt.Instance(vlc_args)

    qt_args = os.environ.get("QT_ARGS", default="").split(",")
    qapp = QApplication(qt_args)

    initialize_style(qapp)

    player_win = AppWindow(media_paths=sys.argv[1:])
    player_win.show()

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
