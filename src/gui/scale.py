import logging

from PyQt5.QtCore import QEvent, QObject, QPoint, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QAction, QActionGroup, QButtonGroup, QMenu, QPushButton

from . import buttons, config, icons, util, vlcqt

log = logging.getLogger(__name__)


class MainMediaFrameSizeController(QObject):
    mediaframerescaled = pyqtSignal(float)

    _default_h = 360
    _default_w = 600

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.mp = vlcqt.media_player
        self.media = self.mp.get_media()
        self.mp.mediachanged.connect(self.conform_to_current_media)

    def set_view_scale(self, scale) -> float:
        self._apply_rescale(scale)
        config.state.view_scale = scale

    def get_base_media_size(self):
        if self.media:
            return util.get_media_size(self.media)
        return self._default_w, self._default_h

    def get_media_size(self, scaled=False):
        if not self.media:
            return self._default_w, self._default_h
        w, h = util.get_media_size(self.media)
        if scaled:
            scale = config.state.view_scale
            return w * scale, h * scale
        return w, h

    def conform_to_current_media(self):
        self.media = self.mp.get_media()
        self._apply_rescale(scale=config.state.view_scale)

    def _apply_rescale(self, scale):
        if self.media:
            w, h = util.get_media_size(self.media)
            self.main_win.resize_to_media(w * scale, h * scale)
        else:
            self.main_win.resize_to_media(self._default_w, self._default_h)
        self.mediaframerescaled.emit(scale)


class ViewScaleMenu(QMenu):
    def __init__(self, main_win):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_ctrlr = self.main_win.frame_size_ctrlr

        # self.frame_size_ctrlr = self.main_win.media_frame.frame_size_ctrlr

        self.setTitle("Zoom")

        self.quarter = QAction("1:4 Quarter", self)
        self.quarter.triggered.connect(lambda: self.set_view_scale(0.25))
        self.quarter.setCheckable(True)

        self.half = QAction("1:2 Half", self)
        self.half.triggered.connect(lambda: self.set_view_scale(0.5))
        self.half.setCheckable(True)

        self.original = QAction("1:1 Original", self)
        self.original.triggered.connect(lambda: self.set_view_scale(1))
        self.original.setCheckable(True)

        self.double = QAction("1:2 Double", self)
        self.double.triggered.connect(lambda: self.set_view_scale(2))
        self.double.setCheckable(True)

        self.zoom_in = QAction("Zoom In", self)
        self.zoom_in.triggered.connect(self._zoom_in)
        self.zoom_in.setIcon(icons.zoom_in["normal"])

        self.zoom_out = QAction("Zoom Out", self)
        self.zoom_out.triggered.connect(self._zoom_out)
        self.zoom_out.setIcon(icons.zoom_out["normal"])

        self.explicit_zooms = QActionGroup(self)
        self.explicit_zooms.addAction(self.quarter)
        self.explicit_zooms.addAction(self.half)
        self.explicit_zooms.addAction(self.original)
        self.explicit_zooms.addAction(self.double)

        self.addActions(self.explicit_zooms.actions())
        self.addAction(self.zoom_in)
        self.addAction(self.zoom_out)

        for a in self.actions():
            a.setEnabled(vlcqt.media_player.has_media)

        self.config_options = sorted(config.options.view_scale)

        self.option_enum_map = {}
        for index, option in enumerate(sorted(self.config_options)):
            self.option_enum_map[option] = index

        self.option_action_map = {
            0.25: self.quarter,
            0.5: self.half,
            1: self.original,
            2: self.double,
        }

        vlcqt.media_player.mediachanged.connect(self.on_mediachanged)
        self.frame_size_ctrlr.mediaframerescaled.connect(self.on_mediaframerescaled)

    def set_view_scale(self, value):
        self.frame_size_ctrlr.set_view_scale(value)

    def on_mediaframerescaled(self, value: float):
        if value == self.config_options[0]:
            self.zoom_in.setEnabled(True)
            self.zoom_out.setEnabled(False)
            log.warning(f"'{value}' is the minimum configured value for 'Zoom In'")
        elif value == self.config_options[-1]:
            self.zoom_in.setEnabled(False)
            self.zoom_out.setEnabled(True)
            log.warning(f"'{value}' is the maximum configured value for 'Zoom In'")
        else:
            self.zoom_in.setEnabled(True)
            self.zoom_out.setEnabled(True)

    def _zoom_in(self):
        index = self.option_enum_map[config.state.view_scale] + 1
        try:
            value = config.options.view_scale[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_view_scale(value)

    def _zoom_out(self, value):
        index = self.option_enum_map[config.state.view_scale] - 1
        try:
            value = config.options.view_scale[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_view_scale(value)

    def on_mediachanged(self):
        has_media = vlcqt.media_player.has_media
        for a in self.actions():
            a.setEnabled(has_media)
        self.option_action_map[config.state.view_scale].setChecked(True)


class ViewScaleButton(buttons.SquareMenuButton):
    def __init__(self, view_scale_menu, parent, size=None):
        super().__init__(
            parent=parent, menu=view_scale_menu, size=size, icons=icons.zoom_menu_button
        )
        self.setToolTip("Zoom")
        self.curr_icon = icons.zoom_menu_button
        self.update_icon_hover()
        self.clicked.connect(self.open_menu)


class ZoomInButton(buttons.SquareIconButton):
    def __init__(self, frame_size_ctrlr, parent, size=None):
        super().__init__(parent=parent, icons=icons.zoom_in_button)
        self.curr_icon = icons.zoom_in_button
        self.update_icon_hover()

        self.frame_size_ctrlr = frame_size_ctrlr
        self.config_options = config.options.view_scale

        self.frame_size_ctrlr.mediaframerescaled.connect(self.on_mediaframerescaled)
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.frame_size_ctrlr

    def on_mediaframerescaled(self, value):
        self.setEnabled(value != self.config_options[-1])


class ZoomOutButton(buttons.SquareIconButton):
    def __init__(self, frame_size_ctrlr, parent, size=None):
        super().__init__(parent=parent, icons=icons.zoom_out_button)

        self.curr_icon = icons.zoom_out_button
        self.update_icon_hover()

        self.frame_size_ctrlr = frame_size_ctrlr
        self.config_options = config.options.view_scale

        self.frame_size_ctrlr.mediaframerescaled.connect(self.on_mediaframerescaled)
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        pass
        # is_checked = self.isChecked()

    def on_mediaframerescaled(self, value):
        self.setEnabled(value != self.config_options[0])
