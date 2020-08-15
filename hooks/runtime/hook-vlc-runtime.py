import ctypes
import os
import sys
from glob import glob

if hasattr(sys, "frozen"):
    bundle_dir = getattr(sys, "_MEIPASS")
    if sys.platform == "win32":
        libvlc_path = os.path.join(bundle_dir, "libvlc.dll")
        libvlccore_path = os.path.join(bundle_dir, "libvlccore.dll")
    elif sys.platform == "darwin":
        libvlc_path = os.path.join(bundle_dir, "libvlc.dylib")
        libvlccore_path = os.path.join(bundle_dir, "libvlccore.dylib")
    elif sys.platform == "linux":
        libvlc_path = glob(os.path.join(bundle_dir, "libvlc.so.*"))[0]
        libvlccore_path = glob(os.path.join(bundle_dir, "libvlccore.so.*"))[0]
    os.environ["PYTHON_VLC_LIB_PATH"] = libvlc_path
    os.environ["PYTHON_VLC_MODULE_PATH"] = bundle_dir
    ctypes.CDLL(libvlccore_path)
