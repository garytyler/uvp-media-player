from PyQt5 import QtWidgets

from player import gui
from player.base.popup import PopupWindowAction, PopupWindowWidget

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

        self.tab_widget.addTab(
            image.ImageEffectsSliderGroup(parent=self, media_player=self.mp), "Image"
        )
        self.tab_widget.addTab(
            audio.AudioEqualizerSliderGroupWithPresets(
                parent=self, media_player=self.mp
            ),
            "Audio",
        )


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
