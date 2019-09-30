import logging
import os
import shutil
import sys
from os import path
from glob import glob
import fbs
from fbs.cmdline import command


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

def _include_tcl_tk_lib_files_in_bundle():
    """https://github.com/pyinstaller/pyinstaller/issues/3753"""

    app_name = fbs.SETTINGS["app_name"]
    project_dir = fbs.SETTINGS["project_dir"]
    bundle_root = os.path.join(project_dir, "target", f"{app_name}.app")
    bundle_src = os.path.join(bundle_root, "Contents", "MacOS")
    frozen_dir = os.path.join(project_dir, "target", app_name)

    py_ver_major = str(sys.version_info.major)
    py_ver_minor = str(sys.version_info.minor)
    py_ver_major_minor  = '.'.join((py_ver_major, py_ver_minor))
    py_ver_dir = '/Library/Frameworks/Python.Framework/Versions'                    
    py_lib_dir = os.path.join(py_ver_dir, py_ver_major_minor, 'lib')
    
    #src_paths = []
    #for src_name in os.listdir(py_lib_dir):
    #    if any((src_name.startswith(s) for s in ('tcl', 'tk', 'Tk'))):
    #        src_paths.append(os.path.join(py_lib_dir, src_name))
    
    for dir_name in ('tcl', 'tk'):
        targ_dir = os.path.join(bundle_src, dir_name)

        if os.path.isdir(targ_dir):
            shutil.rmtree(targ_dir)
        elif os.path.isfile(targ_dir):
            os.remove(targ_dir)

        os.makedirs(targ_dir)

    for stringstart in ("tcl", "tk", "Tk"):  
        src_paths = []
        for src_name in os.listdir(py_lib_dir):
            if src_name.startswith(stringstart) :
                src_paths.append(os.path.join(py_lib_dir, src_name))
        
        targ_dir = os.path.join(bundle_src, stringstart.lower())
        for src_path in src_paths:
            if os.path.isfile(src_path):
                src_name = os.path.basename(src_path)
                targ_path = os.path.join(targ_dir, src_name)
                shutil.copy(src_path, targ_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, targ_dir) 


def _postfreeze():
    """Make any necessary modifications to the frozen target"""
    log = logging.getLogger()
    app_name = fbs.SETTINGS["app_name"]
    project_dir = fbs.SETTINGS["project_dir"]
    frozen_dir = os.path.join(project_dir, "target", app_name)

    if sys.platform.startswith("win"):
        pass
    elif sys.platform.startswith("darwin"):
        _include_tcl_tk_lib_files_in_bundle()
        bundle_root = os.path.join(project_dir, "target", f"{app_name}.app")
        bundle_src = os.path.join(bundle_root, "Contents", "MacOS")
        shutil.copytree(os.path.join(frozen_dir, "lib2to3"), os.path.join(bundle_src, "lib2to3"))
        pass
    else:
        _move_libvlc_dlls_to_subdirectory(frozen_dir)
        shutil.copy("/usr/bin/ffprobe", frozen_dir)

    log.info("Post-freeze complete.")


@command
def postfreeze():
    fbs.init(project_dir=path.dirname(__file__))
    _postfreeze()


def post_command():
    command = sys.argv[1]
    if command == "freeze":
        _postfreeze()


def main():
    fbs.cmdline.main(project_dir=path.dirname(__file__))
    post_command()


if __name__ == "__main__":
    main()
