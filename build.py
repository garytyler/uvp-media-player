import logging
import os
import shutil
import sys
from os import environ, makedirs
from os.path import basename, dirname, exists, join

import fbs
from fbs import cmdline
from fbs_runtime import platform

log = logging.getLogger(__name__)


def verify_supported_platform():
    if not any((platform.is_windows(), platform.is_ubuntu(), platform.is_mac())):
        github_url = "https://github.com/garytyler/seevr-player/issues"
        raise RuntimeError(f"Platform unsupported. Request support at {github_url}")


class DependencyEnvironment(dict):
    """Set/get dependency environment variables with helpful logs and exceptions."""

    _dependency_keys = [
        "PYTHON_VLC_LIB_PATH",
        "PYTHON_VLC_MODULE_PATH",
        "FFPROBE_BINARY_PATH",
    ]

    def __init__(self):
        super().__init__({})
        for key in self._dependency_keys:
            value = environ.get(key)
            if not value:
                super().__setitem__(key, None)
            elif not exists(value):
                raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
            else:
                super().__setitem__(key, value)
                log.info(f"Dependency source (user) - key={key}, value={value}")

    def __setitem__(self, key: str, value: str) -> None:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        elif not exists(value):
            raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
        else:
            log.info(f"Dependency source (default) - key={key}, value={value}")
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)


class FreezeCommandContext:
    def __init__(self):
        verify_supported_platform()

    def __enter__(self):
        self.dep_environ = DependencyEnvironment()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.freeze_ffmpeg_binaries()

    @property
    def resources_dst_dir(self):
        """Return the same root directory that calling fbs_runtime.get_resource() from a
        frozen app would return.

        In all platforms except Mac, this is the parent directory of the app executable.
        In Mac, it's a separate 'Resources' directory in the .app bundle.
        """
        if platform.is_mac():
            return join(fbs.SETTINGS["freeze_dir"], "Contents", "Resources")
        else:
            return fbs.SETTINGS["freeze_dir"]

    def freeze_ffmpeg_binaries(self) -> None:
        # Make ffmpeg resources dir
        ffmpeg_dst_dir = join(self.resources_dst_dir, "ffmpeg")
        makedirs(ffmpeg_dst_dir, exist_ok=True)

        # Copy ffprobe binary
        ffprobe_bin_src_file = self.dep_environ["FFPROBE_BINARY_PATH"]
        ffprobe_bin_dst_file = join(ffmpeg_dst_dir, basename(ffprobe_bin_src_file))
        shutil.copy(ffprobe_bin_src_file, ffprobe_bin_dst_file)


class RunCommandContext:
    def __init__(self):
        verify_supported_platform()

    def __enter__(self):
        extra_args = sys.argv[2:]
        for arg in extra_args:
            sys.argv.remove(arg)
        os.environ["_SEEVR_PLAYER_BUILD_LAUNCH_MEDIA"] = ",".join(extra_args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


COMMAND_CONTEXTS = {"freeze": FreezeCommandContext, "run": RunCommandContext}

if __name__ == "__main__":
    log.info(f"{__file__} - command='{sys.argv[1:]}', platform={platform.name()}")
    project_dir = dirname(__file__)
    fbs.init(project_dir)  # TODO Can I copy dependencies to freeze dir before freezing?
    try:
        command = sys.argv[1]
    except IndexError:
        log.error("Error: Script '{__file__}' requires a command.")
    else:
        context = COMMAND_CONTEXTS.get(command)
        if context:
            # Ignore type checking bug. See: https://github.com/python/mypy/issues/5512
            with context():  # type: ignore
                cmdline.main(project_dir=project_dir)
        else:
            cmdline.main(project_dir=project_dir)
