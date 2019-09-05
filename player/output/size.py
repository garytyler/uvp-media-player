import logging

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QToolButton

from .. import vlcqt
from ..base.popup import PopupMenuAction
from ..gui import icons
from ..util import config

log = logging.getLogger(__name__)


class FrameSizeManager(QObject):
    mediaframeresized = pyqtSignal(float)

    def __init__(self, main_win, viewpoint_mngr):
        super().__init__()
        self.vp_manager = viewpoint_mngr
        self._main_win = main_win
        vlcqt.media_player.mediachanged.connect(self.conform_to_media)

    def set_scale(self, scale) -> float:
        config.state.view_scale = scale
        self._apply_rescale(scale)

    def conform_to_media(self, media: vlcqt.Media = None):
        """If media arg is None, current media_player media is used"""
        self._apply_rescale(self.get_media_scale(media))
        self.vp_manager.trigger_redraw()

    def _apply_rescale(self, scale):
        self._main_win.resize_to_media(scale)
        self.mediaframeresized.emit(scale)  # TODO

    @staticmethod
    def get_media_scale(media: vlcqt.Media = None):
        _media = media if media else vlcqt.media_player.get_media()
        if _media:
            return config.state.view_scale
        else:
            return 1


class ZoomControlManager(QMenu):
    zoomchanged = pyqtSignal(float)

    def __init__(self, main_win, frame_size_mngr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.frame_size_mngr = frame_size_mngr

        for a in self.actions():
            a.setEnabled(vlcqt.media_player.has_media())

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


# class FrameSizeManager(QObject):
#     mediaframeresized = pyqtSignal(float)

#     def __init__(self, main_win, viewpoint_mngr):
#         super().__init__()
#         self.vp_manager = viewpoint_mngr
#         self.main_win = main_win
#         self.mp = vlcqt.media_player
#         self.media = self.mp.get_media()
#         self.mediaframeresized.connect(self.vp_manager.trigger_redraw)
#         self.mp.mediachanged.connect(self.conform_to_media)
#         # self.mediaframeresized.connect(self.vp_manager.trigger_redraw)
#         # self.mp.mediachanged.connect(self.vp_manager.trigger_redraw)

#         # self._main_win.initialized.connect(self.conform_to_media)

#     def set_scale(self, scale) -> float:
#         config.state.view_scale = scale
#         self._apply_rescale(scale)

#     def conform_to_media(self, media: vlcqt.Media = None):
#         """If media arg is None, current media_player media is used"""
#         self.media = media if media else self.mp.get_media()
#         self._apply_rescale(scale=config.state.view_scale)
#         self.vp_manager.trigger_redraw()

#     def _apply_rescale(self, scale):
#         self.main_win.resize_to_media(scale)
#         self.mediaframeresized.emit(scale)


class ZoomInAction(QAction):
    def __init__(self, parent, zoom_ctrl_mngr, size=None):
        super().__init__(parent=parent)
        self.zoom_ctrl_mngr = zoom_ctrl_mngr

        self.setText("Zoom In")
        self.setToolTip("Zoom In")
        self.setIcon(icons.zoom_in_button)

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
        self.setIcon(icons.zoom_out_button)

        self.zoom_ctrl_mngr.zoomchanged.connect(self.on_zoomchanged)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_triggered(self):
        self.zoom_ctrl_mngr.zoom_out()

    def on_zoomchanged(self, value):
        self.setEnabled(value != self.zoom_ctrl_mngr.config_options[0])


class FrameZoomMenu(QMenu):
    def __init__(self, main_win, zoom_ctrl_mngr):
        super().__init__(parent=main_win)
        self.main_win = main_win
        self.zoom_ctrl_mngr = zoom_ctrl_mngr

        self.setTitle("Zoom")
        self.setIcon(icons.zoom_menu_button)

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
        self.zoom_in.setIcon(icons.zoom_in_menu_item)
        self.addAction(self.zoom_in)

        self.zoom_out = ZoomOutAction(self, zoom_ctrl_mngr=self.zoom_ctrl_mngr)
        self.zoom_out.setIcon(icons.zoom_out_menu_item)
        self.addAction(self.zoom_out)

        self.conform_to_media()

        self.zoom_ctrl_mngr.zoomchanged.connect(self.on_zoomchanged)
        vlcqt.media_player.mediachanged.connect(self.on_mediachanged)

    def on_zoomchanged(self, value):
        self.option_action_map[value].setChecked(True)

    def on_mediachanged(self):
        self.conform_to_media()

    def conform_to_media(self):
        has_media = vlcqt.media_player.has_media()
        for a in self.actions():
            a.setEnabled(has_media)
        self.option_action_map[config.state.view_scale].setChecked(True)


class FrameZoomMenuButton(QToolButton):
    def __init__(self, parent, frame_scale_menu, size):
        super().__init__(parent=parent)

        self.menu = frame_scale_menu
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = PopupMenuAction(
            icon=icons.zoom_menu_button,
            text=self.menu.title(),
            menu=self.menu,
            parent=self,
        )
        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setDefaultAction(self.action)
