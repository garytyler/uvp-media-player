import sys

from player import config, vlc_objects
from player.logs import initialize_logging
from player.style import initialize_style
from player.viewpoint import ViewpointManager
from player.window import AppWindow
from PyQt5.QtWidgets import QApplication


def main():
    initialize_logging()
    config.state.load()

    vlc_objects.Instance([])

    media_paths = sys.argv[1:]
    if media_paths:
        vlc_objects.media_player.set_mrl(media_paths[0])

    qapp = QApplication([])
    initialize_style(qapp)

    player_win = AppWindow()
    player_win.show()

    ViewpointManager(url=config.state.url)

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
