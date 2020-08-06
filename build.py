import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from glob import glob
from pathlib import Path
from subprocess import check_call

import PyInstaller.__main__
import typer


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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class BuildSettings(dict):
    def __init__(self):
        self.file_path = os.path.join(BASE_DIR, "build.json")
        with open(self.file_path) as f:
            data = json.loads(f.read())
        self.update(data.get("base", {}))
        if is_mac():
            self.update(data.get("mac", {}))
        if is_linux():
            self.update(data.get("linux", {}))
        if is_windows():
            self.update(data.get("windows", {}))

    def __getitem__(self, key: str) -> str:
        if key not in self:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)

    def __setitem__(self, key: str, value: str) -> None:
        raise RuntimeError(f"Build configuration is read-only:'{self.file_path}'")


BUILD_SETTINGS = BuildSettings()
APP_MODULE = os.path.join(BASE_DIR, "app")
FREEZE_DIR = os.path.join(BASE_DIR, "dist", BUILD_SETTINGS["app_name"])
ICON_PNG = Path(BASE_DIR, "icons", "icon.png")


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
                print(f"Dependency source (user) - key={key}, value={value}")

    def __setitem__(self, key: str, value: str) -> None:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        elif not os.path.exists(value):
            raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
        else:
            print(f"Dependency source (default) - key={key}, value={value}")
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)


def create_build_env(self):
    freeze_proc_dir = tempfile.mkdtemp()

    venv_path = os.path.join(freeze_proc_dir, "release_venv")
    check_call([sys.executable, "-m", "venv", venv_path])

    req_txt = os.path.join(freeze_proc_dir, "requirements.txt")
    check_call(["poetry", "update"], shell=True)
    check_call(
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

    check_call([release_python, "-m", "pip", "install", "-r", req_txt])
    check_call([release_python, "-m", "pip", "install", "-r", req_txt])
    return venv_path


def generate_mac_icns_file(src_img_path, dst_dir):
    src_img_stem = Path(src_img_path).stem
    src_img_ext = Path(src_img_path).suffix
    dst_file_path = os.path.join(dst_dir, f"{src_img_stem}.icns")
    iconset_dir = tempfile.mkdtemp(suffix=".iconset")
    widths_scales = []
    for width in [32, 64, 256, 512, 1024]:
        widths_scales.extend([(width, 1), (width, 2)])
    for width, scale in widths_scales:
        icon_name = (
            f"icon_{width}x{width}{src_img_ext}"
            if scale != 1
            else f"icon_{width//2}x{width//2}@2x{src_img_ext}"
        )
        check_call(
            [
                "sips",
                "-z",
                str(width),
                str(width),
                os.path.join(BASE_DIR, "icons", src_img_path),
                "--out",
                os.path.join(iconset_dir, icon_name),
            ]
        )
    check_call(["iconutil", "-c", "icns", iconset_dir, "-o", dst_file_path])
    shutil.rmtree(iconset_dir)
    return dst_file_path


cli = typer.Typer()


@cli.command()
def run():
    if is_mac():
        for i in ["PYTHON_VLC_LIB_PATH", "PYTHON_VLC_MODULE_PATH"]:
            try:
                del os.environ[i]
            except KeyError:
                pass

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    extra_args = sys.argv[2:]
    for arg in extra_args:
        sys.argv.remove(arg)
    os.environ["_BUILD_SCRIPT_RUN_ARGS"] = ",".join(extra_args)

    check_call([sys.executable, APP_MODULE])


class BaseContext:
    delimiter = ";" if is_windows() else ":"

    def __init__(self, base_command):
        self.command = base_command

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class MacFreezeContext(BaseContext):
    def __enter__(self):
        icns_dst_dir = tempfile.mkdtemp()
        icns_file_path = generate_mac_icns_file(
            src_img_path=ICON_PNG, dst_dir=icns_dst_dir
        )
        self.command.append("--osx-bundle-identifier=com.uvp.videoplayer")
        self.command.append(f"--icon={icns_file_path}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        plist_path = Path(
            BASE_DIR,
            "dist",
            f"{BUILD_SETTINGS['app_name']}.app",
            "Contents",
            "Info.plist",
        )
        with open(plist_path, "rb") as f:
            plist_data = plistlib.load(f)
        plist_data.update(
            {
                "CFBundleName": BUILD_SETTINGS["app_name"],
                "CFBundleDisplayName": BUILD_SETTINGS["app_name"],
                "CFBundleExecutable": BUILD_SETTINGS["app_name"],
                "CFBundleIconFile": "icon.icns",
                "LSBackgroundOnly": "0",
                "NSPrincipalClass": "NSApplication",
            }
        )
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)


class LinuxFreezeContext(BaseContext):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class WindowsFreezeContext(BaseContext):
    def __enter__(self):
        self.dep_environ = DependencyEnvironment()
        self.command.append(f"--additional-hooks-dir={os.path.join(BASE_DIR, 'hooks')}")
        # add vlc binary paths args to satisfy warnings during bundling with hooks
        self.command += [
            f"--paths={p}"
            for p in self.dep_environ.values()
            if p and os.path.exists(p) and os.path.isdir(p)
        ]
        self.command += [
            f"--paths={os.path.dirname(p)}"
            for p in self.dep_environ.values()
            if p and os.path.isfile(p)
        ]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FreezeContext:
    def __init__(self, base_command):
        if is_mac():
            self.context = MacFreezeContext(base_command=base_command)
        elif is_linux():
            self.context = LinuxFreezeContext(base_command=base_command)
        elif is_windows():
            self.context = WindowsFreezeContext(base_command=base_command)
        else:
            raise EnvironmentError("Platform not supported.")

    def __enter__(self):
        self.context.__enter__()
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.__exit__(exc_type, exc_val, exc_tb)


@cli.command()
def freeze():
    shutil.rmtree(os.path.join(BASE_DIR, "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(BASE_DIR, "build"), ignore_errors=True)
    delimiter = ";" if is_windows() else ":"
    base_command = [
        "--log-level=INFO",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--hidden-import=PyQt5.QtNetwork",
        "--hidden-import=PyQt5.QtCore",
        f"--name={BUILD_SETTINGS['app_name']}",
        f"--icon={ICON_PNG}",
        f"--add-data={os.path.join(BASE_DIR, 'build.json')}{delimiter}.",
        f"--add-data={os.path.join(BASE_DIR, 'media')}{delimiter}media",
        f"--add-data={os.path.join(BASE_DIR, 'style')}{delimiter}style",
        f"--add-binary=/Users/g/proj/seevr-player/ffmpeg/ffprobe{delimiter}ffmpeg",
    ]
    with FreezeContext(base_command=base_command) as context:
        context.command.append(os.path.join(BASE_DIR, "app", "__main__.py"))
        PyInstaller.__main__.run(context.command)


@cli.command()
def installer():
    if is_mac():
        mounted_dmg_paths = glob(f"/Volumes/{BUILD_SETTINGS['app_name']}*")
        if mounted_dmg_paths:
            raise RuntimeError(
                f"Eject mounted '{BUILD_SETTINGS['app_name']}' installer volumes"
                f" from your system: {repr(mounted_dmg_paths)}"
            )


if __name__ == "__main__":
    verify_supported_platform()
    cli()
