import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QFileDialog, QMenu

from . import config, picture, vlc_objects, window

log = logging.getLogger(__name__)


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


class ZoomMenu(QMenu):
    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.main_win = main_win

        self.setTitle("Zoom")

        self.quarter = QAction("1:4 Quarter", self)
        self.quarter.triggered.connect(lambda: self.set_zoom(0.25))
        self.quarter.setCheckable(True)

        self.half = QAction("1:2 Half", self)
        self.half.triggered.connect(lambda: self.set_zoom(0.5))
        self.half.setCheckable(True)

        self.original = QAction("1:1 Original", self)
        self.original.triggered.connect(lambda: self.set_zoom(1))
        self.original.setCheckable(True)

        self.double = QAction("1:2 Double", self)
        self.double.triggered.connect(lambda: self.set_zoom(2))
        self.double.setCheckable(True)

        self.zoom_in = QAction("Zoom In", self)
        self.zoom_in.triggered.connect(self._zoom_in)

        self.zoom_out = QAction("Zoom Out", self)
        self.zoom_out.triggered.connect(self._zoom_out)

        self.explicit_zooms = QActionGroup(self)
        self.explicit_zooms.addAction(self.quarter)
        self.explicit_zooms.addAction(self.half)
        self.explicit_zooms.addAction(self.original)
        self.explicit_zooms.addAction(self.double)
        self.explicit_zooms.setExclusive(True)

        self.addActions(self.explicit_zooms.actions())
        self.addAction(self.zoom_in)
        self.addAction(self.zoom_out)

        for a in self.actions():
            a.setEnabled(vlc_objects.media_player.has_media)

        self.option_enum_map = {}
        for index, option in enumerate(sorted(config.options.zoom)):
            self.option_enum_map[option] = index

        self.option_action_map = {
            0.25: self.quarter,
            0.5: self.half,
            1: self.original,
            2: self.double,
        }

        self.option_action_map[config.state.zoom].trigger()
        vlc_objects.media_player.mediachanged.connect(self.on_mediachanged)

    def set_zoom(self, value):
        picture.media_zoomer.set_zoom(value)
        sorted_values = sorted(config.options.zoom)
        if value == sorted_values[0]:
            log.warning(f"'{value}' is the minimum configured value for 'Zoom In'")
            self.zoom_in.setEnabled(True)
            self.zoom_out.setEnabled(False)
        elif value == sorted_values[-1]:
            log.warning(f"'{value}' is the maximum configured value for 'Zoom In'")
            self.zoom_in.setEnabled(False)
            self.zoom_out.setEnabled(True)
        else:
            self.zoom_in.setEnabled(True)
            self.zoom_out.setEnabled(True)

    def _zoom_in(self):
        index = self.option_enum_map[config.state.zoom] + 1
        try:
            value = config.options.zoom[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_zoom(value)

    def _zoom_out(self, value):
        index = self.option_enum_map[config.state.zoom] - 1
        try:
            value = config.options.zoom[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_zoom(value)

    def on_mediachanged(self):
        has_media = vlc_objects.media_player.has_media
        for a in self.actions():
            a.setEnabled(has_media)
        self.option_action_map[config.state.zoom].trigger()
