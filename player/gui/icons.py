import qtawesome as qta
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

APPLICATION_PALETTE = None


def initialize_icon_defaults_light(app_palette):
    global APPLICATION_PALETTE
    APPLICATION_PALETTE = app_palette
    qta.set_global_defaults(**qta.iconic_font._default_options)


def initialize_icon_defaults_dark(app_palette):
    global APPLICATION_PALETTE
    palette = APPLICATION_PALETTE = app_palette
    d = {}
    d["color_on"] = QColor("ForestGreen")
    d["color"] = palette.color(QPalette.Normal, QPalette.ButtonText)
    d["color_on_active"] = d["color_on"].lighter()
    d["color_off_active"] = d["color"].lighter()
    d["color_disabled"] = palette.color(QPalette.Disabled, QPalette.ButtonText)
    qta.set_global_defaults(**d)


class AppIcons:
    def __init__(self):
        global APPLICATION_PALETTE
        self.palette = APPLICATION_PALETTE

        self.fullscreen_menu_bttn = qta.icon("mdi.fullscreen", offset=(0, -0.06))
        self.fullscreen = qta.icon("mdi.fullscreen", scale_factor=1.1)
        self.fullscreen_exit = qta.icon("mdi.fullscreen-exit")
        self.fullscreen_enter = qta.icon("mdi.fullscreen")
        self.display_screen = qta.icon("mdi.desktop-mac")
        self.playback_mode_off = qta.icon("mdi.repeat-off")
        self.playback_mode_one = qta.icon("mdi.repeat-once")
        self.playback_mode_all = qta.icon("mdi.repeat")
        self.play_pause = qta.icon(
            "mdi.play",
            on="mdi.pause",
            off="mdi.play",
            on_active="mdi.pause",
            off_active="mdi.play",
        )
        self.main_menu_button = qta.icon("mdi.dots-vertical")
        self.stop = qta.icon("mdi.stop")
        self.next_media = qta.icon("mdi.skip-forward")
        self.previous_media = qta.icon("mdi.skip-backward")
        self.zoom_in_button = qta.icon("mdi.magnify-plus-outline")
        self.zoom_out_button = qta.icon("mdi.magnify-minus-outline")
        self.zoom_menu_button = qta.icon(
            "mdi.magnify", scale_factor=0.9, offset=(0, -0.05)
        )
        self.zoom_in_menu_item = qta.icon("mdi.magnify-plus")
        self.zoom_out_menu_item = qta.icon("mdi.magnify-minus")
        self.connect_to_server_hovered = qta.icon(
            "mdi.server-network",
            on="mdi.server-network",
            off="mdi.server-network-off",
            color_on="green",
            color_off="red",
        )
        self.connect_to_server_status = qta.icon(
            "mdi.server-network",
            on="mdi.server-network",
            off="mdi.server-network-off",
            off_active="mdi.server-network-off",
            on_active="mdi.server-network",
            color_on_active="green",
            color_off_active="red",
            color_on="darkgreen",
            color_off="crimson",
        )
        self.server_disconnected = qta.icon("mdi.server-network-off")
        open_file_bg_scale = 0.8
        open_many_bg_scale = 0.8
        bg_fg_multiplier = 0.7
        self.open_file = qta.icon(
            "mdi.file",
            "mdi.play",
            options=[
                {"scale_factor": open_file_bg_scale},
                {
                    "scale_factor": open_file_bg_scale * bg_fg_multiplier,
                    "color": self.palette.window(),
                    "color_on_active": self.palette.window(),
                    "color_off_active": self.palette.window(),
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
                    "color": self.palette.window(),
                    "color_on_active": self.palette.window(),
                    "color_off_active": self.palette.window(),
                    "offset": (0.05, -0.05),
                },
            ],
        )
        self.open_file_menu = qta.icon(
            "mdi.file-plus", scale_factor=0.70, offset=(0, -0.06)
        )
        self.volume_button = {
            "mute": qta.icon("mdi.volume-mute", disabled="mdi.volume-off"),
            "low": qta.icon("mdi.volume-low", disabled="mdi.volume-off"),
            "medium": qta.icon("mdi.volume-medium", disabled="mdi.volume-off"),
            "high": qta.icon("mdi.volume-high", disabled="mdi.volume-off"),
        }
        self.always_on_top = qta.icon("mdi.window-restore", scale_factor=1)
        self.open_playlist = qta.icon("mdi.format-list-bulleted")
        self.open_split_view = qta.icon("mdi.view-split-vertical")
        self.open_settings = qta.icon("mdi.cogs")
        self.toolbar_ext_bttn = qta.icon("mdi.menu-right-outline")


_APP_ICONS = None


def __getattr__(name: str):
    global _APP_ICONS
    try:  # If QApplication is needed but not loaded, reinstantialize
        return getattr(_APP_ICONS, name)
    except AttributeError:
        if _APP_ICONS:
            raise
        _APP_ICONS = AppIcons()
        return getattr(_APP_ICONS, name)
