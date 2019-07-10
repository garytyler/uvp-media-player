import logging

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QToolButton

from .. import vlcqt
from ..controls import base
from ..frame.items import ContentFrameItem
from ..gui import icons
from ..util import config

log = logging.getLogger(__name__)


class FrameSizeController(QObject):
    mediaframerescaled = pyqtSignal(float)
    mediaframeresized = pyqtSignal(float)

    _default_h = 360
    _default_w = 600

    def __init__(self, main_win, viewpoint_manager):
        super().__init__()
        self.vp_manager = viewpoint_manager
        self.main_win = main_win
        self.mp = vlcqt.media_player
        self.media = self.mp.get_media()
        self.mp.mediachanged.connect(self.vp_manager.trigger_redraw)
        self.mediaframerescaled.connect(self.vp_manager.trigger_redraw)

    def rescale_frame(self, scale) -> float:
        self._apply_rescale(scale)
        config.state.view_scale = scale

    def get_current_media_size(self):
        content_view = ContentFrameItem(self.media)
        return content_view.width(), content_view.height()

    def conform_to_media(self, media: vlcqt.Media = None):
        """If media arg is None, current media_player media is used"""
        self.media = media if media else self.mp.get_media()
        self._apply_rescale(scale=config.state.view_scale)

    def _apply_rescale(self, scale):
        if self.media:
            w, h = self.get_current_media_size()
            self.main_win.resize_to_media(w * scale, h * scale)
        else:
            self.main_win.resize_to_media(self._default_w, self._default_h)
        self.mediaframerescaled.emit(scale)


class FrameScaleController(QMenu):
    scalechanged = pyqtSignal(float)

    def __init__(self, main_win, frame_size_ctrlr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_ctrlr = frame_size_ctrlr

        for a in self.actions():
            a.setEnabled(vlcqt.media_player.has_media)

        self.config_options = sorted(config.options.view_scale)

        self.option_enum_map = {}
        for index, option in enumerate(sorted(self.config_options)):
            self.option_enum_map[option] = index

        self.frame_size_ctrlr.mediaframerescaled.connect(self.on_mediaframerescaled)

    def set_scale(self, value):
        self.frame_size_ctrlr.rescale_frame(value)

    def on_mediaframerescaled(self, value: float):
        self.scalechanged.emit(value)

    def zoom_in(self):
        index = self.option_enum_map[config.state.view_scale] + 1
        try:
            value = self.config_options[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_scale(value)

    def zoom_out(self):
        index = self.option_enum_map[config.state.view_scale] - 1
        try:
            value = self.config_options[index]
        except IndexError as e:
            log.error(e)
        else:
            self.set_scale(value)


class ZoomInAction(QAction):
    def __init__(self, parent, frame_scale_ctrlr, size=None):
        super().__init__(parent=parent)
        self.frame_scale_ctrlr = frame_scale_ctrlr

        self.setText("Zoom In")
        self.setToolTip("Zoom In")
        self.setIcon(icons.zoom_in_button)

        self.frame_scale_ctrlr.scalechanged.connect(self.on_scalechanged)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_triggered(self):
        self.frame_scale_ctrlr.zoom_in()

    def on_scalechanged(self, value):
        self.setEnabled(value != self.frame_scale_ctrlr.config_options[-1])


class ZoomOutAction(QAction):
    def __init__(self, parent, frame_scale_ctrlr, size=None):
        super().__init__(parent=parent)
        self.frame_scale_ctrlr = frame_scale_ctrlr

        self.setText("Zoom Out")
        self.setToolTip("Zoom Out")
        self.setIcon(icons.zoom_out_button)

        self.frame_scale_ctrlr.scalechanged.connect(self.on_scalechanged)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_triggered(self):
        self.frame_scale_ctrlr.zoom_out()

    def on_scalechanged(self, value):
        self.setEnabled(value != self.frame_scale_ctrlr.config_options[0])


class FrameScaleMenu(QMenu):
    def __init__(self, main_win, frame_scale_ctrlr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_scale_ctrlr = frame_scale_ctrlr

        self.setTitle("Zoom")

        self.quarter = QAction("1:4 Quarter", self)
        self.quarter.triggered.connect(lambda: self.frame_scale_ctrlr.set_scale(0.25))
        self.quarter.setCheckable(True)

        self.half = QAction("1:2 Half", self)
        self.half.triggered.connect(lambda: self.frame_scale_ctrlr.set_scale(0.5))
        self.half.setCheckable(True)

        self.original = QAction("1:1 Original", self)
        self.original.triggered.connect(lambda: self.frame_scale_ctrlr.set_scale(1))
        self.original.setCheckable(True)

        self.double = QAction("1:2 Double", self)
        self.double.triggered.connect(lambda: self.frame_scale_ctrlr.set_scale(2))
        self.double.setCheckable(True)

        self.explicit_zooms = QActionGroup(self)
        self.explicit_zooms.addAction(self.quarter)
        self.explicit_zooms.addAction(self.half)
        self.explicit_zooms.addAction(self.original)
        self.explicit_zooms.addAction(self.double)
        self.addActions(self.explicit_zooms.actions())

        self.option_action_map = {
            0.25: self.quarter,
            0.5: self.half,
            1: self.original,
            2: self.double,
        }

        self.zoom_in = ZoomInAction(self, frame_scale_ctrlr=self.frame_scale_ctrlr)
        self.zoom_in.setIcon(icons.zoom_in_menu_item)
        self.addAction(self.zoom_in)

        self.zoom_out = ZoomOutAction(self, frame_scale_ctrlr=self.frame_scale_ctrlr)
        self.zoom_out.setIcon(icons.zoom_out_menu_item)
        self.addAction(self.zoom_out)

        self.conform_to_media()

        self.frame_scale_ctrlr.scalechanged.connect(self.on_scalechanged)
        vlcqt.media_player.mediachanged.connect(self.on_mediachanged)

    def on_scalechanged(self, value):
        self.option_action_map[value].setChecked(True)

    def on_mediachanged(self):
        self.conform_to_media()

    def conform_to_media(self):
        has_media = vlcqt.media_player.has_media
        for a in self.actions():
            a.setEnabled(has_media)
        self.option_action_map[config.state.view_scale].setChecked(True)


class FrameScaleMenuButton(QToolButton):
    def __init__(self, parent, frame_scale_menu, size):
        super().__init__(parent=parent)

        self.menu = frame_scale_menu
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = base.OpenMenuAction(
            icon=icons.zoom_menu_button,
            text=self.menu.title(),
            menu=self.menu,
            button=self,
        )
        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setDefaultAction(self.action)


class ZoomInButton(QToolButton):
    def __init__(self, parent, frame_scale_ctrlr, size=None):
        super().__init__(parent=parent)
        self.frame_scale_ctrlr = frame_scale_ctrlr

        self.setAutoRaise(True)
        self.setIconSize(QSize(size, size))

        self.action = ZoomInAction(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )
        self.setDefaultAction(self.action)


class ZoomOutButton(QToolButton):
    def __init__(self, parent, frame_scale_ctrlr, size=None):
        super().__init__(parent=parent)
        self.frame_scale_ctrlr = frame_scale_ctrlr

        self.setAutoRaise(True)
        self.setIconSize(QSize(size, size))

        self.action = ZoomOutAction(
            parent=self, frame_scale_ctrlr=self.frame_scale_ctrlr
        )
        self.setDefaultAction(self.action)
