# seevr-player

# Build

As with any `pyinstaller` build, the build process must be run using the targeted OS platform. For more info, see [PyInstaller Docs: Requirements](https://pyinstaller.readthedocs.io/en/stable/requirements.html?highlight=Windows%20XP#requirements).

## Build for Windows

### Requirements

- Windows 10
- [VLC 3.0.8](https://www.videolan.org/vlc/)
- [Python 3.7](https://www.python.org/downloads/)
- [pip](https://pip.readthedocs.io/en/stable/installing/)
- [Pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv) (to verify dependency hashes)

### Options

The build script for Windows (`build-win.ps1`) accepts [pyinstaller options](https://pyinstaller.readthedocs.io/en/stable/usage.html#options) as arguments. In the case of a conflict, these args will override those already called in the script.

### Instructions

```ps
# Create a virtual environment with dependencies
pipenv sync --dev

# Activate the virtual environment
pipenv shell

# Run windows build script from project root
.\scripts\build-win.ps1
```

To debug the build, run the build script with `--console` to open a console to monitor standard i/o, and use `--debug=imports` to also monitor imports. Also, submit an issue.

## Environment Variables

#### `VLC_ARGS`

#### `QT_ARGS`

#### `LOG_LEVELS`

- Comma-delimited (`,`) list of Colon-delimited (`:`) name/value pairs
- Use "`root`" for name of default logger

#### `VR_PLAYER_CONFIG`

- Overrides setting in config file

#### `VR_PLAYER_COLOR_THEME`

- Overridden by setting in config file

#### `VR_PLAYER_REMOTE_URL`

- Overridden by setting in config file
