from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QApplication

from .. import config


class ExitApp(QAction):
    def __init__(self, parent=None):
        super().__init__(text="Exit", parent=parent)
        self.qapp = QApplication.instance()
        self.triggered.connect(self.qapp.closeAlls)


class StayOnTop(QAction):
    def __init__(self, main_win=None):
        super().__init__(text="Stay on top", parent=main_win)
        self.main_win = main_win
        self.setCheckable(True)
        self.triggered.connect(self.on_triggered)
        self.main_win.initialized.connect(
            lambda: self.triggered.emit(config.state.stay_on_top)
        )

    def on_triggered(self, checked):
        if checked:
            self._enable()
        else:
            self._disable()
        # Sync state
        config.state.stay_on_top = checked
        self.setChecked(checked)

    def _enable(self):
        _args = self.main_win.windowFlags() | Qt.WindowStaysOnTopHint
        self.main_win.setWindowFlags(_args)
        self.main_win.show()

    def _disable(self):
        _args = self.main_win.windowFlags() & ~Qt.WindowStaysOnTopHint
        self.main_win.setWindowFlags(_args)
        self.main_win.show()
