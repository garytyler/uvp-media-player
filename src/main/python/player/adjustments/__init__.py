from PyQt5 import QtWidgets

from player import gui
from player.common.base.popup import PopupWindowAction, PopupWindowWidget
from player.common.utils import cached_property

from . import audio, image


class MediaPlayerAdjustmentsWindow(PopupWindowWidget):
    def __init__(self, main_win, media_player, parent):
        super().__init__(parent)
        self.main_win = main_win
        self.mp = media_player
        self.setWindowTitle("Media Player Adjustments")
        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.tab_widget = QtWidgets.QTabWidget()
        self.layout().addWidget(self.tab_widget)

        self.tab_widget.addTab(self.image_effects_widget, "Image")
        self.tab_widget.addTab(self.audio_effects_widget, "Audio")

    @cached_property
    def image_effects_widget(self):
        return image.ImageEffectsWidget(parent=self, media_player=self.mp)

    @cached_property
    def audio_effects_widget(self):
        return audio.AudioEqualizerWidget(parent=self, media_player=self.mp)


class OpenMediaPlayerAdjustmentsWindowAction(PopupWindowAction):
    def __init__(self, main_win, media_player):
        super().__init__(
            icon=gui.icons.get("open_media_player_adjustments"),
            text="Media Player Adjustments",
            widget=MediaPlayerAdjustmentsWindow(
                main_win=main_win, media_player=media_player, parent=main_win
            ),
            main_win=main_win,
        )
