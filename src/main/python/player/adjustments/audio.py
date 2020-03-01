from PyQt5 import QtCore, QtWidgets

from player import config, vlcqt
from player.utils import cached_property


class MediaPlayerAdjustmentSlider(QtWidgets.QSlider):
    def __init__(
        self, name, min_value, max_value, tick_interval, media_player, parent=None,
    ):
        super().__init__(parent=parent)
        self.name = name
        self.mp = media_player
        self.setToolTip(name)
        self.setOrientation(QtCore.Qt.Vertical)
        self.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.setMinimum(config.schema[self._config_key()]["min"] * 100)
        self.setMaximum(config.schema[self._config_key()]["max"] * 100)
        self.setTickInterval(tick_interval * 100)

        self.valueChanged.connect(lambda v: self._set_model_state(v))

        self._set_model_state(self._get_store_state())

    def _config_key(self):
        return self.name

    def _set_model_state(self, value):
        raise NotImplementedError

    def _get_model_state(self):
        raise NotImplementedError

    def _set_store_state(self, value):
        setattr(config.state, self._config_key(), value)

    def _get_store_state(self):
        return getattr(config.state, self._config_key()) * 100

    @QtCore.pyqtSlot()
    def save_state(self):
        """Write current value to config store"""
        self._set_store_state(self.value() / 100)

    @QtCore.pyqtSlot()
    def update_view(self):
        self.setValue(int(self._get_model_state() * 100))

    @QtCore.pyqtSlot()
    def reset_from_store(self):
        """Reset to default value"""
        self.setValue(config.schema[self._config_key()]["default"] * 100)

    def showEvent(self, e):
        self.update_view()


class AudioEqualizerAmpSliderWidget(MediaPlayerAdjustmentSlider):
    def __init__(self, freq_band_index, equalizer, *args, **kwargs):
        self.freq_band_index = freq_band_index
        self.eq = equalizer
        super().__init__(*args, **kwargs)

    def _config_key(self):
        return f"audio_eq_amp_{self.name}"

    def _set_model_state(self, value):
        self.eq.set_amp_at_index(float(value / 100), self.freq_band_index)
        self.mp.set_equalizer(self.eq)

    def _get_model_state(self):
        return self.eq.get_amp_at_index(self.freq_band_index)


class AudioEqualizerPreampSliderWidget(MediaPlayerAdjustmentSlider):
    def __init__(self, equalizer, *args, **kwargs):
        self.eq = equalizer
        super().__init__(*args, **kwargs)

    def _config_key(self):
        return "audio_eq_preamp"

    def _set_model_state(self, value):
        self.eq.set_preamp(float(value / 100))
        self.mp.set_equalizer(self.eq)

    def _get_model_state(self):
        return self.eq.get_preamp()


class AudioEqualizerWidget(QtWidgets.QWidget):

    on_enabled = QtCore.pyqtSignal(bool)

    def __init__(self, media_player, parent=None):
        super().__init__(parent=parent)
        self.mp = media_player
        self.eq = vlcqt.AudioEqualizer()

        self.setLayout(QtWidgets.QVBoxLayout())
        self.top_ctrls_lo = QtWidgets.QGridLayout()
        self.enable_checkbox = QtWidgets.QCheckBox("Enable Image Effects", parent=self)
        self.top_ctrls_lo.addWidget(self.enable_checkbox)
        self.layout().addLayout(self.top_ctrls_lo)

        self.sliders_layout = QtWidgets.QGridLayout()
        for index, slider in enumerate(self.sliders):
            label = QtWidgets.QLabel(slider.name.capitalize())
            self.sliders_layout.addWidget(slider, 1, index)
            self.sliders_layout.addWidget(label, 2, index)
            self.on_enabled.connect(slider.setEnabled)
            self.on_enabled.connect(label.setEnabled)
        self.layout().addLayout(self.sliders_layout)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setCheckable(False)
        self.layout().addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_state)

        self.reset_button = QtWidgets.QPushButton("Reset")
        self.reset_button.setCheckable(False)
        self.layout().addWidget(self.reset_button)
        self.reset_button.clicked.connect(
            lambda: [slider.reset_from_store() for slider in self.sliders]
        )

        self.enable_checkbox.stateChanged.connect(self.on_enable_checkbox_stateChanged)
        self.enable_checkbox.stateChanged.emit(2 if config.state.audio_eq_enable else 0)

        for slider in self.sliders:
            slider.sliderPressed.connect(lambda: self.save_button.setEnabled(True))

    def showEvent(self, e):
        for slider in self.sliders:
            slider.update_view()

    @QtCore.pyqtSlot()
    def save_state(self):
        """Save all image effect states to settings store."""
        for slider in self.sliders:
            slider.save_state()
        self.save_button.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_enable_checkbox_stateChanged(self, value):
        self.mp.set_equalizer(self.eq if value else vlcqt.AudioEqualizer())
        self.enable_checkbox.setChecked(value)
        config.state.audio_eq_enable = True if value else False
        for slider in self.sliders:
            slider.setEnabled(True if value else False)
        self.on_enabled.emit(True if value else False)

    @cached_property
    def sliders(self):
        amp_sliders = [
            AudioEqualizerAmpSliderWidget(
                equalizer=self.eq,
                freq_band_index=index,
                name=name,
                min_value=-20.0,
                max_value=20.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            )
            for index, name in enumerate(
                ["60", "170", "310", "600", "1K", "3K", "6K", "12K", "14K", "16K"]
            )
        ]
        preamp_slider = AudioEqualizerPreampSliderWidget(
            equalizer=self.eq,
            name="preamp",
            min_value=-20.0,
            max_value=20.0,
            tick_interval=1,
            media_player=self.mp,
            parent=self,
        )
        return [preamp_slider] + amp_sliders
