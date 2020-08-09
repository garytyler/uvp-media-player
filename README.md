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

- Supported platforms
  - Ubuntu (64-bit)
  - Windows (64-bit)
  - macOS
- [Python 3.7](https://www.python.org/downloads/) w/ development packages
  - If building Python yourself, please rebuild your Python with `--enable-shared` (on Linux) or `--enable-framework` (on Darwin). If using `pyenv`, use the `CONFIGURE_OPTS` environment variable (`CONFIGURE_OPTS="--enable-shared"` on Linux or `CONFIGURE_OPTS="--enable-framework"` on Darwin).
- [VLC](https://www.videolan.org/vlc/) system installation
- [ffprobe](https://ffbinaries.com/downloads) binary for your platform

## Platform-specific

- Ubuntu (64-bit)
  - [fpm](https://fpm.readthedocs.io/en/latest/installing.html)
- Windows (64-bit)
  - [nsis](https://nsis.sourceforge.io/Main_Page)

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

# Support

[Submit an issue](https://github.com/garytyler/seevr-player/issues)
