import config
import vlcqt
from PyQt5 import QtCore, QtWidgets
from utils import cached_property


class MediaPlayerAdjustmentSlider(QtWidgets.QSlider):
    def __init__(
        self, name, min_value, max_value, tick_interval, media_player, parent=None,
    ):
        super().__init__(parent=parent)
        self.name = name
        self.mp = media_player
        self.setToolTip(name)
        self.setMinimum(config.schema[self.config_key()]["min"] * 100)
        self.setMaximum(config.schema[self.config_key()]["max"] * 100)
        self.setTickInterval(tick_interval * 100)

        self.valueChanged.connect(lambda v: self._set_model_state(v))

        self._set_model_state(self._get_store_state())

    def config_key(self):
        return self.name

    def value(self):
        return super().value() / 100

    def _set_model_state(self, value):
        raise NotImplementedError

    def _get_model_state(self):
        raise NotImplementedError

    def _set_store_state(self, value):
        setattr(config.state, self.config_key(), value)

    def _get_store_state(self):
        return getattr(config.state, self.config_key()) * 100

    @QtCore.pyqtSlot()
    def save_current_state(self):
        """Write current value to config store"""
        self._set_store_state(self.value())

    @QtCore.pyqtSlot()
    def update_view(self):
        self.setValue(self._get_model_state())

    @QtCore.pyqtSlot()
    def reset_from_store(self):
        """Reset to default value"""
        self.setValue(config.schema[self.config_key()]["default"])

    def setValue(self, value):
        super().setValue(int(value * 100))

    def showEvent(self, e):
        self.update_view()


class MediaPlayerAdjustmentSliderGroup(QtWidgets.QWidget):

    on_enabled = QtCore.pyqtSignal(bool)

    def __init__(self, media_player, parent=None):
        super().__init__(parent=parent)
        self.mp = media_player
        self.eq = vlcqt.AudioEqualizer()

        self.setLayout(QtWidgets.QVBoxLayout())
        self.top_ctrls_layout = QtWidgets.QHBoxLayout()
        self.enable_checkbox = QtWidgets.QCheckBox("Enable Equalizer", parent=self)
        self.top_ctrls_layout.addWidget(self.enable_checkbox)
        self.layout().addLayout(self.top_ctrls_layout)

        self.sliders_layout = QtWidgets.QGridLayout()
        for index, slider in enumerate(self.sliders):
            label = QtWidgets.QLabel(slider.name.capitalize())
            if slider.orientation() == QtCore.Qt.Vertical:
                self.sliders_layout.addWidget(slider, 1, index)
                self.sliders_layout.addWidget(label, 2, index)
            elif slider.orientation() == QtCore.Qt.Horizontal:
                self.sliders_layout.addWidget(slider, index, 2)
                self.sliders_layout.addWidget(label, index, 1)
            self.on_enabled.connect(slider.setEnabled)
            self.on_enabled.connect(label.setEnabled)
        self.layout().addLayout(self.sliders_layout)

        self.buttom_btns_layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(self.buttom_btns_layout)

        self.buttom_btns_layout.addStretch(1)

        self.reset_button = QtWidgets.QPushButton("Reset")
        self.reset_button.setCheckable(False)
        self.buttom_btns_layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(
            lambda: [slider.reset_from_store() for slider in self.sliders]
        )

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setCheckable(False)
        self.buttom_btns_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_current_state)

        self.enable_checkbox.stateChanged.connect(self.on_enable_checkbox_stateChanged)
        self.enable_checkbox.stateChanged.emit(
            2 if self.get_enabled_store_state() else 0
        )

        for slider in self.sliders:
            slider.sliderPressed.connect(lambda: self.save_button.setEnabled(True))

    def showEvent(self, e):
        for slider in self.sliders:
            slider.update_view()

    @QtCore.pyqtSlot()
    def save_current_state(self):
        for slider in self.sliders:
            slider.save_current_state()
        self.save_button.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_enable_checkbox_stateChanged(self, value):
        self.mp.set_equalizer(self.eq if value else vlcqt.AudioEqualizer())
        self.enable_checkbox.setChecked(value)
        self.set_enabled_store_state(True if value else False)
        for slider in self.sliders:
            slider.setEnabled(True if value else False)
        self.on_enabled.emit(True if value else False)

    @cached_property
    def band_frequencies(self):
        return [vlcqt.libvlc_audio_equalizer_get_band_frequency(n) for n in range(10)]

    def set_enabled_store_state(self, value: bool) -> None:
        raise NotImplementedError

    def get_enabled_store_state(self) -> bool:
        raise NotImplementedError

    @cached_property
    def sliders(self):
        raise NotImplementedError
