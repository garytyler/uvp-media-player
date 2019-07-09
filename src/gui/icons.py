import qtawesome as qta
from PyQt5.QtGui import QColor

APP_ICONS = None


light_defaults = {
    "color": qta.iconic_font._default_options["color"],
    "color_disabled": QColor(20, 20, 20),
    # "color_disabled": qta.iconic_font._default_options["color_disabled"],
}

color_on = QColor("ForestGreen")
color_off = QColor(150, 150, 150)

# base_text = QColor(160, 160, 160)
other = QColor("Magenta").lighter(170)


class Defaults:
    def __init__(self):
        self.color = QColor(150, 150, 150)
        self.color_on = color_on
        self.color_off_active = color_off.lighter()
        self.color_on_active = color_on.lighter()
        self.color_disabled = QColor(100, 100, 100)


defaults = Defaults()

dark_defaults = {
    "color": color_off,
    "color_disabled": QColor(100, 100, 100),
    "color_on": color_on,
    "color_off_active": color_off.lighter(),
    "color_on_active": color_on.lighter(),
}


class AppIcons:
    def __init__(self):
        self.color_on_active = "blue"
        self.color_off_inactive = defaults.color
        self.unchecked_hover = "white"
        self.checked_hover = QColor(193, 193, 74)
        self.checked_normal = "orange"
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
            color=defaults.color,
            color_on=defaults.color,
            color_off=defaults.color,
            color_on_active=defaults.color_off_active,
            color_off_active=defaults.color_off_active,
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
        self.volume_button = qta.icon("mdi.volume-low")
        # self.volume_button = {
        #     "low": {
        #         "normal": qta.icon("mdi.volume-low"),
        #         "hovered": qta.icon("mdi.volume-low", color=self.unchecked_hover),
        #     },
        #     "medium": {
        #         "normal": qta.icon("mdi.volume-medium"),
        #         "hovered": qta.icon("mdi.volume-medium", color=self.unchecked_hover),
        #     },
        #     "high": {
        #         "normal": qta.icon("mdi.volume-high"),
        #         "hovered": qta.icon("mdi.volume-high", color=self.unchecked_hover),
        #     },
        #     "minus": {
        #         "normal": qta.icon("mdi.volume-minus"),
        #         "hovered": qta.icon("mdi.volume-minus", color=self.unchecked_hover),
        #     },
        #     "plus": {
        #         "normal": qta.icon("mdi.volume-plus"),
        #         "hovered": qta.icon("mdi.volume-plus", color=self.unchecked_hover),
        #     },
        #     "mute": {
        #         "normal": qta.icon("mdi.volume-mute"),
        #         "hovered": qta.icon("mdi.volume-mute", color=self.unchecked_hover),
        #     },
        #     "off": {
        #         "normal": qta.icon("mdi.volume-off"),
        #         "hovered": qta.icon("mdi.volume-off", color=self.unchecked_hover),
        #     },
        # }


def __getattr__(name: str):
    global APP_ICONS
    try:
        return getattr(APP_ICONS, name)
    except AttributeError:
        if APP_ICONS:
            raise
        APP_ICONS = AppIcons()
        return getattr(APP_ICONS, name)
