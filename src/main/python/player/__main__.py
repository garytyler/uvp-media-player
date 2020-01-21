import sys

from player.context import AppContext


def main():
    app_context = AppContext()
    exit_code = app_context.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
