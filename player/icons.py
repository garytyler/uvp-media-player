import qtawesome as qta
from PyQt5.QtGui import QColor

APP_ICONS = None


light_defaults = {
    "color": qta.iconic_font._default_options["color"],
    "color_disabled": QColor(20, 20, 20),
    # "color_disabled": qta.iconic_font._default_options["color_disabled"],
}


dark_defaults = {
    "color": QColor(180, 180, 180),
    "color_disabled": QColor(100, 100, 100),
    # "color_disabled": light_defaults["color_disabled"],
}


class AppIcons:
    def __init__(self):
        self.hover_color = "orange"
        self.main_menu_button = {
            "normal": qta.icon("mdi.dots-vertical"),
            "hovered": qta.icon("mdi.dots-vertical", color=self.hover_color),
        }
        self.stop = qta.icon("mdi.stop")

        self.play_pause_button = {
            "play": {
                "normal": qta.icon("mdi.pause"),
                "hovered": qta.icon("mdi.pause", color=self.hover_color),
            },
            "pause": {
                "normal": qta.icon("mdi.play"),
                "hovered": qta.icon("mdi.play", color=self.hover_color),
            },
        }
        self.playback_mode_button = {
            "off": {
                "normal": qta.icon("mdi.repeat-off"),
                "hovered": qta.icon("mdi.repeat-off", color=self.hover_color),
            },
            "one": {
                "normal": qta.icon("mdi.repeat-once"),
                "hovered": qta.icon("mdi.repeat-once", color=self.hover_color),
            },
            "all": {
                "normal": qta.icon("mdi.repeat"),
                "hovered": qta.icon("mdi.repeat", color=self.hover_color),
            },
        }
        self.skip_forward_button = {
            "normal": qta.icon("mdi.skip-forward"),
            "hovered": qta.icon("mdi.skip-forward", color=self.hover_color),
        }
        self.skip_backward_button = {
            "normal": qta.icon("mdi.skip-backward"),
            "hovered": qta.icon("mdi.skip-backward", color=self.hover_color),
        }
        self.volume_button = {
            "low": {
                "normal": qta.icon("mdi.volume-low"),
                "hovered": qta.icon("mdi.volume-low", color=self.hover_color),
            },
            "medium": {
                "normal": qta.icon("mdi.volume-medium"),
                "hovered": qta.icon("mdi.volume-medium", color=self.hover_color),
            },
            "high": {
                "normal": qta.icon("mdi.volume-high"),
                "hovered": qta.icon("mdi.volume-high", color=self.hover_color),
            },
            "minus": {
                "normal": qta.icon("mdi.volume-minus"),
                "hovered": qta.icon("mdi.volume-minus", color=self.hover_color),
            },
            "plus": {
                "normal": qta.icon("mdi.volume-plus"),
                "hovered": qta.icon("mdi.volume-plus", color=self.hover_color),
            },
            "mute": {
                "normal": qta.icon("mdi.volume-mute"),
                "hovered": qta.icon("mdi.volume-mute", color=self.hover_color),
            },
            "off": {
                "normal": qta.icon("mdi.volume-off"),
                "hovered": qta.icon("mdi.volume-off", color=self.hover_color),
            },
        }


def __getattr__(name: str):
    global APP_ICONS
    try:
        return getattr(APP_ICONS, name)
    except AttributeError:
        if APP_ICONS:
            raise
        APP_ICONS = AppIcons()
        return getattr(APP_ICONS, name)
