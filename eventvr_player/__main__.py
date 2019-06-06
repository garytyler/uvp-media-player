import sys

import vlc
from eventvr_player.viewer import PlayerGUI
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication([])

    media_path = sys.argv[1]
    ws_url = sys.argv[2]

    vlcmediaplayer = vlc.MediaPlayer(media_path)

    player = PlayerGUI(vlcmediaplayer=vlcmediaplayer, url=ws_url)
    player.show()
    player.play()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
