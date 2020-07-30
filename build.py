import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from glob import glob

import typer

log = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_MODULE = os.path.join(BASE_DIR, "app")
FREEZE_DIR = os.path.join(BASE_DIR, "dist", "app")
CONFIG = {}


def load_build_config():
    global CONFIG
    config_path = os.path.join(BASE_DIR, "build.json")
    with open(config_path) as f:
        data = json.loads(f.read())
        CONFIG.update(data.get("base", {}))
        if is_mac():
            CONFIG.update(data.get("mac", {}))
        if is_linux():
            CONFIG.update(data.get("linux", {}))
        if is_windows():
            CONFIG.update(data.get("windows", {}))


def is_mac():
    return sys.platform == "darwin"


def is_linux():
    return sys.platform == "linux"


def is_windows():
    return sys.platform == "win32"


def verify_supported_platform():
    if not any((is_mac(), is_linux(), is_windows())):
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
            value = os.environ.get(key)
            if not value:
                super().__setitem__(key, None)
            elif not os.path.exists(value):
                raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
            else:
                super().__setitem__(key, value)
                log.info(f"Dependency source (user) - key={key}, value={value}")

    def __setitem__(self, key: str, value: str) -> None:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        elif not os.path.exists(value):
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
    def __enter__(self):
        self.dep_environ = DependencyEnvironment()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.freeze_ffmpeg_binaries()

    @property
    def resources_dst_dir(self):
        """Return the same root directory that calling fbs_runtime.get_resource() from a
        frozen app would return.

        In all platforms except Mac, this is the parent directory of the app executable.
        In Mac, it's a separate 'Resources' directory in the .app bundle.
        """
        if is_mac():
            return os.path.join(FREEZE_DIR, "Contents", "Resources")
        else:
            return FREEZE_DIR

    def freeze_ffmpeg_binaries(self) -> None:
        # Make ffmpeg resources dir
        ffmpeg_dst_dir = os.path.join(self.resources_dst_dir, "ffmpeg")
        os.makedirs(ffmpeg_dst_dir, exist_ok=True)

        # Copy ffprobe binary
        ffprobe_bin_src_file = self.dep_environ["FFPROBE_BINARY_PATH"]
        ffprobe_bin_dst_file = os.path.join(
            ffmpeg_dst_dir, os.path.basename(ffprobe_bin_src_file)
        )
        shutil.copy(ffprobe_bin_src_file, ffprobe_bin_dst_file)


def create_build_env(self):
    freeze_proc_dir = tempfile.mkdtemp()

    venv_path = os.path.join(freeze_proc_dir, "release_venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path])

    req_txt = os.path.join(freeze_proc_dir, "requirements.txt")
    subprocess.run(["poetry", "update"], shell=True)
    subprocess.run(
        [
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "-f",
            "requirements.txt",
            ">",
            req_txt,
        ],
        shell=True,
    )

    if is_windows():
        release_python = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        release_python = os.path.join(venv_path, "bin", "python")

    subprocess.run([release_python, "-m", "pip", "install", "-r", req_txt])
    subprocess.run([release_python, "-m", "pip", "install", "-r", req_txt])
    return venv_path


class InstallerCommandContext:
    def __enter__(self):
        if is_mac():
            mounted_dmg_paths = glob(f"/Volumes/{CONFIG['app_name']}*")
            if mounted_dmg_paths:
                raise RuntimeError(
                    f"Eject mounted '{CONFIG['app_name']}' installer volumes"
                    f" from your system: {repr(mounted_dmg_paths)}"
                )

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


cli = typer.Typer()


@cli.command()
def run():
    extra_args = sys.argv[2:]
    for arg in extra_args:
        sys.argv.remove(arg)
    os.environ["_BUILD_SCRIPT_RUN_ARGS"] = ",".join(extra_args)
    subprocess.run([sys.executable, APP_MODULE])


@cli.command()
def freeze():
    with FreezeCommandContext():
        os.chdir(BASE_DIR)
        command = [
            "pyinstaller",
            "--log-level=INFO",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--windowed",
            f"--name={CONFIG['app_name']}",
            "--hidden-import=PyQt5.QtNetwork",
            "--hidden-import=PyQt5.QtCore",
            "--add-data='./resources/*;resources}'",
            "--additional-hooks-dir=./hooks",
            "--console",
            os.path.join(BASE_DIR, "app", "__main__.py"),
        ]
        if is_windows():
            command = ["powershell.exe", "-c"] + command
        subprocess.run(command, shell=True)


@cli.command()
def installer():
    with InstallerCommandContext():
        typer.echo("Installer")


if __name__ == "__main__":
    verify_supported_platform()
    load_build_config()
    cli()
