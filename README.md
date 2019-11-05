<center> <h1>seevr-player</h1> </center>

# Application Environment Variables

- `VLC_ARGS`
- `VR_PLAYER_LOG_FILE`
- `VR_PLAYER_LOG_LEVELS`
  - Comma-delimited (`,`) list of Colon-delimited (`:`) name/value pairs
  - Use "`root`" for name of default logger
- `VR_PLAYER_CONFIG`
- `VR_PLAYER_REMOTE_URL`
- Overridden by setting in config file

# Build

As with any `pyinstaller` build, the build process must be run on the target platform. For more info, see [PyInstaller Docs: Requirements](https://pyinstaller.readthedocs.io/en/stable/requirements.html?highlight=Windows%20XP#requirements).

## Build Requirements

- Supported platforms: Ubuntu 18.04, Windows 10, macOS Mojave 10.14
- [Python 3.6](https://www.python.org/downloads/)
- [VLC](https://www.videolan.org/vlc/)

NOTE: If using `pipenv`, you will likely encounter [pyinstaller issue #4064](https://github.com/pyinstaller/pyinstaller/issues/4064) with an error like `ImportError: cannot import 'distutils'` or similar when launching the application. A simple workaround is to rollback `virtualenv` to version 16.1 (`virtualenv==16.1`), in both your system `pip` and your virtual environment `pip`.

## Build Environment Variables

A few external dependencies are required. They can be specified with paths set to environment variables.

- `FFPROBE_BINARY_PATH`
  - Path to a static `ffprobe` binary for the target platform. You can can download this at [ffbinaries.com](https://ffbinaries.com)
- `PYTHON_VLC_LIB_PATH`
  - Path to VLC 'libvlc' dynamically linked library
  - Some typical values are:
    - Windows: `C:\Program Files\VideoLAN\VLC\libvlc.dll`
    - Ubuntu: `/usr/lib/x86_64-linux-gnu/libvlc.so`
    - macOS: `/Applications/VLC.app/Contents/MacOS/lib/libvlc.dylib`
- `PYTHON_VLC_MODULE_PATH`
  - Path to VLC plugins directory for the installed VLC application.
  - Some typical values are:
    - Windows: `C:\Program Files\VideoLAN\VLC\plugins`
    - Ubuntu: `/usr/lib/x86_64-linux-gnu/vlc/plugins`
    - macOS: `/Applications/VLC.app/Contents/MacOS/plugins`

## Build Script

Run [fbs](https://build-system.fman.io/manual/) build commands with the provided `build.py` script.

```bash
python build.py clean
python build.py freeze
python build.py installer
```

# Support

[Submit an issue](https://github.com/garytyler/seevr-player/issues)
