import logging
import shutil
import sys
from ctypes.util import find_library
from glob import glob
from importlib import import_module
from os import environ, makedirs
from os.path import basename, dirname, exists, isdir, isfile, join

import fbs
from fbs_runtime import platform

log = logging.getLogger(__name__)


def verify_supported_platform():
    if not any((platform.is_windows(), platform.is_ubuntu(), platform.is_mac())):
        github_url = "https://github.com/garytyler/seevr-player/issues"
        raise RuntimeError(f"Platform unsupported. Request support at {github_url}")


class FreezeCommandContext:
    def __init__(self):
        verify_supported_platform()

    def __enter__(self):
        host_vlc = self.find_host_vlc_binaries()
        dependency_keys_defaults = [
            ("PYTHON_VLC_LIB_PATH", host_vlc["libvlc"]),
            ("PYTHON_VLC_MODULE_PATH", host_vlc["plugins"]),
            ("FFPROBE_BINARY_PATH", find_library("ffprobe")),
        ]
        for key, default_value in dependency_keys_defaults.items():
            self.setdefault_dependency(key, default_value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.freeze_vlc_binaries()
        self.freeze_ffmpeg_binaries()
        self.handle_tcl_tk_lib_issue()

    def find_host_vlc_binaries(self) -> dict:
        """If optional env. vars 'PYTHON_VLC_LIB_PATH' and 'PYTHON_VLC_MODULE_PATH' are
        not set, python-vlc will search for the shared libs it needs on the host
        system.
        """
        result = {"libvlc": None, "plugins": None}

        if platform.is_windows():
            vlc = import_module("vlc")
            app_files_root = vlc.plugin_path
            lib_path = "libvlc.dll"
            result["libvlc"] = join(app_files_root, lib_path)
            result["plugins"] = join(app_files_root, "plugins")
        elif platform.is_ubuntu():
            os_lib_dir = "/usr/lib/x86_64-linux-gnu"
            result["libvlc"] = join(os_lib_dir, find_library("vlc"))
            result["plugins"] = join(os_lib_dir, "vlc", "plugins")
        elif platform.is_mac():
            vlc = import_module("vlc")
            result["libvlc"] = vlc.dll._name
            result["plugins"] = vlc.plugin_path

        # If value is non-existent path, replace value with None
        for key, value in result.items():
            if isinstance(value, str) and not exists(value):
                result[key] = None

        # Provide warning if none found
        if all((not v for v in result.values())):
            log.warning(f"'vlc binaries not found on host {platform.name()} system")

        return result

    def setdefault_dependency(self, key: str, default_value: str) -> str:
        """Set dependency environment variables. Similar to dict.setdefault method with
        appropriate logging and exception msgs.
        """
        user_value = environ.get(key, "")
        if user_value and exists(user_value):
            log.debug(f"Dependency source (user) - key={key}, value={user_value}")
        elif user_value and not exists(user_value):
            raise Exception(f"'{key}' value is non-existent path: {user_value}")
        elif not default_value or not isinstance(default_value, str):
            raise Exception(f"Env. variable '{key}' has invalid value: {default_value}")
        elif not exists(default_value):
            raise Exception(f"Value for '{key}' is non-existent path: {default_value}")
        else:
            environ[key] = default_value
            log.debug(f"Dependency source (default) - key={key}, value={default_value}")
        return environ[key]

    @property
    def freeze_resources_dir(self):
        """Return the same root directory that calling fbs_runtime.get_resource() from
        a frozen app would return.

        In all platforms except Mac, this is the parent directory of the app
        executable. In Mac, it's a separate 'Resources' directory in the .app bundle.
        """
        if platform.is_mac():
            r = join(fbs.SETTINGS["freeze_dir"], "Contents", "Resources")
        else:
            r = fbs.SETTINGS["freeze_dir"]
        makedirs(r, exist_ok=True)
        return r

    @property
    def freeze_binary_dir(self):
        """Always return the parent directory of the frozen app executable.

        In all platforms except Mac, the 'freeze_dir' setting already points to the
        parent directory of the frozen app executable. This routine will do so on Mac
        as well.
        """
        if platform.is_mac():
            r = join(fbs.SETTINGS["freeze_dir"], "Contents", "MacOS")
        else:
            r = fbs.SETTINGS["freeze_dir"]
        makedirs(r, exist_ok=True)
        return r

    def freeze_vlc_binaries(self) -> None:
        # Make ffmpeg resources dir
        freeze_vlc_dir = join(self.freeze_resources_dir, "vlc")
        makedirs(freeze_vlc_dir)

        # Get vlc shared library source paths
        vlc_libvlc_src_file = environ["PYTHON_VLC_LIB_PATH"]
        vlc_plugin_src_dir = environ["PYTHON_VLC_MODULE_PATH"]

        # Copy vlc libvlc binaries
        for i in glob(join(dirname(vlc_libvlc_src_file), "libvlc*")):
            shutil.copy(i, freeze_vlc_dir)

        # Copy vlc plugin binaries
        shutil.copytree(vlc_plugin_src_dir, join(freeze_vlc_dir, "plugins"))

    def freeze_ffmpeg_binaries(self) -> None:
        # Make ffmpeg resources dir
        freeze_ffmpeg_dir = join(self.freeze_resources_dir, "ffmpeg")
        makedirs(freeze_ffmpeg_dir)

        # Copy ffprobe binary
        ffprobe_bin_src_file = environ["FFPROBE_BINARY_PATH"]
        ffprobe_bin_dst_file = join(freeze_ffmpeg_dir, basename(ffprobe_bin_src_file))
        shutil.copy(ffprobe_bin_src_file, ffprobe_bin_dst_file)

    def handle_tcl_tk_lib_issue(self):
        """https://github.com/pyinstaller/pyinstaller/issues/3753"""
        if platform.is_mac():
            py_version = ".".join((str(i) for i in sys.version_info[:2]))
            lib_dir = f"/Library/Frameworks/Python.framework/Versions/{py_version}/lib"
            for dst_dir_name, globspecs in [("tcl", ["tcl*"]), ("tk", ["tk*", "Tk*"])]:
                dst_dir_path = join(self.freeze_binary_dir, dst_dir_name)
                makedirs(dst_dir_path, exist_ok=True)
                for globspec in globspecs:
                    for i in glob(join(lib_dir, globspec)):
                        if isfile(i):
                            shutil.copy2(i, dst_dir_path)
                        elif isdir(i):
                            shutil.copytree(i, join(dst_dir_path, basename(i)))


COMMAND_CONTEXTS = {"freeze": FreezeCommandContext}

if __name__ == "__main__":
    log.info(f"{__file__} - {platform.name()}")
    project_dir = dirname(__file__)
    command_context = COMMAND_CONTEXTS.get(sys.argv[1])
    if command_context:
        with command_context():
            fbs.cmdline.main(project_dir=project_dir)
    else:
        fbs.cmdline.main(project_dir=project_dir)
