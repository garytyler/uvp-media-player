import sys

# import vlc
from eventvr_player.viewer import PlayerFactory
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication([])

    media_path = sys.argv[1]
    ws_url = sys.argv[2]

    player = PlayerFactory(media_path=media_path, url=ws_url)
    # player = PlayerFactory(url=ws_url)
    player.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
