# eventvr-player

## Requirements

- python-vlc requires a local installation of [VLC Media Player](https://www.videolan.org/vlc/) (64-bit)

## Environment Variables

- `LOG_LEVEL`
- `VR_PLAYER_CONFIG`
- `VR_PLAYER_COLOR_THEME` (overridden by setting in config file)
- `VR_PLAYER_REMOTE_URL` (overridden by setting in config file)

# Build

>**NOTE: This build requires a virtual environment created using using `virtualenv==16.1.0`. See [`pyinstaller` issue #4064](https://github.com/pyinstaller/pyinstaller/issues/4064) for an update on this limitation and other workarounds. To avoid modifying your system `virtualenv` installation, you can create the build virtual environment from a separate temporary virtual environment which itself uses `virtualenv==16.1.0`.**

## Build for Windows (.exe)

### About the Windows build script (`./scripts/build-win.ps1`)

Arguments passed to the build script will be appended to the `pyinstaller` command line args already called by the script. In most cases, this will invalidate the default definition. For example, the script uses `--log-level=INFO` by default, but running it with `--log-level=DEBUG` will change the `pyinstaller` log level to `DEBUG`. However, some `pyinstaller` args accept multiple definitions, in which case both definitions would apply. See the script itself and [PyInstaller Docs: General Options](https://pyinstaller.readthedocs.io/en/stable/usage.html#general-options) for more info.

### Instructions (using Powershell)

```ps
# Using Windows Powershell with a Python 3.7 system installation...

# Install virtualenv version 16.1.0
python3.7 -m pip install virtualenv==16.1.0

# Confirm virtualenv version is 16.1.0
python3.7 -m virtualenv --version

# Create a virtual environment in project root
python3.7 -m virtualenv .venv

# Activate the build virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run windows build script from project root
.\scripts\build-win.ps1
```
