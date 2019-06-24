import logging

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QSlider, QToolButton

from .. import config, util, vlcqt
from ..controls import base
from ..gui import icons

log = logging.getLogger(__name__)


class TogglePlaybackModeAction(QAction):
    setplaybackmode = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setText("Toggle Playback Mode")
        self.setToolTip("Toggle Playback Mode")
        self.setIconText("Playback Mode")

        self.lp = vlcqt.list_player
        self.setCheckable(True)

        self.option_names = ["off", "one", "all"]
        for index, item in enumerate(self.option_names):
            if item == config.state.playback_mode:
                util.rotate_list(self.option_names, index)
                break

        option_name = self.option_names[0]
        self.setIcon(icons.playback_mode[option_name])

        self.triggered.connect(self.on_triggered)
        self.setplaybackmode.connect(self.lp.on_setplaybackmode)

    def on_triggered(self):
        util.rotate_list(self.option_names, 1)
        option_name = self.option_names[0]
        self.setIcon(icons.playback_mode[option_name])
        config.state.playback_mode = option_name
        self.setplaybackmode.emit(option_name)
        self.setChecked(True if option_name != "off" else False)


class TogglePlaybackModeButton(QToolButton):
    def __init__(self, parent, size):
        super().__init__(parent=parent)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = TogglePlaybackModeAction(parent=self)
        self.setDefaultAction(self.action)


class PlayPauseAction(QAction):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setToolTip("Play/Pause")
        self.setCheckable(True)

        self.setIcon(icons.play_pause)

        self.mp = vlcqt.media_player
        self.lp = vlcqt.list_player

        if self.mp.is_playing():
            self.on_playing()
        else:
            self.on_paused()

        self.mp.playing.connect(self.on_playing)
        self.mp.paused.connect(self.on_paused)
        self.mp.stopped.connect(self.on_paused)

        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_playing(self):
        self.setChecked(True)

    @pyqtSlot()
    def on_paused(self):
        self.setChecked(False)

    @pyqtSlot()
    def on_triggered(self):
        if self.mp.is_playing():
            self.lp.pause()
        else:
            self.lp.play()


class PlayPauseButton(QToolButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.action = PlayPauseAction(parent=self)
        self.setDefaultAction(self.action)


class SkipBackwardButton(base.SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.skip_backward_button)
        self.curr_icon = self.icons
        self.update_icon_hover()
        pass


class SkipForwardButton(base.SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.skip_forward_button)
        self.curr_icon = self.icons
        self.update_icon_hover()
        pass


class FrameResPlaybackSlider(QSlider):

    default_values = {"length": 1, "proportion_per_frame": 1}

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.mp = vlcqt.media_player
        self.setToolTip("Position")
        self.curr_pos = self.mp.get_position()
        self.mp_pos = None
        self.mouse_down = False

        # # Might be useful for playlist
        # self.proportion_per_frame = self.default_values["proportion_per_frame"]
        # self.length = self.default_values["length"]

        _media = self.mp.get_media()
        if _media:
            self.conform_to_media(media=_media)

        self.mp.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)
        # self.mp.endreached.connect(self.on_endreached) # Might be useful for playlist

        self.newframe_conn = self.mp.newframe.connect(self.on_newframe)

    def conform_to_media(self, media):
        fps = util.get_media_fps(media)
        duration_secs = media.get_duration() / 1000
        self.total_frames = duration_secs * fps
        self.proportion_per_frame = 1 / self.total_frames
        self.set_length(self.total_frames)
        self.curr_pos = self.mp_pos = self.mp.get_position()

    def setValue(self, value):
        if not self.mouse_down:
            super().setValue(value)

    @pyqtSlot(vlcqt.Event)
    def on_mediachanged(self, e):
        self.conform_to_media(media=self.mp.get_media())

    @pyqtSlot(vlcqt.Event)
    def on_positionchanged(self, e):
        self.mp_pos = self.mp.get_position()
        self.mouse_down = False

    @pyqtSlot()
    def on_newframe(self):
        if self.mp_pos:
            self.curr_pos = self.mp_pos
            self.mp_pos = None
        else:
            self.curr_pos = self.curr_pos + self.proportion_per_frame
        self.setValue(self.curr_pos * self.length)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mouse_down = True
        self.mp.positionchanged.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        super().setValue(as_slider_val)
        self.mp_pos = as_proportion

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.mp_pos = as_proportion
        super().setValue(as_slider_val)

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.connect(self.on_positionchanged)

    def set_length(self, value):
        self.setMinimum(0)
        self.setMaximum(value)
        self.length = self.maximum() - self.minimum()
        self.setTickInterval(1 / self.length)

    def get_mouse_pos(self, e):
        slider_min, slider_max = self.minimum(), self.maximum()
        slider_range = slider_max - slider_min
        pos_as_proportion = e.pos().x() / self.width()
        pos_as_slider_val = slider_range * pos_as_proportion + slider_min
        return pos_as_proportion, pos_as_slider_val
