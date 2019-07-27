import logging

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
from ..base.popup import PopupControlAction, PopupControlWidget
from ..gui import icons
from ..util import config

log = logging.getLogger(__name__)


class VolumeManager(QObject):
    volumechanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.mp = vlcqt.media_player
        self.mp.audio_set_volume(config.state.volume)
        self.mp.audiovolume.connect(self.on_audiovolume)
        self.mp.mediachanged.connect(self.on_mediachanged)

    def set_volume(self, value):
        self.mp.audio_set_volume(value)
        if not self.mp.has_media():
            # No change event will be called if no media loaded,
            # so we call that event here and let view base update config state,
            # then update media player from config state when next media is loaded
            self.volumechanged.emit(value)

    def get_volume(self):
        if self.mp.has_media():
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

    def __init__(self, parent, vol_mngr):
        super().__init__(parent)
        self.vol_mngr = vol_mngr

        self.setToolTip("Volume")
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.valueChanged.connect(self.on_slider_valueChanged)

    def on_slider_valueChanged(self, value):
        self.vol_mngr.set_volume(value)

    def showEvent(self, e):
        curr_value = self.vol_mngr.get_volume()
        # if curr_value:
        self.setValue(curr_value if curr_value else config.state.volume)

    def hideEvent(self, e):
        vol_val = self.value()
        config.state.volume = vol_val
        self.widgethidden.emit(vol_val)


class VolumeSliderPopupControlWidget(PopupControlWidget):
    def __init__(self, parent, slider):
        super().__init__(parent)
        self.slider = slider
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.slider)


class VolumePopupAction(PopupControlAction):
    def __init__(
        self, widget: PopupControlWidget, button: QToolButton, vol_mngr: VolumeManager
    ):
        super().__init__(text="Volume", widget=widget, button=button)
        self.widget = widget
        self.vol_mngr = vol_mngr
        self.icons = icons.volume_button
        self.mp = vlcqt.media_player

        self.vol_mngr.volumechanged.connect(self.update_icon)
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


class VolumeSliderPopupButton(QToolButton):
    def __init__(self, parent, size, vol_mngr):
        super().__init__(parent=parent)
        self.vol_mngr = vol_mngr

        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.slider = VolumeSlider(self, vol_mngr=self.vol_mngr)
        self.widget = VolumeSliderPopupControlWidget(parent=self, slider=self.slider)
        self.action = VolumePopupAction(
            widget=self.widget, button=self, vol_mngr=self.vol_mngr
        )

        self.setDefaultAction(self.action)
