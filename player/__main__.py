import sys

from player import user, vlc_objects
from player.logs import initialize_logging
from player.style import initialize_style
from player.viewpoint import ViewpointManager
from player.window import AppWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


def main():
    initialize_logging()
    user.config.load()

    vlc_objects.Instance([])

    media_paths = sys.argv[1:]
    if media_paths:
        vlc_objects.media_player = vlc_objects.media_player
        vlc_objects.media_player.set_mrl(media_paths[0])

    qapp = QApplication([])
    initialize_style(qapp)

    player_win = AppWindow(flags=Qt.WindowFlags(Qt.WindowStaysOnTopHint))
    player_win.show()

    ViewpointManager(url=user.config.url)

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
