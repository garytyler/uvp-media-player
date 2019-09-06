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

As with any `pyinstaller` build, the build process must be run using the targeted OS platform. For more info, see [PyInstaller Docs: Requirements](https://pyinstaller.readthedocs.io/en/stable/requirements.html?highlight=Windows%20XP#requirements).

## Build for Windows

### Build Requirements (Windows)

- Windows 10
- [VLC 3.0.8](https://www.videolan.org/vlc/)
- [Python 3.7](https://www.python.org/downloads/)
- [pip](https://pip.readthedocs.io/en/stable/installing/)
- [Pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv) (to verify dependency hashes)

### Build Options (Windows)

The build script (`build-win.ps1`) accepts [pyinstaller options](https://pyinstaller.readthedocs.io/en/stable/usage.html#options) as arguments. In the case of a conflict, these args will override those already called in the script.

- To build the project as one `.exe` file, run the build script with `--onefile`. This will override the `--onedir` call that is default in the script.

### Build Instructions (Windows)

```ps
# Create a virtual environment with dependencies
pipenv sync --dev

# Activate the virtual environment
pipenv shell

# Run windows build script from project root
.\scripts\build-win.ps1
```

### Troubleshooting

- Run the build script with `--console` to open a console for monitoring standard i/o.
- Run the build script with `--console` and `--debug=imports` to monitor standard i/o and imports.
- Submit an issue
