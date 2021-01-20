import sys

from app.context import AppContext


def run(*args, **kwargs):
    context = AppContext(*args, **kwargs)
    context.main_win.show()
    sys.exit(context.app.exec_())


if __name__ == "__main__":
    run(files=sys.argv[1:])
