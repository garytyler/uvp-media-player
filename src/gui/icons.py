import qtawesome as qta
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

APP_ICONS = None


class DarkColors:
    def __init__(self):
        self.color = QColor(150, 150, 150)
        self.color_on = QColor("ForestGreen")
        self.color_off_active = self.color.lighter()
        self.color_on_active = self.color_on.lighter()
        self.color_disabled = QColor(100, 100, 100)


light_defaults = qta.iconic_font._default_options
dark_defaults = DarkColors()


class AppIcons:
    def __init__(self):
        self.fullscreen_enter = qta.icon("mdi.fullscreen")
        self.fullscreen_exit = qta.icon("mdi.fullscreen-exit")
        self.display_screen = qta.icon("mdi.desktop-mac")
        self.playback_mode = {
            "off": qta.icon("mdi.repeat-off"),
            "one": qta.icon("mdi.repeat-once"),
            "all": qta.icon("mdi.repeat"),
        }
        self.play_pause = qta.icon(
            "mdi.play",
            on="mdi.pause",
            off="mdi.play",
            on_active="mdi.pause",
            off_active="mdi.play",
            color=dark_defaults.color,
            color_on=dark_defaults.color,
            color_off=dark_defaults.color,
            color_on_active=dark_defaults.color_off_active,
            color_off_active=dark_defaults.color_off_active,
        )
        self.main_menu_button = qta.icon("mdi.dots-vertical")
        self.stop = qta.icon("mdi.stop")
        self.next_media = qta.icon("mdi.skip-forward")
        self.previous_media = qta.icon("mdi.skip-backward")
        self.zoom_in_button = qta.icon("mdi.magnify-plus-outline")
        self.zoom_out_button = qta.icon("mdi.magnify-minus-outline")
        self.zoom_in_menu_item = qta.icon("mdi.magnify-plus")
        self.zoom_out_menu_item = qta.icon("mdi.magnify-minus")
        self.zoom_menu_button = qta.icon(
            "mdi.magnify",
            "mdi.menu-up",
            options=[{}, {"scale_factor": 0.6, "offset": (0.35, -0.35)}],
        )
        self.server_connected = qta.icon(
            "mdi.server-network",
            on="mdi.server-network",
            off="mdi.server-network-off",
            color_on="green",
            color_on_disabled="green",
            color_off_disabled="red",
        )
        self.server_disconnected = qta.icon("mdi.server-network-off")
        open_file_bg_scale = 0.9
        open_many_bg_scale = 0.8
        bg_fg_multiplier = 0.7
        self.open_file = qta.icon(
            "mdi.file",
            "mdi.play",
            options=[
                {"scale_factor": open_file_bg_scale},
                {
                    "scale_factor": open_file_bg_scale * bg_fg_multiplier,
                    "color": self.palette().window(),
                    "color_on_active": self.palette().window(),
                    "color_off_active": self.palette().window(),
                    "offset": (-0.01, 0.02),
                },
            ],
        )
        self.open_multiple = qta.icon(
            "mdi.file-multiple",
            "mdi.play",
            options=[
                {"scale_factor": open_many_bg_scale},
                {
                    "scale_factor": open_many_bg_scale * bg_fg_multiplier,
                    "color": self.palette().window(),
                    "color_on_active": self.palette().window(),
                    "color_off_active": self.palette().window(),
                    "offset": (0.05, -0.05),
                },
            ],
        )
        self.volume_button = {
            "mute": qta.icon("mdi.volume-mute", disabled="mdi.volume-off"),
            "low": qta.icon("mdi.volume-low", disabled="mdi.volume-off"),
            "medium": qta.icon("mdi.volume-medium", disabled="mdi.volume-off"),
            "high": qta.icon("mdi.volume-high", disabled="mdi.volume-off"),
        }
        self.always_on_top = qta.icon("mdi.window-restore", scale_factor=1.2)

    def palette(self):
        qapp = QApplication.instance()
        return qapp.palette()


def __getattr__(name: str):
    global APP_ICONS
    try:
        return getattr(APP_ICONS, name)
    except AttributeError:
        if APP_ICONS:
            raise
        APP_ICONS = AppIcons()
        return getattr(APP_ICONS, name)
