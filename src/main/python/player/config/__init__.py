import logging

from PyQt5.QtCore import QSettings

log = logging.getLogger(__name__)


SCHEMA = {
    "loop_mode": {"type": str, "default": "off", "options": ("off", "one", "all")},
    "stay_on_top": {"type": bool, "default": False, "options": (True, False)},
    "view_scale": {"type": float, "default": 1, "options": (0.25, 0.5, 1, 2)},
    "auto_resize": {"type": bool, "default": False, "options": (True, False)},
    "color_theme": {"type": str, "default": "dark", "options": ("light", "dark")},
    "url": {
        "type": str,
        "default": "wss://seevr.herokuapp.com/mediaplayer",
        "options": None,
    },
    "volume": {"type": int, "default": 50, "min": 1, "max": 100},
    "tool_bar_area": {"type": str, "default": "bottom", "options": ("top", "bottom")},
    "meta_tags": {
        "type": list,
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
        "options": ([]),
    },
    # Image effects
    # Reference: https://wiki.videolan.org/Documentation:Modules/adjust
    "image_effects_enable": {"type": bool, "default": False, "options": (True, False)},
    "contrast": {"type": float, "default": 1.0, "min": 0.0, "max": 2.0},
    "brightness": {"type": float, "default": 1.0, "min": 0.0, "max": 2.0},
    "hue": {"type": float, "default": 0.0, "min": -180.0, "max": 180.0},
    "saturation": {"type": float, "default": 1.0, "min": 0.0, "max": 3.0},
    "gamma": {"type": float, "default": 1.0, "min": 0.01, "max": 10.0},
    # Audio equalizer
    "audio_eq_enable": {"type": bool, "default": False, "options": (True, False)},
    "audio_eq_preamp": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_60": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_170": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_310": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_600": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_1K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_3K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_6K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_12K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_14K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    "audio_eq_amp_16K": {"type": float, "default": 0.0, "min": -20.0, "max": 20.0},
    # VLC options
    "hw_accel": {"type": bool, "default": True, "options": (True, False)},
}


class Settings(QSettings):
    def __init__(self, organization_name, application_name):
        super().__init__(
            QSettings.IniFormat,
            QSettings.UserScope,
            organization_name,
            application_name,
        )
        from . import state  # noqa: F401


# TODO Change 'config' module name to 'settings' and 'options' obj to 'config'
class _Options:
    def __getattr__(self, key):
        return SCHEMA[key]["options"]


options = _Options()

schema = SCHEMA
