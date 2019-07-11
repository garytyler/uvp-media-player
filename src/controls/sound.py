from PyQt5.QtCore import QObject, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QSlider,
    QToolButton,
    QWidget,
)

from .. import vlcqt
from ..controls import base
from ..gui import icons
from ..util import config


class VolumeController(QObject):
    volumechanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.mp = vlcqt.media_player
        self.mp.audio_set_volume(config.state.volume)
        self.mp.audiovolume.connect(self.on_audiovolume)
        self.mp.mediachanged.connect(self.on_mediachanged)

    def set_volume(self, value):
        self.mp.audio_set_volume(value)
        if not self.mp.has_media:
            # No change event will be called if no media loaded,
            # so we call that event here and let view components update config state,
            # then update media player from config state when next media is loaded
            self.volumechanged.emit(value)

    def get_volume(self):
        if self.mp.has_media:
            _value = self.mp.audio_get_volume()
        else:
            _value = config.state.volume
        return _value

    def on_audiovolume(self, value):
        self.volumechanged.emit(value)

    def on_mediachanged(self):
        self.mp.audio_set_volume(self.get_volume())


class VolumeSlider(QSlider):
    """Initializes and updates media player volume value"""

    widgethidden = pyqtSignal(int)

    def __init__(self, parent, vol_ctrlr):
        super().__init__(parent)
        self.vol_ctrlr = vol_ctrlr

        self.setToolTip("Volume")
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.valueChanged.connect(self.on_slider_valueChanged)

    def on_slider_valueChanged(self, value):
        self.vol_ctrlr.set_volume(value)

    def showEvent(self, e):
        curr_value = self.vol_ctrlr.get_volume()
        # if curr_value:
        self.setValue(curr_value if curr_value else config.state.volume)

    def hideEvent(self, e):
        vol_val = self.value()
        config.state.volume = vol_val
        self.widgethidden.emit(vol_val)


class VolumeSliderPopUpWidget(base.PopUpWidget):
    def __init__(self, parent, slider):
        super().__init__(parent)
        self.slider = slider
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.slider)
        print(slider.width())
        print(slider.height())


class VolumePopUpAction(base.PopUpWidgetAction):
    def __init__(
        self, widget: base.PopUpWidget, button: QToolButton, vol_ctrlr: VolumeController
    ):
        super().__init__(text="Volume", widget=widget, button=button)
        self.widget = widget
        self.vol_ctrlr = vol_ctrlr
        self.icons = icons.volume_button
        self.mp = vlcqt.media_player

        self.vol_ctrlr.volumechanged.connect(self.update_icon)
        self.update_icon(config.state.volume)

    def update_icon(self, vol_val):
        vol_max = 100
        low_max = vol_max / 3
        medium_max = vol_max / 1.5

        if vol_val == 0:
            self.setIcon(self.icons["mute"])
        elif 0 < vol_val < low_max:
            self.setIcon(self.icons["low"])
        elif low_max < vol_val < medium_max:
            self.setIcon(self.icons["medium"])
        elif medium_max < vol_val < vol_max:
            self.setIcon(self.icons["high"])


class VolumeSliderPopUpButton(QToolButton):
    def __init__(self, parent, size, vol_ctrlr):
        super().__init__(parent=parent)
        self.vol_ctrlr = vol_ctrlr

        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.slider = VolumeSlider(self, vol_ctrlr=self.vol_ctrlr)
        self.widget = VolumeSliderPopUpWidget(parent=self, slider=self.slider)
        self.action = VolumePopUpAction(
            widget=self.widget, button=self, vol_ctrlr=self.vol_ctrlr
        )

        self.setDefaultAction(self.action)
