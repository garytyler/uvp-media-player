import sys

from eventvr_player.viewer import PlayerFactory
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication([])

    # player = PlayerFactory(
    #     media_path=sys.argv[1] if len(sys.argv) > 1 else None,
    #     url=sys.argv[2] if len(sys.argv) > 2 else None,
    # )

    player = PlayerFactory(
        media_path="media/360video_2min.mp4",
        url="wss://eventvr.herokuapp.com/mediaplayer",
    )
    player.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
