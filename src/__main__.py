import sys

from PyQt5.QtWidgets import QApplication
from src import config, vlcqt
from src.gui.main import AppWindow
from src.gui.style import initialize_style
from src.logs import initialize_logging


def main():
    initialize_logging()
    config.state.load()

    vlcqt.Instance([])

    qapp = QApplication([])

    initialize_style(qapp)

    player_win = AppWindow()
    player_win.show()

    media_paths = sys.argv[1:]
    if media_paths:
        vlcqt.list_player.set_mrls(media_paths)

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
