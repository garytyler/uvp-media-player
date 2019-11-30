import logging
from os import getenv

from PyQt5.QtCore import QSettings

log = logging.getLogger(__name__)

_CONFIG_FILE_PATH = getenv("VR_PLAYER_CONFIG", ".user_config")


_SETTINGS = {
    "loop_mode": {"options": ("off", "one", "all"), "default": "off", "type": str},
    "stay_on_top": {"options": (True, False), "default": False, "type": bool},
    "view_scale": {"options": (0.25, 0.5, 1, 2), "default": 1, "type": int},
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


class _Settings(QSettings):
    def __init__(self):
        super().__init__("SeeVR", "Player")
        self.setDefaultFormat(self.IniFormat)


class _State:
    _handlers: dict = {}
    settings = _Settings()

    def __init__(self):
        # Load config from environment variables
        _state = {}
        # env_url = getenv("VR_PLAYER_REMOTE_URL", default=None)
        # if env_url:
        #     _state["url"] = env_url

        # Set values from env vars to local super var
        # Do not call self.__setattr__
        super(_State, self).__setattr__("_state", _state)

    def load(self):
        for key in _SETTINGS.keys():
            self.settings.setValue(key, _SETTINGS[key]["default"])
        # try:
        #     with open(_CONFIG_FILE_PATH, "r") as f:
        #         data = json.loads(f.read())
        # except FileNotFoundError:
        #     log.info("NO CONFIG FILE FOUND")
        #     return

        # for key, value in data.items():
        #     allowed_values = _SETTINGS[key]["options"]
        #     if allowed_values and value not in allowed_values:
        #         raise ValueError(f"Invalid value found in config: '{key}': {value}")
        #     else:
        #         self._update_runtime(key, value)
        #         self.settings.setValue(key, value)
        # log.debug(f"LOADED CONFIG FROM FILE items={self._state}")

    def register_handler(self, key, callback):
        if key not in _SETTINGS.keys():
            raise ValueError
        handlers = self._handlers.get(key)
        if not handlers:
            handlers = []
        handlers.append(callback)

    def _update_runtime(self, key, value):
        handlers = self._handlers.get(key)
        if handlers:
            for h in handlers:
                h(value)
        self._state[key] = value

    def __setattr__(self, key, value):

        # log.debug(f"SET CONFIG ITEM key={key}, value={value}")
        # if self._state.get(key) == value:
        #     return

        allowed_values = _SETTINGS[key]["options"]  # Never throws error
        if allowed_values and value not in allowed_values:
            raise ValueError("Invalid value for this configuration setting")

        self.settings.setValue(key, value)

        # self._update_runtime(key, value)

        # with open(_CONFIG_FILE_PATH, "w") as f:
        #     f.write(json.dumps(self._state))

    def __getattr__(self, key):
        if self.settings.contains(key):
            value = self.settings.value(key)
        else:
            value = _SETTINGS[key]["default"]
        return _SETTINGS[key]["type"](value)

        # try:
        #     value = self.settings.value(key)
        #     # value = self._state.get(key, _SETTINGS[key]["default"])
        # except KeyError as e:
        #     log.critical(e)
        # else:
        #     log.debug(f"GET CONFIG ITEM key={key}, value={value}")
        #     return value


state = _State()


class _Options:
    def __getattr__(self, key):
        return _SETTINGS[key]["options"]


options = _Options()
