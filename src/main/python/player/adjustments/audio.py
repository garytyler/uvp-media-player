import copy
import logging
import re

from PyQt5 import QtCore, QtWidgets

from player import config, vlcqt
from player.utils import cached_property

log = logging.getLogger(__name__)


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
        # self.setValue(config.schema[self.config_key()]["default"] * 100)
        self.setValue(config.schema[self.config_key()]["default"])

    def setValue(self, value):
        super().setValue(int(value * 100))

    def showEvent(self, e):
        self.update_view()


class AudioEqualizerAmpSliderWidget(MediaPlayerAdjustmentSlider):
    def __init__(self, band_index, equalizer, *args, **kwargs):
        self.band_index = band_index
        self.eq = equalizer
        super().__init__(*args, **kwargs)

    def config_key(self):
        return f"audio_eq_amp_{self.band_index}"

    def _set_model_state(self, value):
        self.eq.set_amp_at_index(float(value / 100), self.band_index)
        self.mp.set_equalizer(self.eq)

    def _get_model_state(self):
        return self.eq.get_amp_at_index(self.band_index)


class AudioEqualizerPreampSliderWidget(MediaPlayerAdjustmentSlider):
    def __init__(self, equalizer, *args, **kwargs):
        self.eq = equalizer
        super().__init__(*args, **kwargs)

    def config_key(self):
        return "audio_eq_preamp"

    def _set_model_state(self, value):
        self.eq.set_preamp(float(value / 100))
        self.mp.set_equalizer(self.eq)

    def _get_model_state(self):
        return self.eq.get_preamp()


