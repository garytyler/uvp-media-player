from PyQt5 import QtCore, QtWidgets

from player import config, vlcqt
from player.common.utils import cached_property


class EnableImageEffectsCheckBox(QtWidgets.QCheckBox):
    def __init__(self, media_player, parent=None):
        super().__init__(parent=parent)
        self.mp = media_player
        self.setText("Enable Image Effects")
        self.setTristate(False)
        self.stateChanged.connect(self.on_stateChanged)
        self.stateChanged.emit(2 if config.state.image_effects_enable else 0)

    @QtCore.pyqtSlot(int)
    def on_stateChanged(self, value):
        self.mp.video_set_adjust_int(vlcqt.VideoAdjustOption.Enable, 1 if value else 0)
        config.state.image_effects_enable = True if value else False


class AdjustmentSliderWidget(QtWidgets.QSlider):
    def __init__(
        self,
        name,
        adjust_option_type,
        min_value,
        max_value,
        tick_interval,
        media_player,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.name = name
        self.adjust_option_type = adjust_option_type
        self.mp = media_player

        self.setToolTip(name)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.setMinimum(config.schema[self.name]["min"] * 100)
        self.setMaximum(config.schema[self.name]["max"] * 100)
        self.setTickInterval(tick_interval * 100)

        self.valueChanged.connect(lambda v: self._set_media_state(v))

        self._set_media_state(self.get_stored_state())

    def _set_media_state(self, value):
        self.mp.video_set_adjust_float(self.adjust_option_type, float(value / 100))

    def get_media_state(self):
        return self.mp.video_get_adjust_float(self.adjust_option_type)

    def _set_stored_state(self, value):
        setattr(config.state, self.name, value)

    def get_stored_state(self):
        return getattr(config.state, self.name) * 100

    @QtCore.pyqtSlot()
    def save_state(self):
        """Write current value to config store"""
        self._set_stored_state(self.value() / 100)

    @QtCore.pyqtSlot()
    def load_state_from_media(self):
        """Reset to default value"""
        self.setValue(self.get_media_state() * 100)

    @QtCore.pyqtSlot()
    def reset_state(self):
        """Reset to default value"""
        self.setValue(config.schema[self.name]["default"] * 100)

    def showEvent(self, e):
        self.load_state_from_media()


class AudioEffectsWidget(QtWidgets.QWidget):
    """Main gui widget for audio effect settings"""

    on_enabled = QtCore.pyqtSignal(bool)

    def __init__(self, media_player, parent=None):
        super().__init__(parent=parent)
        self.mp = media_player

        self.setWindowTitle("Audio")
        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.top_ctrls_lo = QtWidgets.QGridLayout()
        self.enable_checkbox = QtWidgets.QCheckBox("Enable Image Effects", parent=self)
        self.top_ctrls_lo.addWidget(self.enable_checkbox)
        self.layout().addLayout(self.top_ctrls_lo)

        self.sliders_layout = QtWidgets.QGridLayout()
        for index, slider in enumerate(self.sliders):
            label = QtWidgets.QLabel(slider.name.capitalize())
            self.sliders_layout.addWidget(label, index, 1)
            self.sliders_layout.addWidget(slider, index, 2)
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
            lambda: [slider.reset_state() for slider in self.sliders]
        )

        self.enable_checkbox.stateChanged.connect(self.on_enable_checkbox_stateChanged)
        self.enable_checkbox.stateChanged.emit(
            2 if config.state.image_effects_enable else 0
        )

        for slider in self.sliders:
            slider.sliderPressed.connect(lambda: self.save_button.setEnabled(True))
            # sliderdef load_stored_state_to_media()

    def showEvent(self, e):
        for slider in self.sliders:
            slider.load_state_from_media()

    @QtCore.pyqtSlot()
    def save_state(self):
        """Save all image effect states to settings store."""
        for slider in self.sliders:
            slider.save_state()
        self.save_button.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_enable_checkbox_stateChanged(self, value):
        self.mp.video_set_adjust_int(vlcqt.VideoAdjustOption.Enable, 1 if value else 0)
        self.enable_checkbox.setChecked(value)
        config.state.image_effects_enable = True if value else False
        for slider in self.sliders:
            slider.setEnabled(True if value else False)
        self.on_enabled.emit(True if value else False)

    @cached_property
    def sliders(self):
        return [
            AdjustmentSliderWidget(
                name="contrast",
                adjust_option_type=vlcqt.VideoAdjustOption.Contrast,
                min_value=0.0,
                max_value=2.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            AdjustmentSliderWidget(
                name="brightness",
                adjust_option_type=vlcqt.VideoAdjustOption.Brightness,
                min_value=0.0,
                max_value=2.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            AdjustmentSliderWidget(
                name="hue",
                adjust_option_type=vlcqt.VideoAdjustOption.Hue,
                min_value=-180,
                max_value=180,
                tick_interval=180,
                media_player=self.mp,
                parent=self,
            ),
            AdjustmentSliderWidget(
                name="saturation",
                adjust_option_type=vlcqt.VideoAdjustOption.Saturation,
                min_value=0.0,
                max_value=3.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            AdjustmentSliderWidget(
                name="gamma",
                adjust_option_type=vlcqt.VideoAdjustOption.Gamma,
                min_value=0.01,
                max_value=10.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
        ]


# class MediaPlayerAdjustmentsWindow(PopupWindowWidget):
#     def __init__(self, main_win, media_player, parent):
#         super().__init__(parent)
#         self.main_win = main_win
#         self.setWindowTitle("Media Player Adjustments")
#         self.setLayout(QtWidgets.QVBoxLayout(self))
#         self.layout().addWidget(
#             ImageEffectsWidget(parent=self, media_player=media_player)
#         )


# class OpenMediaPlayerAdjustmentsWindowAction(PopupWindowAction):
#     def __init__(self, main_win, media_player):
#         super().__init__(
#             icon=gui.icons.get("open_media_player_adjustments"),
#             text="Media Player Adjustments",
#             widget=MediaPlayerAdjustmentsWindow(
#                 main_win=main_win, media_player=media_player, parent=main_win
#             ),
#             main_win=main_win,
#         )
