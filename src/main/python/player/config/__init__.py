import logging

from PyQt5.QtCore import QSettings

log = logging.getLogger(__name__)


SCHEMA = {
    "loop_mode": {"options": ("off", "one", "all"), "default": "off", "type": str},
    "stay_on_top": {"options": (True, False), "default": False, "type": bool},
    "view_scale": {"options": (0.25, 0.5, 1, 2), "default": 1, "type": float},
    "auto_resize": {"options": (True, False), "default": False, "type": bool},
    "color_theme": {"options": ("light", "dark"), "default": "dark", "type": str},
    "url": {
        "options": (),
        "default": "wss://seevr.herokuapp.com/mediaplayer",
        "type": str,
    },
    "volume": {"options": (), "default": 50, "type": int},  # number between 1 and 100
    "tool_bar_area": {"options": ("top", "bottom"), "default": "bottom", "type": str},
    "meta_tags": {
        "options": ([]),
        "default": [
            "title",
            "duration",
            "artist",
            "genre",
            "album",
            "track number",
            "description",
            "uri",
            "id",
            "rating",
            "disc number",
            "date",
        ],
        "type": str,
    },
}


class Settings(QSettings):
    def __init__(self, organization_name, application_name):
        super().__init__(
            QSettings.IniFormat,
            QSettings.UserScope,
            organization_name,
            application_name,
        )


class _Options:
    def __getattr__(self, key):
        return SCHEMA[key]["options"]


options = _Options()
