from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QToolButton

from ..gui import icons
from ..util import config


def get_always_on_top(window):
    value = window.windowFlags() & Qt.WindowStaysOnTopHint
    return value


def set_always_on_top(window, value):
    if value:
        if not get_always_on_top(window):
            _args = window.windowFlags() | Qt.WindowStaysOnTopHint
            window.setWindowFlags(_args)
            window.show()
    else:
        if get_always_on_top(window):
            _args = window.windowFlags() & ~Qt.WindowStaysOnTopHint
            window.setWindowFlags(_args)
            window.show()


class AlwaysOnTopAction(QAction):
    def __init__(self, main_win=None):
        super().__init__(text="Always On Top", parent=main_win)
        self.main_win = main_win

        self.setIcon(icons.always_on_top)
        self.setCheckable(True)

        self.triggered.connect(self.on_triggered)

        if hasattr(self.main_win, "initialized"):
            self.main_win.initialized.connect(
                lambda: self.triggered.emit(config.state.stay_on_top)
            )

    def on_triggered(self, checked):
        set_always_on_top(self.main_win, checked)
        config.state.stay_on_top = checked
        self.setChecked(checked)
