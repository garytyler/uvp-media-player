import os
from glob import glob
from os.path import commonpath, dirname, join, relpath

from PyInstaller.compat import is_darwin, is_linux, is_win

if is_linux:
    DYLIB_PATTERN = "lib*.so*"
elif is_win:
    DYLIB_PATTERN = "*.dll"
elif is_darwin:
    DYLIB_PATTERN = "*.dylib"


def get_lib_file():
    lib_file = os.environ.get("PYTHON_VLC_LIB_PATH")
    if (
        lib_file and os.path.exists(os.path.dirname(lib_file))
        if is_linux
        else os.path.exists(lib_file)
    ):
        return lib_file
    elif is_linux:
        path = join("/", "usr", "lib", "x86_64-linux-gnu", "libvlc.so")
    elif is_darwin:
        path = join(
            "/", "Applications", "VLC.app", "Contents", "MacOS", "lib", "libvlc.dylib",
        )
    elif is_win:
        path = join("C:\\", "Program Files", "VideoLAN", "VLC", "libvlc.dll")
    if os.path.exists(dirname(path)) if is_linux else os.path.exists(path):
        return path
    raise FileNotFoundError(
        "vlc plugins directory not found."
        "please use environment variable 'PYTHON_VLC_MODULE_PATH'"
    )


def get_plugin_dir():
    plugin_dir = os.environ.get("PYTHON_VLC_MODULE_PATH")
    if plugin_dir and os.path.exists(plugin_dir):
        return plugin_dir
    elif is_linux:
        path = join("/", "usr", "lib", "x86_64-linux-gnu", "vlc", "plugins")
    elif is_darwin:
        path = join("/", "Applications", "VLC.app", "Contents", "MacOS", "plugins")
    elif is_win:
        path = join("C:\\", "", "Program Files", "VideoLAN", "VLC", "plugins")
    if os.path.exists(path):
        return path
    raise FileNotFoundError(
        "vlc plugins directory not found."
        "please use environment variable 'PYTHON_VLC_MODULE_PATH'"
    )


def hook(hook_api):
    if not hook_api.__name__ == "vlc":
        return None

    lib_file = get_lib_file()
    plugin_dir = get_plugin_dir()

    # Get common root
    common_root = commonpath([lib_file, plugin_dir])

    if is_win or is_darwin:
        # Add libvlc binaries
        lib_files = glob(join(dirname(lib_file), DYLIB_PATTERN))
        lib_binaries = []
        for f in lib_files:
            binary_tuple = (f, ".")
            lib_binaries.append(binary_tuple)
        hook_api.add_binaries(lib_binaries)

    if is_darwin:
        # Add plugin binaries
        module_files = glob(join(plugin_dir, DYLIB_PATTERN))
        plugin_binaries = []
        for f in module_files:
            rel_dir = relpath(dirname(f), common_root)
            binary_tuple = (f, rel_dir)
            plugin_binaries.append(binary_tuple)
        hook_api.add_binaries(plugin_binaries)

    if is_linux or is_win:
        # Add plugin binaries
        plugin_src_files = []
        for root, _, __ in os.walk(plugin_dir):
            plugin_src_files.extend(glob(join(root, DYLIB_PATTERN)))
        plugin_binaries = []
        for f in plugin_src_files:
            rel_dir = relpath(dirname(f), common_root)
            bin_tuple = (f, rel_dir if is_win else ".")
            plugin_binaries.append(bin_tuple)
        hook_api.add_binaries(plugin_binaries)
