import os
import sys

from eventvr_player.logs import initialize_logging
from eventvr_player.window import PlayerFactory
from PyQt5.QtWidgets import QApplication


def main():
    initialize_logging(level="DEBUG", color=True)

    app = QApplication([])

    media_paths = ["media/360video_5sec.mp4" for i in range(5)]
    url = "wss://eventvr.herokuapp.com/mediaplayer"

    player_factory = PlayerFactory(media_paths=media_paths, url=url)
    player_factory.player_win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
