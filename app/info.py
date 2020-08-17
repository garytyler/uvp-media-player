import json
import sys


class BuildInformation(dict):
    base: dict = {
        "name": None,
        "version": None,
        "description": None,
        "author": None,
        "author_email": None,
        "url": None,
        "depends": [],
    }

    def __init__(self, json_path):
        self.json_path = json_path
        self.update(self.base)
        with open(json_path, "r") as f:
            data = json.loads(f.read())
        self.update(data.get("base", {}))
        if sys.platform == "darwin":
            self.update(data.get("mac", {}))
        elif sys.platform.startswith("win"):
            self.update(data.get("windows", {}))
        elif sys.platform == "linux":
            self.update(data.get("linux", {}))
        else:
            raise RuntimeError(f"Platform not supported: {sys.platform}")

    def __getitem__(self, key: str) -> str:
        if key not in self:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)

    def __setitem__(self, key: str, value: str) -> None:
        raise RuntimeError(f"Build info is read-only:'{self.json_path}'")
