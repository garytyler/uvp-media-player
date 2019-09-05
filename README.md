# eventvr-player

## Requirements

- python-vlc requires a local installation of [VLC Media Player](https://www.videolan.org/vlc/) (64-bit)

## Environment Variables

- `VLC_ARGS`
- `QT_ARGS`
- `LOG_LEVEL`
- `VR_PLAYER_CONFIG`
- `VR_PLAYER_COLOR_THEME` (overridden by setting in config file)
- `VR_PLAYER_REMOTE_URL` (overridden by setting in config file)

# Build

**NOTE:** As with any `pyinstaller` build, the build process must be run using the targeted OS platform. For more, see [pyinstaller requirements](https://pyinstaller.readthedocs.io/en/stable/requirements.html?highlight=Windows%20XP#requirements).

## Build for Windows

### Build Requirements (Windows)

- Windows 10
- [Python 3.7](https://www.python.org/downloads/)
- [pip](https://pip.readthedocs.io/en/stable/installing/)
- [Pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv) (to verify dependency hashes)

### About the build script (Windows)

Arguments passed to the build script (`build-win.ps1`) will be appended to the `pyinstaller` command line args already called by the script. In most cases, this will invalidate the default definition. For example, the script uses `--log-level=INFO` by default, but running it with `--log-level=DEBUG` will change the `pyinstaller` log level to `DEBUG`. However, some `pyinstaller` args accept multiple definitions, in which case both definitions would apply. See the script itself and [PyInstaller Docs: General Options](https://pyinstaller.readthedocs.io/en/stable/usage.html#general-options) for more info.

### Build Instructions (Windows)

```ps
# Create a virtual environment with dependencies
pipenv sync --dev

# Activate the virtual environment
pipenv shell

# Run windows build script from project root
.\scripts\build-win.ps1 --windowed
```

### Troubleshooting

- Run the build script without `--windowed` to open a console for monitoring standard i/o.
- Use `--debug=imports` to monitor imports.
- Submit an issue
