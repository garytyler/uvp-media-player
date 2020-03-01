import sys

from player.context import AppContext


def main():
    app_context = AppContext()
    app = app_context.run()

    sys.exit(app)


if __name__ == "__main__":
    main()
