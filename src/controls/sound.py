from PyQt5.QtCore import QPoint, QSize, Qt
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

from .. import config, vlcqt
from ..controls import base
from ..gui import icons


class VolumeSlider(QSlider):
    def __init__(self, parent):
        super().__init__(parent)
        self.mp = vlcqt.media_player

        self.setToolTip("Volume")
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.setValue(self.mp.audio_get_volume())

        self.mp.audiovolume.connect(self.on_audiovolume)
        self.valueChanged.connect(self.on_valueChanged)

    def on_audiovolume(self, value):
        self.setValue(self.mp.audio_get_volume())

    def on_valueChanged(self, value):
        self.update_slider_value(value)

    def update_slider_value(self, value=None):
        if value:
            _value = value
        elif self.mp.has_media:
            _value = self.mp.audio_get_volume()
        else:
            _value = config.state.volume
        self.mp.audio_set_volume(_value)


class VolumeSliderPopUp(base.PopUpWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.slider = VolumeSlider(self)
        self.layout.addWidget(self.slider)

    def showEvent(self, e):
        self.slider.update_slider_value()

    def hideEvent(self, e):
        config.state.volume = self.slider.value()


class VolumePopUpButton(QToolButton):
    def __init__(self, parent, size):
        super().__init__(parent=parent)
        self.setToolTip("Zoom")
        self.setCheckable(False)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.widget = VolumeSliderPopUp(parent=self)

        self.action = base.PopUpWidgetAction(
            icon=icons.volume_button, text="Volume", widget=self.widget, button=self
        )

        self.setDefaultAction(self.action)
