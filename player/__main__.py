import sys

import qtmodern.styles
import qtmodern.windows
from player import factory, logs, style
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


def main():
    logs.initialize_logging(level="DEBUG", color=True)

    qapp = QApplication([])
    # self.setAttribute(Qt.WA_TranslucentBackground)
    # style.set_color_theme("dark")
    # qtmodern.styles.dark(qapp)
    media_paths = []
    # media_paths = ["media/360vid_5sec.mp4"]
    media_paths = ["media/regvid_2min.mp4", "media/regvid_5sec.mp4"]
    url = "wss://eventvr.herokuapp.com/mediaplayer"

    player_factory = factory.PlayerFactory(
        # media_paths=media_paths, url=url, vlc_args=["--verbose=2"]
        media_paths=media_paths,
        url=url,
        vlc_args=[],
    )

    player_factory.player_win.show()

    # mw = qtmodern.windows.ModernWindow(player_factory.player_win)
    # mw.show()

    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()
