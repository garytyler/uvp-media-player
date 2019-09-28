import os
import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication

from player import vlcqt
from player.gui.style import initialize_style
from player.util import config
from player.util.logs import initialize_logging
from player.window import AppWindow


def main():
    initialize_logging()
    config.state.load()

    vlc_args = os.environ.get("VLC_ARGS", default="").split(",")
    vlcqt.Instance(vlc_args)

    qt_args = os.environ.get("QT_ARGS", default="").split(",")

    appctxt = ApplicationContext()
    # qapp = QApplication(qt_args)

    initialize_style(appctxt.app)
    # qapp.setApplicationDisplayName("Media Player")

    player_win = AppWindow()
    player_win.load_media(sys.argv[1:])

    player_win.show()

    # exit_code = qapp.exec_()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
