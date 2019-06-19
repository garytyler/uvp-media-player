from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QFileDialog

from . import config, picture, window


class ExitApp(QAction):
    def __init__(self, parent=None):
        super().__init__(text="Exit", parent=parent)
        self.qapp = QApplication.instance()
        self.triggered.connect(self.qapp.closeAllWindows)


class StayOnTop(QAction):
    def __init__(self, main_win=None):
        super().__init__(text="Stay on top", parent=main_win)
        self.main_win = main_win
        self.setCheckable(True)
        self.setChecked(config.state.stay_on_top)
        self.triggered.connect(self._on_triggered)

    def _on_triggered(self, checked):
        if checked:
            _args = self.main_win.windowFlags() | Qt.WindowStaysOnTopHint
            self.main_win.setWindowFlags(_args)
            self.main_win.show()
        else:
            _args = self.main_win.windowFlags() & ~Qt.WindowStaysOnTopHint
            self.main_win.setWindowFlags(_args)
        config.state.stay_on_top = checked


class ZoomMenu(window.MenuBase):
    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.main_win = main_win

        self.setTitle("Zoom")

        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)

        quarter = QAction("1:4 Quarter", self)
        quarter.triggered.connect(lambda: self._set_zoom(0.25))
        quarter.setCheckable(True)

        half = QAction("1:2 Half", self)
        half.triggered.connect(lambda: self._set_zoom(0.5))
        half.setCheckable(True)

        original = QAction("1:1 Original", self)
        original.triggered.connect(lambda: self._set_zoom(1))
        original.setCheckable(True)

        double = QAction("1:2 Double", self)
        double.triggered.connect(lambda: self._set_zoom(2))
        double.setCheckable(True)

        self.action_group.addAction(quarter)
        self.action_group.addAction(half)
        self.action_group.addAction(original)
        self.action_group.addAction(double)
        self.addActions(self.action_group.actions())

        for a in self.actions():
            a.setEnabled(self.mp.has_media)

        self.mp.mediachanged.connect(self._on_mediachanged)

    def _set_zoom(self, value):
        picture.media_zoomer.set_zoom(value)

    def _on_mediachanged(self):
        for a in self.actions():
            a.setEnabled(self.mp.has_media)
