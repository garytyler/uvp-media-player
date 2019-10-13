import json
import logging
from os import getenv

log = logging.getLogger(__name__)

_CONFIG_FILE_PATH = getenv("VR_PLAYER_CONFIG", ".user_config")


_SETTINGS = {
    "loop_mode": {"options": ("off", "one", "all"), "default": "off"},
    "stay_on_top": {"options": (True, False), "default": False},
    "view_scale": {"options": (0.25, 0.5, 1, 2), "default": 1},
    "color_theme": {"options": ("light", "dark"), "default": "dark"},
    "url": {"options": (), "default": "wss://seevr.herokuapp.com/mediaplayer"},
    "volume": {"options": (), "default": 50},  # number between 1 and 100
    "tool_bar_area": {"options": ("top", "bottom"), "default": "bottom"},
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
    },
}


class _State:
    _handlers: dict = {}

    def __init__(self):
        # Load config from environment variables
        _state = {}
        env_url = getenv("VR_PLAYER_REMOTE_URL", default=None)
        if env_url:
            _state["url"] = env_url

        # Set values from env vars to local super var
        # Do not call self.__setattr__
        super(_State, self).__setattr__("_state", _state)

    def load(self):
        try:
            with open(_CONFIG_FILE_PATH, "r") as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            log.info("NO CONFIG FILE FOUND")
            return

        for key, value in data.items():
            allowed_values = _SETTINGS[key]["options"]
            if allowed_values and value not in allowed_values:
                raise ValueError(f"Invalid value found in config: '{key}': {value}")
            else:
                self._update_runtime(key, value)
        log.debug(f"LOADED CONFIG FROM FILE items={self._state}")

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
        log.debug(f"SET CONFIG ITEM key={key}, value={value}")
        if self._state.get(key) == value:
            return

        allowed_values = _SETTINGS[key]["options"]  # Never throws error
        if allowed_values and value not in allowed_values:
            raise ValueError("Invalid value for this configuration setting")

        self._update_runtime(key, value)

        with open(_CONFIG_FILE_PATH, "w") as f:
            f.write(json.dumps(self._state))

    def __getattr__(self, key):
        try:
            value = self._state.get(key, _SETTINGS[key]["default"])
        except KeyError as e:
            log.critical(e)
        else:
            log.debug(f"GET CONFIG ITEM key={key}, value={value}")
            return value


state = _State()


class _Options:
    def __getattr__(self, key):
        return _SETTINGS[key]["options"]


options = _Options()
