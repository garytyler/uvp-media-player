import os
import shutil
import sys
from contextlib import contextmanager
from ctypes.util import find_library
from glob import glob
from importlib import import_module
from os import environ, remove
from os.path import basename, dirname, isdir, isfile, join

import fbs
from fbs.cmdline import command
from fbs_runtime import platform


def _macOS_include_tcl_tk_lib_files_in_bundle():
    """https://github.com/pyinstaller/pyinstaller/issues/3753"""
    app_name = fbs.SETTINGS["app_name"]
    project_dir = fbs.SETTINGS["project_dir"]

    freeze_prep_dir = join(project_dir, "target", app_name)
    freeze_dir = fbs.SETTINGS["freeze_dir"]
    bundle_src = join(freeze_dir, "Contents", "MacOS")

    py_ver_major = str(sys.version_info.major)
    py_ver_minor = str(sys.version_info.minor)
    py_ver_major_minor = ".".join((py_ver_major, py_ver_minor))
    py_ver_dir = "/Library/Frameworks/Python.Framework/Versions"
    py_lib_dir = join(py_ver_dir, py_ver_major_minor, "lib")

    for dir_name in ("tcl", "tk"):
        for targ_root in (freeze_prep_dir, bundle_src):
            targ_dir = join(targ_root, dir_name)

        if isdir(targ_dir):
            shutil.rmtree(targ_dir)
        elif isfile(targ_dir):
            remove(targ_dir)

    for name_start in ("tcl", "tk"):
        src_paths = []
        for src_name in os.listdir(py_lib_dir):
            if src_name.startswith(name_start):
                src_paths.append(join(py_lib_dir, src_name))

        for targ_root in (freeze_prep_dir, bundle_src):
            targ_dir = join(targ_root, name_start.lower())

            for src_path in src_paths:
                if isfile(src_path):
                    src_name = basename(src_path)
                    targ_path = join(targ_dir, src_name)
                    shutil.copy(src_path, targ_path)
                elif isdir(src_path):
                    src_name = basename(src_path)
                    targ_path = join(targ_dir, src_name)
                    shutil.copytree(src_path, targ_path)


@command
def pre_freeze():
    freeze_env = {}
    if platform.is_windows():
        vlc = import_module("vlc")
        app_files_root = vlc.plugin_path
        freeze_env["PYTHON_VLC_LIB_PATH"] = join(app_files_root, vlc.dll._name)
        freeze_env["PYTHON_VLC_MODULE_PATH"] = join(app_files_root, "plugins")
    elif platform.is_ubuntu():
        os_lib_dir = "/usr/lib/x86_64-linux-gnu"
        # python-vlc on linux doesn't need to know where the libvlc dlls or vlc shared  # libraries are, but we do, so we define them using the optional environment
        # variables that are checked by python-vlc on module import.
        freeze_env["PYTHON_VLC_LIB_PATH"] = join(os_lib_dir, find_library("vlc"))
        freeze_env["PYTHON_VLC_MODULE_PATH"] = join(os_lib_dir, "vlc", "plugins")
    elif platform.is_mac():
        vlc = import_module("vlc")
        freeze_env["PYTHON_VLC_LIB_PATH"] = vlc.dll._name
        freeze_env["PYTHON_VLC_MODULE_PATH"] = vlc.plugin_path
    else:
        print("Platform unsupported!")

    freeze_env["FFMPEG_LIB_PATH"] = environ["FFMPEG_LIB_PATH"]

    print(f"Setting {len(freeze_env)} build environment variables...")
    for key, val in freeze_env.items():
        val = environ.setdefault(key, val)
        print(f"  {key}={val}")


@command
def post_freeze():
    freeze_dir = fbs.SETTINGS["freeze_dir"]
    if platform.is_mac():
        resource_dir = join(freeze_dir, "Contents", "Resources")
    else:
        resource_dir = join(freeze_dir)

    # Get shared library source paths
    plugin_source_path = environ["PYTHON_VLC_MODULE_PATH"]
    libvlc_source_path = environ["PYTHON_VLC_LIB_PATH"]

    # Copy libvlc libraries
    os.makedirs(join(resource_dir, "vlc"), exist_ok=True)
    for i in glob(join(dirname(libvlc_source_path), "libvlc*")):
        shutil.copy(i, join(resource_dir, "vlc"))

    # Copy plugin libraries
    shutil.copytree(plugin_source_path, join(join(resource_dir, "vlc"), "plugins"))

    # Copy ffprobe library
    shutil.copy(environ["FFMPEG_LIB_PATH"], join(resource_dir))

    if platform.is_mac():
        _macOS_include_tcl_tk_lib_files_in_bundle()


@contextmanager
def freeze_context():
    pre_freeze()
    print("Freezing...")
    yield
    post_freeze()
    print("Done freezing.")


_COMMAND_CONTEXTS = {"freeze": freeze_context}

if __name__ == "__main__":
    project_dir = dirname(__file__)
    command_context = _COMMAND_CONTEXTS.get(sys.argv[1])
    if command_context:
        with command_context():
            fbs.cmdline.main(project_dir=project_dir)
    else:
        fbs.cmdline.main(project_dir=project_dir)
