import sys

from player import factory, logs, style
from PyQt5.QtWidgets import QApplication


def main():
    logs.initialize_logging(level="DEBUG", color=True)

    qapp = QApplication([])

    qapp.setStyle("fusion")
    style.set_color_theme("dark")

    media_paths = ["media/regvid_2min.mp4", "media/regvid_5sec.mp4"]
    url = "wss://eventvr.herokuapp.com/mediaplayer"

    player_factory = factory.PlayerFactory(
        media_paths=media_paths, url=url, vlc_args=[]
    )

    player_factory.player_win.show()

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
