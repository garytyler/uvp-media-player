import sys

from PyQt5.QtCore import QSettings

from player.config import SCHEMA


class _State:
    _handlers: dict = {}

    _state: dict = {}

    def load(self, settings: QSettings):
        for key in SCHEMA.keys():
            val = settings.value(key)
            if val:
                self._state[key] = val
        super().__setattr__("settings", settings)

    def __setattr__(self, key, value):
        options = SCHEMA[key]["options"]  # Never throws error
        if options and value not in options:
            raise ValueError("Invalid value for this configuration setting")
        self.settings.setValue(key, value)

    def __getattr__(self, key):
        value = self.settings.value(
            key, defaultValue=SCHEMA[key]["default"], type=SCHEMA[key]["type"],
        )
        options = SCHEMA[key]["options"]
        if options and value not in options:
            default = SCHEMA[key]["default"]
            self.settings.setValue(key, default)
        return value


# See here for explanation from Guido about why this is acceptable:
# https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
sys.modules[__name__] = _State()  # type: ignore
