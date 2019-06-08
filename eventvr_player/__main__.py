import sys

from PyQt5.QtWidgets import QApplication
from viewer import PlayerFactory


def main():
    app = QApplication([])

    player = PlayerFactory(
        media_path=sys.argv[1] if len(sys.argv) > 1 else None,
        url=sys.argv[2] if len(sys.argv) > 2 else None,
    )
    player.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
