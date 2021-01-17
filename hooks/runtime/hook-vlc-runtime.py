import ctypes
import os
import sys
from glob import glob

bundle_dir = getattr(sys, "_MEIPASS")

libvlc_path = None
libvlccore_path = None

if sys.platform.startswith("win"):
    libvlc_path = os.path.join(bundle_dir, "libvlc.dll")
    libvlccore_path = os.path.join(bundle_dir, "libvlccore.dll")
elif sys.platform == "darwin":
    libvlc_path = os.path.join(bundle_dir, "libvlc.dylib")
    libvlccore_path = os.path.join(bundle_dir, "libvlccore.dylib")
elif sys.platform == "linux":
    libvlc_paths = glob(os.path.join(bundle_dir, "libvlc.so.*"))
    libvlccore_paths = glob(os.path.join(bundle_dir, "libvlccore.so.*"))
    if libvlc_paths:
        libvlc_path = libvlc_paths[0]
    if libvlccore_paths:
        libvlccore_path = libvlccore_paths[0]

if libvlc_path:
    os.environ["PYTHON_VLC_LIB_PATH"] = libvlc_path
os.environ["PYTHON_VLC_MODULE_PATH"] = (
    os.path.join(bundle_dir, "plugins")
    if sys.platform.startswith("win")
    else bundle_dir
)
if libvlccore_path:
    ctypes.CDLL(libvlccore_path)
