from fbs.cmdline import command
from os import path

import fbs
import logging

from ctypes.util import find_library
import subprocess as sp
import imageio_ffmpeg
import os
import sys
import shutil


def _move_libvlc_dlls_to_subdirectory(frozen_dir):
    """Fix for issue with launching exe from same root as libvlc dll files in linux.
    See: https://github.com/oaubert/python-vlc/issues/104
    """
    libvlc_dll_paths = []
    for file_name in os.listdir(frozen_dir):
        file_path = os.path.abspath(os.path.join(frozen_dir, file_name))
        if os.path.isfile(file_path) and file_name.startswith("libvlc"):
            libvlc_dll_paths.append(file_path)

    if not libvlc_dll_paths:
        raise FileNotFoundError("libvlc dlls not found in target dir")

    libvlc_dir_path = os.path.join(frozen_dir, "libvlc")
    os.mkdir(libvlc_dir_path)
    for file_path in libvlc_dll_paths:
        shutil.move(file_path, libvlc_dir_path)


@command
def postfreeze():
    """Make any necessary modifications to the frozen target"""
    log = logging.getLogger()
    app_name = fbs.SETTINGS["app_name"]
    project_dir = fbs.SETTINGS["project_dir"]
    frozen_dir = os.path.join(project_dir, "target", app_name)

    if sys.platform.startswith("win"):
        pass
    elif sys.platform.startswith("darwin"):
        pass
    else:
        _move_libvlc_dlls_to_subdirectory(frozen_dir)
        shutil.copy("/usr/bin/ffprobe", frozen_dir)

    log.info("Post-freeze complete.")


def post_command():
    command = sys.argv[1]
    if command == "freeze":
        postfreeze()


def main():
    fbs.cmdline.main(project_dir=path.dirname(__file__))
    post_command()


if __name__ == "__main__":
    main()
