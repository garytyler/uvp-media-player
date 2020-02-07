import logging

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QToolButton

from player import config
from player.common.base.popup import PopupMenuAction
from player.gui import icons

log = logging.getLogger(__name__)


class FrameSizeManager(QObject):
    mediaframeresized = pyqtSignal(float)
    default_size = 600, 360
    default_scale = 1

    def __init__(self, main_win, viewpoint_mngr, listplayer):
        super().__init__()
        self.viewpoint_mngr = viewpoint_mngr
        self._main_win = main_win
        self.listplayer = listplayer
        self.listplayer.mediachanged.connect(self.on_mediachanged)

    def on_mediachanged(self, media_item):
        if config.state.auto_resize:
            width, height = media_item.size()
            self.update_frame_size(height=height, width=width)

    def set_scale(self, scale) -> float:
        config.state.view_scale = scale
        self.update_frame_size(scale=scale)

    def update_frame_size(self, width=None, height=None, scale=None):
        """If media arg is None, current media_player media is used"""
        if not height or not width:
            _width, _height = self.get_media_size()
            width = width if width else _width
            height = height if height else _height
        scale = scale if scale else self.get_media_scale()
        self._main_win.resize_to_media(width, height, scale)
        self.mediaframeresized.emit(scale)  # TODO
        self.viewpoint_mngr.trigger_redraw()

    def get_media_size(self):
        item = self.listplayer.item()
        if item:
            return item.size()
        else:
            return self.default_size

    def get_media_scale(self):
        item = self.listplayer.item()
        if item:
            return config.state.view_scale
        else:
            return self.default_scale


class ZoomControlManager(QObject):
    zoomchanged = pyqtSignal(float)

    def __init__(self, main_win, frame_size_mngr, media_player):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_mngr = frame_size_mngr

        # for a in self.actions():
        #     a.setEnabled(media_player.has_media())

        self.config_options = sorted(config.options.view_scale)

        self.option_enum_map = {}
        for index, option in enumerate(sorted(self.config_options)):
            self.option_enum_map[option] = index

        self.frame_size_mngr.mediaframeresized.connect(self.on_mediaframeresized)

    def set_scale(self, value):
        self.frame_size_mngr.set_scale(value)

    def on_mediaframeresized(self, value: float):
        self.zoomchanged.emit(value)

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


class AutoResizeAction(QAction):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setText("Auto-resize")
        self.setToolTip("Auto-resize")
        self.setCheckable(True)
        self.setChecked(config.state.auto_resize)
        self.toggled.connect(self.on_toggled)

    @pyqtSlot(bool)
    def on_toggled(self, value):
        config.state.auto_resize = value


class ZoomInAction(QAction):
    def __init__(self, parent, zoom_ctrl_mngr, size=None):
        super().__init__(parent=parent)
        self.zoom_ctrl_mngr = zoom_ctrl_mngr

        self.setText("Zoom In")
        self.setToolTip("Zoom In")
        self.setIcon(icons.get("zoom_in_button"))

        self.zoom_ctrl_mngr.zoomchanged.connect(self.on_zoomchanged)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_triggered(self):
        self.zoom_ctrl_mngr.zoom_in()

    def on_zoomchanged(self, value):
        self.setEnabled(value != self.zoom_ctrl_mngr.config_options[-1])


class ZoomOutAction(QAction):
    def __init__(self, parent, zoom_ctrl_mngr, size=None):
        super().__init__(parent=parent)
        self.zoom_ctrl_mngr = zoom_ctrl_mngr

        self.setText("Zoom Out")
        self.setToolTip("Zoom Out")
        self.setIcon(icons.get("zoom_out_button"))

        self.zoom_ctrl_mngr.zoomchanged.connect(self.on_zoomchanged)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_triggered(self):
        self.zoom_ctrl_mngr.zoom_out()

    def on_zoomchanged(self, value):
        self.setEnabled(value != self.zoom_ctrl_mngr.config_options[0])


class FrameZoomMenu(QMenu):
    def __init__(self, main_win, zoom_ctrl_mngr, listplayer, media_player):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.zoom_ctrl_mngr = zoom_ctrl_mngr
        self.listplayer = listplayer
        self.mp = media_player

        self.setTitle("Zoom")
        self.setIcon(icons.get("zoom_menu_button"))

        self.quarter = QAction("1:4 Quarter", self)
        self.quarter.triggered.connect(lambda: self.zoom_ctrl_mngr.set_scale(0.25))
        self.quarter.setCheckable(True)

        self.half = QAction("1:2 Half", self)
        self.half.triggered.connect(lambda: self.zoom_ctrl_mngr.set_scale(0.5))
        self.half.setCheckable(True)

        self.original = QAction("1:1 Original", self)
        self.original.triggered.connect(lambda: self.zoom_ctrl_mngr.set_scale(1))
        self.original.setCheckable(True)

        self.double = QAction("1:2 Double", self)
        self.double.triggered.connect(lambda: self.zoom_ctrl_mngr.set_scale(2))
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

        self.zoom_in = ZoomInAction(self, zoom_ctrl_mngr=self.zoom_ctrl_mngr)
        self.zoom_in.setIcon(icons.get("zoom_in_menu_item"))
        self.addAction(self.zoom_in)

        self.zoom_out = ZoomOutAction(self, zoom_ctrl_mngr=self.zoom_ctrl_mngr)
        self.zoom_out.setIcon(icons.get("zoom_out_menu_item"))
        self.addAction(self.zoom_out)

        self.addSeparator()
        self.addAction(AutoResizeAction(self))

        self.conform_to_media()

        self.zoom_ctrl_mngr.zoomchanged.connect(self.on_zoomchanged)
        self.listplayer.mediachanged.connect(self.on_mediachanged)

    def on_zoomchanged(self, value):
        self.option_action_map[value].setChecked(True)

    def on_mediachanged(self):
        self.conform_to_media()

    def conform_to_media(self):
        self.option_action_map[config.state.view_scale].setChecked(True)

    def enable_zoom_actions(self):
        """Enable zoom actions if media is loaded and disable them if not."""
        has_media = self.mp.has_media()
        for a in self.actions():
            a.setEnabled(has_media)


class FrameZoomMenuButton(QToolButton):
    def __init__(self, parent, frame_scale_menu, size):
        super().__init__(parent=parent)

        self.menu = frame_scale_menu
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = PopupMenuAction(
            icon=icons.get("zoom_menu_button"),
            text=self.menu.title(),
            menu=self.menu,
            parent=self,
        )
        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setDefaultAction(self.action)
