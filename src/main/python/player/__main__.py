import sys

from player.context import AppContext


def main():
    app_context = AppContext()
    sys.exit(app_context.run())


if __name__ == "__main__":
    main()
