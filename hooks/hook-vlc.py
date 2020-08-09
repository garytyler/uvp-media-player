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
    if lib_file and os.path.exists(lib_file):
        return lib_file
    elif is_linux:
        return join("/", "usr", "lib", "x86_64-linux-gnu", "libvlc.so")


def get_mod_dir():
    mod_dir = os.environ.get("PYTHON_VLC_MODULE_PATH")
    if mod_dir and os.path.exists(mod_dir):
        return mod_dir
    elif is_linux:
        return join("/", "usr", "lib", "x86_64-linux-gnu", "vlc", "plugins")


def hook(hook_api):
    if not hook_api.__name__ == "vlc":
        return None

    lib_file = get_lib_file()
    mod_dir = get_mod_dir()

    # Get common root
    common_root = commonpath([lib_file, mod_dir])

    if not is_linux:
        # Add libvlc binaries
        lib_files = glob(join(dirname(lib_file), DYLIB_PATTERN))
        libvlc_binaries = []
        for f in lib_files:
            binary_tuple = (f, "vlc")
            libvlc_binaries.append(binary_tuple)
        hook_api.add_binaries(libvlc_binaries)

    # Add plugin binaries
    plugin_src_files = []
    for root, _, __ in os.walk(mod_dir):
        plugin_src_files.extend(glob(join(root, DYLIB_PATTERN)))
    plugin_binaries = []
    for f in plugin_src_files:
        rel_dir = relpath(dirname(f), common_root)
        bin_tuple = (f, rel_dir)
        plugin_binaries.append(bin_tuple)
    hook_api.add_binaries(plugin_binaries)
