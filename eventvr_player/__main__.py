import os
import sys

from eventvr_player.logs import initialize_logging
from eventvr_player.viewer import PlayerFactory
from PyQt5.QtWidgets import QApplication

# from eventvr_player.logs import initialize_logging


def main():
    initialize_logging(level="DEBUG", color=True)

    app = QApplication([])
    player = PlayerFactory(
        media_path="media/360video_2min.mp4",
        url="wss://eventvr.herokuapp.com/mediaplayer",
    )
    player.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
