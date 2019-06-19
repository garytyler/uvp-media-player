import logging

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QSlider, QVBoxLayout, QWidget
from vlc import Event

from . import util, vlc_objects

log = logging.getLogger(__name__)


class PositionSlider(QSlider):
    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.mp = vlc_objects.media_player
        self.setToolTip("Position")

        self.mp.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)

    @pyqtSlot(Event)
    def on_positionchanged(self, e):
        self.setValue(self.mp.get_position() * self.length)

    @pyqtSlot(Event)
    def on_mediachanged(self, e):
        media = self.mp.get_media()
        self.fps = util.get_media_fps(media)
        duration_secs = media.get_duration() / 1000
        self.total_frames = duration_secs * self.fps
        self.set_length(self.total_frames)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.setValue(as_slider_val)

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


class FrameResPositionSlider(QSlider):

    default_values = {"length": 1, "proportion_per_frame": 1}

    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self.mp = vlc_objects.media_player
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

    @pyqtSlot(Event)
    def on_mediachanged(self, e):
        self.conform_to_media(media=self.mp.get_media())

    @pyqtSlot(Event)
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


class PlaybackSlider(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        l, t, r, b = self.layout.getContentsMargins()
        self.layout.setContentsMargins(l, 0, r, 0)
        self.slider = FrameResPositionSlider(parent=self)
        self.layout.addWidget(self.slider)


class VolumeSlider(QSlider):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip("Volume")
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())

    def set_volume(self, value):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(value)
        self.volumeslider.setValue(value)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
