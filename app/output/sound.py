import logging

import config
import vlcqt
from base.popup import PopupControlWidget
from gui import icons
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QAction, QHBoxLayout, QSlider, QToolButton

log = logging.getLogger(__name__)


class VolumeManager(QObject):
    volumechanged = pyqtSignal(int)

    def __init__(self, parent, listplayer, media_player):
        super().__init__(parent)
        self.lp = listplayer
        self.mp = media_player
        vlcqt.libvlc_audio_set_volume(self.mp, config.state.volume)
        self.mp.audiovolume.connect(self.on_audiovolume)
        self.lp.mediachanged.connect(self.on_mediachanged)

    def set_volume(self, value):
        self.mp.audio_set_volume(value)
        if not self.mp.has_media():
            # No change event will be called if no media loaded,
            # so we call that event here and let view base update config state,
            # then update media player from config state when next media is loaded
            self.volumechanged.emit(value)

    def get_volume(self):
        if self.mp.has_media():
            volume = self.mp.audio_get_volume()
        else:
            volume = config.state.volume
        return volume

    def on_audiovolume(self, e):
        volume = self.get_volume()
        self.volumechanged.emit(volume)

    def on_mediachanged(self):
        self.mp.audio_set_volume(self.get_volume())


class VolumeSlider(QSlider):
    """Initializes and updates media player volume value"""

    def __init__(self, parent, vol_mngr):
        super().__init__(parent=parent)
        self.vol_mngr = vol_mngr
        self.vol_mngr.set_volume(100)

        self.setToolTip("Volume")
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.valueChanged.connect(self.on_slider_valueChanged)

    def on_slider_valueChanged(self, value):
        self.vol_mngr.set_volume(value)


class VolumePopupWidget(PopupControlWidget):
    def __init__(self, parent, vol_mngr: VolumeManager):
        super().__init__(parent=parent)
        self.vol_mngr = vol_mngr
        self.slider = VolumeSlider(parent=parent, vol_mngr=self.vol_mngr)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.slider)
        self._hideclick = False

    def showEvent(self, e):
        value = self.vol_mngr.get_volume()
        if value:
            self.slider.setValue(value)

    def hideEvent(self, e):
        config.state.volume = self.slider.value()

    def mouseReleaseEvent(self, e):
        """Make certain that when a user clicks outside of the widget while it's open,
        the widget closes nicely. Depends on state recorded in 'mousePressEvent' call.
        """
        if self._hideclick is True:
            self.hide()
            self._hideclick = False

    def mousePressEvent(self, e):
        if e.source() != self and not self.isHidden():
            self._hideclick = True


class VolumePopupAction(QAction):
    def __init__(self, parent, vol_mngr: VolumeManager):
        super().__init__(text="Volume")
        self.vol_mngr = vol_mngr
        self.icons = icons.get("volume_button")
        self.vol_widget = VolumePopupWidget(parent=parent, vol_mngr=self.vol_mngr)

        self.update_icon(config.state.volume)  # type: ignore

        self.triggered.connect(self.vol_widget.popup)
        self.vol_mngr.volumechanged.connect(self.update_icon)

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


class VolumePopupButton(QToolButton):
    def __init__(self, parent, vol_mngr):
        super().__init__(parent=parent)
        self.vol_mngr = vol_mngr
        self.setToolTip("Zoom")
        self.action = VolumePopupAction(parent=self, vol_mngr=self.vol_mngr)
        self.setDefaultAction(self.action)
