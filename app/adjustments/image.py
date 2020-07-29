import config
import vlcqt
from PyQt5 import QtCore, QtWidgets
from utils import cached_property

from ._base import MediaPlayerAdjustmentSlider, MediaPlayerAdjustmentSliderGroup


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


class ImageEffectAdjustmentSlider(MediaPlayerAdjustmentSlider):
    def __init__(self, adjust_option_type, *args, **kwargs):
        self.adjust_option_type = adjust_option_type
        super().__init__(*args, **kwargs)

        self.setOrientation(QtCore.Qt.Horizontal)
        self.setTickPosition(QtWidgets.QSlider.TicksAbove)

    def config_key(self):
        return f"image_effects_{self.name}"

    def _set_model_state(self, value):
        self.mp.video_set_adjust_float(self.adjust_option_type, float(value / 100))

    def _get_model_state(self):
        return self.mp.video_get_adjust_float(self.adjust_option_type)


class ImageEffectsSliderGroup(MediaPlayerAdjustmentSliderGroup):
    def __init__(self, media_player, parent=None):
        super().__init__(media_player=media_player, parent=parent)
        self.media_player = media_player

    def set_enabled_store_state(self, value):
        config.state.image_effects_enable = value

    def get_enabled_store_state(self):
        return config.state.image_effects_enable

    @cached_property
    def sliders(self):
        return [
            ImageEffectAdjustmentSlider(
                name="contrast",
                adjust_option_type=vlcqt.VideoAdjustOption.Contrast,
                min_value=0.0,
                max_value=2.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            ImageEffectAdjustmentSlider(
                name="brightness",
                adjust_option_type=vlcqt.VideoAdjustOption.Brightness,
                min_value=0.0,
                max_value=2.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            ImageEffectAdjustmentSlider(
                name="hue",
                adjust_option_type=vlcqt.VideoAdjustOption.Hue,
                min_value=-180,
                max_value=180,
                tick_interval=180,
                media_player=self.mp,
                parent=self,
            ),
            ImageEffectAdjustmentSlider(
                name="saturation",
                adjust_option_type=vlcqt.VideoAdjustOption.Saturation,
                min_value=0.0,
                max_value=3.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
            ImageEffectAdjustmentSlider(
                name="gamma",
                adjust_option_type=vlcqt.VideoAdjustOption.Gamma,
                min_value=0.01,
                max_value=10.0,
                tick_interval=1,
                media_player=self.mp,
                parent=self,
            ),
        ]


# class ImageEffectsSliderGroup(QtWidgets.QWidget):

#     on_enabled = QtCore.pyqtSignal(bool)

#     def __init__(self, media_player, parent=None):
#         super().__init__(parent=parent)
#         self.mp = media_player

#         self.setWindowTitle("Image Effects")
#         self.setLayout(QtWidgets.QVBoxLayout())

#         self.top_ctrls_lo = QtWidgets.QGridLayout()
#         self.enable_checkbox = QtWidgets.QCheckBox("Enable Image Effects", parent=self)
#         self.top_ctrls_lo.addWidget(self.enable_checkbox)
#         self.layout().addLayout(self.top_ctrls_lo)

#         self.sliders_layout = QtWidgets.QGridLayout()
#         for index, slider in enumerate(self.sliders):
#             label = QtWidgets.QLabel(slider.name.capitalize())
#             self.sliders_layout.addWidget(label, index, 1)
#             self.sliders_layout.addWidget(slider, index, 2)
#             self.on_enabled.connect(slider.setEnabled)
#             self.on_enabled.connect(label.setEnabled)
#         self.layout().addLayout(self.sliders_layout)

#         self.save_button = QtWidgets.QPushButton("Save")
#         self.save_button.setCheckable(False)
#         self.layout().addWidget(self.save_button)
#         self.save_button.clicked.connect(self.save_state)

#         self.reset_button = QtWidgets.QPushButton("Reset")
#         self.reset_button.setCheckable(False)
#         self.layout().addWidget(self.reset_button)
#         self.reset_button.clicked.connect(
#             lambda: [slider.reset_state() for slider in self.sliders]
#         )

#         self.enable_checkbox.stateChanged.connect(self.on_enable_checkbox_stateChanged)
#         self.enable_checkbox.stateChanged.emit(
#             2 if config.state.image_effects_enable else 0
#         )

#         for slider in self.sliders:
#             slider.sliderPressed.connect(lambda: self.save_button.setEnabled(True))

#     def showEvent(self, e):
#         for slider in self.sliders:
#             slider.update_view()

#     @QtCore.pyqtSlot()
#     def save_state(self):
#         """Save all image effect states to settings store."""
#         for slider in self.sliders:
#             slider.save_state()
#         self.save_button.setEnabled(False)

#     @QtCore.pyqtSlot(int)
#     def on_enable_checkbox_stateChanged(self, value):
#         self.mp.video_set_adjust_int(vlcqt.VideoAdjustOption.Enable, 1 if value else 0)
#         self.enable_checkbox.setChecked(value)
#         config.state.image_effects_enable = True if value else False
#         for slider in self.sliders:
#             slider.setEnabled(True if value else False)
#         self.on_enabled.emit(True if value else False)

#     @cached_property
#     def sliders(self):
#         return [
#             ImageEffectAdjustmentSlider(
#                 name="image_effects_contrast",
#                 adjust_option_type=vlcqt.VideoAdjustOption.Contrast,
#                 min_value=0.0,
#                 max_value=2.0,
#                 tick_interval=1,
#                 media_player=self.mp,
#                 parent=self,
#             ),
#             ImageEffectAdjustmentSlider(
#                 name="image_effects_brightness",
#                 adjust_option_type=vlcqt.VideoAdjustOption.Brightness,
#                 min_value=0.0,
#                 max_value=2.0,
#                 tick_interval=1,
#                 media_player=self.mp,
#                 parent=self,
#             ),
#             ImageEffectAdjustmentSlider(
#                 name="image_effects_hue",
#                 adjust_option_type=vlcqt.VideoAdjustOption.Hue,
#                 min_value=-180,
#                 max_value=180,
#                 tick_interval=180,
#                 media_player=self.mp,
#                 parent=self,
#             ),
#             ImageEffectAdjustmentSlider(
#                 name="image_effects_saturation",
#                 adjust_option_type=vlcqt.VideoAdjustOption.Saturation,
#                 min_value=0.0,
#                 max_value=3.0,
#                 tick_interval=1,
#                 media_player=self.mp,
#                 parent=self,
#             ),
#             ImageEffectAdjustmentSlider(
#                 name="image_effects_gamma",
#                 adjust_option_type=vlcqt.VideoAdjustOption.Gamma,
#                 min_value=0.01,
#                 max_value=10.0,
#                 tick_interval=1,
#                 media_player=self.mp,
#                 parent=self,
#             ),
#         ]
