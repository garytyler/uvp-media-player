from PyQt5 import QtWidgets

from player import base, config, gui

from .about import AboutTextLabel


class EnableHardwareAccelerationCheckbox(QtWidgets.QCheckBox):
    def __init__(self, parent):
        super().__init__(
            text="Enable hardware acceleration (Requires restart)", parent=parent
        )


class PlayerPreferencesWindow(base.modal.BaseModalSettingsDialog):
    def __init__(self, main_win, media_player):
        super().__init__(title="Media Player Preferences", main_win=main_win)

    def create(self, widget):
        widget.setLayout(QtWidgets.QVBoxLayout())

        # VLC Options
        self.vlc_options_group = QtWidgets.QGroupBox(
            title="VLC Options ", parent=widget
        )
        self.vlc_options_lo = QtWidgets.QVBoxLayout()
        self.vlc_options_group.setLayout(self.vlc_options_lo)
        widget.layout().addWidget(self.vlc_options_group)

        self.hw_accel_checkbox = QtWidgets.QCheckBox(
            text="Enable hardware acceleration (Requires restart)", parent=widget
        )
        self.hw_accel_checkbox.setChecked(config.state.hw_accel)
        self.vlc_options_lo.addWidget(self.hw_accel_checkbox)

        # About
        self.about_group = QtWidgets.QGroupBox(title="About", parent=widget)
        self.about_lo = QtWidgets.QVBoxLayout()
        self.about_group.setLayout(self.about_lo)
        widget.layout().addWidget(self.about_group)

        self.about_lo.addWidget(AboutTextLabel(parent=self))

        return widget

    def save(self):
        config.state.hw_accel = True if self.hw_accel_checkbox.isChecked() else False


class OpenMediaPlayerPreferencesWindowAction(
    base.modal.BaseOpenModalSettingsDialogAction
):
    def __init__(self, main_win, media_player):
        super().__init__(
            text="Media Player Preferences",
            main_win=main_win,
            icon=gui.icons.get("open_media_player_preferences"),
        )
        self.media_player = media_player

    def create(self):
        return PlayerPreferencesWindow(
            main_win=self.main_win, media_player=self.media_player
        )
