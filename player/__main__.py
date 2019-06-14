import sys

from player import factory, logs
from PyQt5.QtWidgets import QApplication


def main():
    logs.initialize_logging(level="DEBUG", color=True)

    app = QApplication([])

    media_paths = ["media/360video_5sec.mp4" for i in range(5)]
    url = "wss://eventvr.herokuapp.com/mediaplayer"

    player_factory = factory.PlayerFactory(
        # media_paths=media_paths, url=url, vlc_args=["--verbose=2"]
        media_paths=media_paths,
        url=url,
        vlc_args=[],
    )
    player_factory.player_win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
