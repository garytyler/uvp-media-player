import json
import os
import sys
from functools import lru_cache


def cached_property(getter):
    return property(lru_cache()(getter))


class PlatformNotSupportedError(Exception):
    def __str__(self):
        return f"Platform not supported: {sys.platform}"


class _Platform:
    @cached_property
    def is_mac(self):
        return sys.platform == "darwin"

    @cached_property
    def is_linux(self):
        return sys.platform == "linux"

    @cached_property
    def is_win(self):
        return sys.platform == "win32"


platform = _Platform()


class BuildInformation(dict):
    base = {
        "name": None,
        "version": None,
        "description": None,
        "author": None,
        "author_email": None,
        "url": None,
        "depends": [],
    }

    def __init__(self, json_path):
        self.update(self.base)
        with open(json_path, "r") as f:
            data = json.loads(f.read())
        self.update(data.get("base", {}))
        if platform.is_mac:
            self.update(data.get("mac", {}))
        elif platform.is_win:
            self.update(data.get("windows", {}))
        elif platform.is_linux:
            self.update(data.get("linux", {}))
        else:
            raise PlatformNotSupportedError

    def __getitem__(self, key: str) -> str:
        if key not in self:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)

    def __setitem__(self, key: str, value: str) -> None:
        raise RuntimeError(f"Build info is read-only:'{self.file_path}'")


class BaseAppContext:
    @cached_property
    def base_dir(self):
        if self.is_frozen:
            raise RuntimeError("base_dir not allowed in freeze or release")
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @cached_property
    def is_frozen(self):
        return hasattr(sys, "frozen") and hasattr(sys, "_MEIPASS")

    def get_resource(self, *path_parts):
        bundle_dir = getattr(
            sys, "_MEIPASS", os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        )
        return os.path.join(bundle_dir, *path_parts)