class AudioEqualizerSliderGroupWidget(QtWidgets.QWidget):

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

        amp_sliders = [
            AudioEqualizerAmpSliderWidget(
                equalizer=self.eq,
                band_index=index,
                name=re.sub(".0$", "", re.sub("000.0$", "K", str(band_freq))),
                min_value=-20.0,
                max_value=20.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            )
            for index, band_freq in enumerate(self.band_frequencies)
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
        self.sliders = [preamp_slider] + amp_sliders

        self.sliders_layout = QtWidgets.QGridLayout()
        for index, slider in enumerate(self.sliders):
            label = QtWidgets.QLabel(slider.name.capitalize())
            self.sliders_layout.addWidget(slider, 1, index)
            self.sliders_layout.addWidget(label, 2, index)
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
        self.enable_checkbox.stateChanged.emit(2 if config.state.audio_eq_enable else 0)

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
        config.state.audio_eq_enable = True if value else False
        for slider in self.sliders:
            slider.setEnabled(True if value else False)
        self.on_enabled.emit(True if value else False)

    @cached_property
    def band_frequencies(self):
        return [vlcqt.libvlc_audio_equalizer_get_band_frequency(n) for n in range(10)]


class AudioEqualizerPresetComboBox(QtWidgets.QComboBox):
    currentPresetChanged = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.activated.connect(self.on_activated)

    def showEvent(self, e):
        self.reload_items()

    def hideEvent(self, e):
        config.state.audio_eq_selected_user_preset = self.currentText()

    def showPopup(self):
        self.reload_items()
        super().showPopup()

    def reload_items(self):
        self.clear()
        self.addItem(
            "",
            {
                "audio_eq_amp_0": 0.0,
                "audio_eq_amp_1": 0.0,
                "audio_eq_amp_2": 0.0,
                "audio_eq_amp_3": 0.0,
                "audio_eq_amp_4": 0.0,
                "audio_eq_amp_5": 0.0,
                "audio_eq_amp_6": 0.0,
                "audio_eq_amp_7": 0.0,
                "audio_eq_amp_8": 0.0,
                "audio_eq_amp_9": 0.0,
                "audio_eq_preamp": 0.0,
            },
        )
        for name, preset in config.state.audio_eq_user_presets.items():
            self.addItem(name, preset)
        self.insertSeparator(self.count())
        for name, preset in self.default_presets.items():
            self.addItem(name, preset)
        self.setCurrentIndex(self.findText(config.state.audio_eq_selected_user_preset))

    def on_activated(self, index):
        self.currentPresetChanged.emit(self.itemData(index))

    @cached_property
    def default_presets(self):
        default_presets = {}
        for index in range(vlcqt.libvlc_audio_equalizer_get_preset_count()):
            name = vlcqt.libvlc_audio_equalizer_get_preset_name(index).decode()
            eq = vlcqt.libvlc_audio_equalizer_new_from_preset(index)
            preset = {"audio_eq_preamp": eq.get_preamp()}
            for n in range(10):
                preset[f"audio_eq_amp_{n}"] = eq.get_amp_at_index(n)
            default_presets[f"{name}"] = preset
        return default_presets


class AudioEqualizerWidget(AudioEqualizerSliderGroupWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(media_player=media_player, parent=parent)
        self.preset_box = AudioEqualizerPresetComboBox(self)
        self.top_ctrls_layout.addWidget(
            QtWidgets.QLabel("Preset"), 1, QtCore.Qt.AlignRight
        )
        self.top_ctrls_layout.addWidget(self.preset_box, stretch=2)

        self.preset_buttons_layout = QtWidgets.QHBoxLayout()
        self.layout().insertLayout(1, self.preset_buttons_layout)

        self.preset_buttons_layout.addStretch(1)

        self.create_preset_button = QtWidgets.QPushButton("Make Preset")
        self.create_preset_button.setCheckable(False)
        self.preset_buttons_layout.addWidget(self.create_preset_button)
        self.create_preset_button.clicked.connect(self.create_user_preset)

        self.delete_preset_button = QtWidgets.QPushButton("Delete Preset")
        self.delete_preset_button.setCheckable(False)
        self.preset_buttons_layout.addWidget(self.delete_preset_button)
        self.delete_preset_button.clicked.connect(self.delete_user_preset)

        self.preset_box.currentPresetChanged.connect(self.load_preset)

    def showEvent(self, e):
        self.delete_preset_button.setEnabled(bool(config.state.audio_eq_user_presets))

    def load_preset(self, preset: dict):
        for slider in self.sliders:
            key = slider.config_key()
            value = preset[key]
            slider.setValue(value)

    def create_user_preset(self):
        input_dialog = QtWidgets.QInputDialog(self)
        input_dialog.setOkButtonText("Save Preset")
        input_label = "Preset Name:"
        while True:
            name, approved = input_dialog.getText(
                self, "Create Preset", input_label, text=self.preset_box.currentText(),
            )
            if not approved:
                break
            elif not name.strip():
                input_label = "(!) - Preset Name cannot be empty."
            elif name.strip() in self.preset_box.default_presets:
                input_label = (
                    f"(!) - '{name}' is a stock preset.\n"
                    "Choose another name.\n\n"
                    "Preset Name:"
                )
            else:
                break
        preset = {slider.config_key(): slider.value() for slider in self.sliders}
        user_presets_copy = copy.deepcopy(config.state.audio_eq_user_presets)
        user_presets_copy[name] = preset
        config.state.audio_eq_user_presets = user_presets_copy
        self.delete_preset_button.setEnabled(bool(config.state.audio_eq_user_presets))

    def delete_user_preset(self):
        input_dialog = QtWidgets.QInputDialog(self)
        input_dialog.setOkButtonText("Delete Preset")
        current_index = self.preset_box.currentIndex()
        user_presets = config.state.audio_eq_user_presets
        name, approved = input_dialog.getItem(
            self,
            "Delete Preset",
            "Select Preset",
            config.state.audio_eq_user_presets,
            current=current_index - 1 if current_index - 1 <= len(user_presets) else 0,
            editable=False,
        )
        if not approved:
            return
        user_presets_copy = copy.deepcopy(config.state.audio_eq_user_presets)
        del user_presets_copy[name]
        config.state.audio_eq_user_presets = user_presets_copy
        self.preset_box.setCurrentIndex(0)
        self.delete_preset_button.setEnabled(bool(config.state.audio_eq_user_presets))
