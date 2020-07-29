import os
import sys

from context import AppContext


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    app_context = AppContext(base_dir=base_dir)
    app = app_context.run()
    sys.exit(app)


if __name__ == "__main__":
    main()
