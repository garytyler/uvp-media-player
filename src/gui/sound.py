from PyQt5.QtWidgets import QSlider

from . import buttons, icons


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


class VolumeButton(buttons.SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.volume_button)
        self.setToolTip("Volume")
        self.switch_icon("off")
        self.setDisabled(True)
        self.update_icon_hover()
