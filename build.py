import os
import plistlib
import shutil
import sys
import tempfile
from pathlib import Path
from subprocess import check_call
from textwrap import dedent

import PyInstaller.__main__
import typer
from PIL import Image

from app.info import BuildInformation, platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_INFO = BuildInformation(os.path.join(BASE_DIR, "build.json"))
APP_NAME = BUILD_INFO["name"]
APP_SLUG = BUILD_INFO["name"].replace(" ", "-")
APP_VERSION = BUILD_INFO["version"]
APP_MODULE = os.path.join(BASE_DIR, "app")
FREEZE_DIR = os.path.join(BASE_DIR, "dist", APP_NAME)
ICON_PNG = Path(BASE_DIR, "icons", "icon.png")
if platform.is_mac:
    ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]
elif platform.is_linux:
    ICON_SIZES = [16, 24, 48, 96]
elif platform.is_win:
    ICON_SIZES = [16, 24, 32, 48, 256]


class PlatformNotSupportedError(Exception):
    def __str__(self):
        return f"Platform not supported: {sys.platform}"


def generate_icns(src_img, dst_dir):
    src_img_stem = Path(src_img).stem
    src_img_ext = Path(src_img).suffix
    dst_file_path = os.path.join(dst_dir, f"{src_img_stem}.icns")
    iconset_dir = tempfile.mkdtemp(suffix=".iconset")
    widths_scales = []
    for width in [32, 64, 256, 512, 1024]:
        widths_scales.extend([(width, 1), (width, 2)])
    for width, scale in widths_scales:
        icon_version_name = (
            f"icon_{width}x{width}{src_img_ext}"
            if scale != 1
            else f"icon_{width//scale}x{width//scale}@{scale}x{src_img_ext}"
        )
        img_data = Image.open(src_img)
        img_resized_data = img_data.resize((round(width * scale), round(width * scale)))
        img_resized_data.save(Path(iconset_dir, icon_version_name))
    check_call(["iconutil", "-c", "icns", iconset_dir, "-o", dst_file_path])
    shutil.rmtree(iconset_dir)
    return dst_file_path


def generate_ico(src_img, dst_dir):
    ico_dst_path = Path(dst_dir, f"{Path(src_img).stem}.ico")
    img_data = Image.open(src_img)
    sizes = [(i, i) for i in ICON_SIZES]
    img_data.save(ico_dst_path, format="ico", sizes=sizes)
    return ico_dst_path


class DependencyEnvironment(dict):
    """Set/get dependency environment variables with helpful logs and exceptions."""

    _dependency_keys = [
        "PYTHON_VLC_LIB_PATH",
        "PYTHON_VLC_MODULE_PATH",
        "FFPROBE_BINARY_PATH",
    ]

    def __init__(self):
        super().__init__({})
        for key in self._dependency_keys:
            value = os.environ.get(key)
            if not value:
                super().__setitem__(key, None)
            elif not os.path.exists(value):
                raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
            else:
                super().__setitem__(key, value)
                print(f"Dependency source (user) - key={key}, value={value}")

    def __setitem__(self, key: str, value: str) -> None:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        elif not os.path.exists(value):
            raise FileNotFoundError(f"'{key}' value is non-existent path: {value}")
        else:
            print(f"Dependency source (default) - key={key}, value={value}")
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        if key not in self._dependency_keys:
            raise ValueError(f"'{key}' is not a valid dependency environment variable")
        else:
            return super().__getitem__(key)


cli = typer.Typer()


class BaseContext:
    delimiter = ";" if platform.is_win else ":"

    def __init__(self, base_command):
        self.command = base_command

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class FreezeContextMac(BaseContext):
    def __enter__(self):
        self.icns_tmp_dir = tempfile.mkdtemp()
        generaged_icns = generate_icns(src_img=ICON_PNG, dst_dir=self.icns_tmp_dir)
        self.command.extend(
            [
                "--windowed",
                "--onedir",
                "--osx-bundle-identifier=com.uvp.videoplayer",
                f"--icon={generaged_icns}",
            ]
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        plist_path = Path(
            BASE_DIR, "dist", f"{APP_NAME}.app", "Contents", "Info.plist",
        )
        with open(plist_path, "rb") as f:
            plist_data = plistlib.load(f)
        plist_data.update(
            {
                "CFBundleName": APP_NAME,
                "CFBundleDisplayName": APP_NAME,
                "CFBundleExecutable": APP_SLUG,
                "CFBundleIconFile": "icon.icns",
                "LSBackgroundOnly": "0",
                "NSPrincipalClass": "NSApplication",
            }
        )
        with open(plist_path, "wb") as f:
            plistlib.dump(plist_data, f)
        shutil.rmtree(self.icns_tmp_dir, ignore_errors=True)


class FreezeContextLinux(BaseContext):
    def __enter__(self):
        self.ico_tmp_dir = tempfile.mkdtemp()
        generated_ico = generate_ico(src_img=ICON_PNG, dst_dir=self.ico_tmp_dir)
        self.command.extend(["--windowed", "--onefile", f"--icon={generated_ico}"])

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.ico_tmp_dir, ignore_errors=True)


class FreezeContextWindows(BaseContext):
    def __enter__(self):
        self.ico_tmp_dir = tempfile.mkdtemp()
        generated_ico = generate_ico(src_img=ICON_PNG, dst_dir=self.ico_tmp_dir)
        self.command.extend(["--noconsole", "--onedir", f"--icon={generated_ico}"])
        self.dep_environ = DependencyEnvironment()
        # add vlc binary paths args to satisfy warnings during bundling with hooks
        self.command += [
            f"--paths={p}"
            for p in self.dep_environ.values()
            if p and os.path.exists(p) and os.path.isdir(p)
        ]
        self.command += [
            f"--paths={os.path.dirname(p)}"
            for p in self.dep_environ.values()
            if p and os.path.isfile(p)
        ]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.ico_tmp_dir, ignore_errors=True)


class FreezeContext:
    def __init__(self, base_command):
        if platform.is_mac:
            self.context = FreezeContextMac(base_command=base_command)
        elif platform.is_linux:
            self.context = FreezeContextLinux(base_command=base_command)
        elif platform.is_win:
            self.context = FreezeContextWindows(base_command=base_command)
        else:
            raise EnvironmentError("Platform not supported.")

    def __enter__(self):
        self.context.__enter__()
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.__exit__(exc_type, exc_val, exc_tb)


@cli.command()
def freeze(console=False):
    delimiter = ";" if platform.is_win else ":"
    base_command = [
        "--log-level=INFO",
        "--noconfirm",
        "--clean",
        f"--name={APP_SLUG}",
        f"--add-data={BUILD_INFO.json_path}{delimiter}.",
        f"--add-data={os.path.join(BASE_DIR, 'media')}{delimiter}media",
        f"--add-data={os.path.join(BASE_DIR, 'style')}{delimiter}style",
        f"--add-binary={os.environ['FFPROBE_BINARY_PATH']}{delimiter}.",
        f"--additional-hooks-dir={os.path.join(BASE_DIR, 'hooks', 'analysis')}",
        f"--runtime-hook={Path(BASE_DIR, 'hooks', 'runtime', 'hook-vlc-runtime.py')}",
    ]
    shutil.rmtree(os.path.join(BASE_DIR, "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(BASE_DIR, "build"), ignore_errors=True)
    with FreezeContext(base_command=base_command) as context:
        context.command.append(os.path.join(BASE_DIR, "app", "__main__.py"))
        PyInstaller.__main__.run(context.command)


def create_mac_installer():
    dmgbuild_settings = tempfile.mkstemp()[1]
    with open(dmgbuild_settings, "w") as f:
        f.write(
            dedent(
                f"""
        import biplist
        import os.path
        application = defines.get(
            "app", "{Path(BASE_DIR, "dist", f"{APP_SLUG}.app")}"
        )
        appname = os.path.basename(application)
        def icon_from_app(app_path):
            plist_path = os.path.join(app_path, "Contents", "Info.plist")
            plist = biplist.readPlist(plist_path)
            icon_name = plist["CFBundleIconFile"]
            icon_root, icon_ext = os.path.splitext(icon_name)
            if not icon_ext:
                icon_ext = ".icns"
            icon_name = icon_root + icon_ext
            return os.path.join(app_path, "Contents", "Resources", icon_name)
        size = defines.get("size", None)
        format = defines.get("format", "UDBZ")
        size = defines.get("size", None)
        files = [application]
        symlinks = {{"Applications": "/Applications"}}
        badge_icon = icon_from_app(application)
        icon_locations = {{appname: (140, 120), "Applications": (500, 120)}}
        background = "builtin-arrow"
        show_status_bar = False
        show_tab_view = False
        show_toolbar = False
        show_pathbar = False
        show_sidebar = False
        sidebar_width = 180
        window_rect = ((100, 100), (640, 280))
        default_view = "icon-view"
        show_icon_preview = False
        include_icon_view_settings = "auto"
        include_list_view_settings = "auto"
        arrange_by = None
        grid_offset = (0, 0)
        grid_spacing = 100
        scroll_position = (0, 0)
        label_pos = "bottom"  # or 'right'
        text_size = 16
        icon_size = 128
        list_icon_size = 16
        list_text_size = 12
        list_scroll_position = (0, 0)
        list_sort_by = "name"
        list_use_relative_dates = True
        list_calculate_all_sizes = (False,)
        list_columns = ("name", "date-modified", "size", "kind", "date-added")
        list_column_widths = {{
            "name": 300,
            "date-modified": 181,
            "date-created": 181,
            "date-added": 181,
            "date-last-opened": 181,
            "size": 97,
            "kind": 115,
            "label": 100,
            "version": 75,
            "comments": 300,
        }}
        list_column_sort_directions = {{
            "name": "ascending",
            "date-modified": "descending",
            "date-created": "descending",
            "date-added": "descending",
            "date-last-opened": "descending",
            "size": "descending",
            "kind": "ascending",
            "label": "ascending",
            "version": "ascending",
            "comments": "ascending",
        }}
    """
            )
        )
    dst_dmg_name = f"{APP_SLUG}-v{APP_VERSION}.dmg"
    dst_dmg_path = Path(BASE_DIR, "dist", dst_dmg_name)
    check_call(["dmgbuild", f"-s={dmgbuild_settings}", APP_NAME, dst_dmg_path])
    os.remove(dmgbuild_settings)


def create_windows_installer():
    bundle_dir = Path(BASE_DIR, "dist", f"{APP_SLUG}")
    author = BUILD_INFO["author"]
    installer_nsi = Path(bundle_dir, "Installer.nsi")
    installer_exe = Path(BASE_DIR, "dist", f"{APP_SLUG}-v{APP_VERSION}.exe")
    with open(installer_nsi, "w") as f:
        f.write(
            dedent(
                f"""
        Unicode True
        !include MUI2.nsh
        !include FileFunc.nsh

        ;--------------------------------
        ;Perform Machine-level install, if possible

        !define MULTIUSER_EXECUTIONLEVEL Highest
        ;Add support for command-line args that let uninstaller know whether to
        ;uninstall machine- or user installation:
        !define MULTIUSER_INSTALLMODE_COMMANDLINE
        !include MultiUser.nsh
        !include LogicLib.nsh

        Function .onInit
        !insertmacro MULTIUSER_INIT
        ;Do not use InstallDir at all so we can detect empty $InstDir!
        ${{If}} $InstDir == "" ; /D not used
            ${{If}} $MultiUser.InstallMode == "AllUsers"
                StrCpy $InstDir "$PROGRAMFILES\\{APP_NAME}"
            ${{Else}}
                StrCpy $InstDir "$LOCALAPPDATA\\{APP_NAME}"
            ${{EndIf}}
        ${{EndIf}}
        FunctionEnd

        Function un.onInit
        !insertmacro MULTIUSER_UNINIT
        FunctionEnd

        ;--------------------------------
        ;General

        Name "{APP_NAME}"
        OutFile "{installer_exe}"

        ;--------------------------------
        ;Interface Settings

        !define MUI_ABORTWARNING

        ;--------------------------------
        ;Pages

        !define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the of {APP_NAME}.$\\r$\\n$\\r$\\n$\\r$\\nClick Next to continue."
        !insertmacro MUI_PAGE_WELCOME
        !insertmacro MUI_PAGE_DIRECTORY
        !insertmacro MUI_PAGE_INSTFILES
            !define MUI_FINISHPAGE_NOAUTOCLOSE
            !define MUI_FINISHPAGE_RUN
            !define MUI_FINISHPAGE_RUN_CHECKED
            !define MUI_FINISHPAGE_RUN_TEXT "Run {APP_NAME}"
            !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
        !insertmacro MUI_PAGE_FINISH

        !insertmacro MUI_UNPAGE_CONFIRM
        !insertmacro MUI_UNPAGE_INSTFILES

        ;--------------------------------
        ;Languages

        !insertmacro MUI_LANGUAGE "English"

        ;--------------------------------
        ;Installer Sections

        !define UNINST_KEY \
            "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
        Section
        SetOutPath "$InstDir"
        File /r "..\\{APP_NAME}\\*"
        WriteRegStr SHCTX "Software\\{APP_NAME}" "" $InstDir
        WriteUninstaller "$InstDir\\uninstall.exe"
        CreateShortCut "$SMPROGRAMS\\{APP_NAME}.lnk" "$InstDir\\{APP_NAME}.exe"
        WriteRegStr SHCTX "${{UNINST_KEY}}" "DisplayName" "{APP_NAME}"
        WriteRegStr SHCTX "${{UNINST_KEY}}" "UninstallString" \
            "$\\"$InstDir\\uninstall.exe$\\" /$MultiUser.InstallMode"
        WriteRegStr SHCTX "${{UNINST_KEY}}" "QuietUninstallString" \
            "$\\"$InstDir\\uninstall.exe$\\" /$MultiUser.InstallMode /S"
        WriteRegStr SHCTX "${{UNINST_KEY}}" "Publisher" "{author}"
        ${{GetSize}} "$InstDir" "/S=0K" $0 $1 $2
        IntFmt $0 "0x%08X" $0
        WriteRegDWORD SHCTX "${{UNINST_KEY}}" "EstimatedSize" "$0"

        SectionEnd

        ;--------------------------------
        ;Uninstaller Section

        Section "Uninstall"

        RMDir /r "$InstDir"
        Delete "$SMPROGRAMS\\{APP_NAME}.lnk"
        DeleteRegKey /ifempty SHCTX "Software\\{APP_NAME}"
        DeleteRegKey SHCTX "${{UNINST_KEY}}"

        SectionEnd

        Function LaunchLink
        ;Use explorer.exe to launch with user permissions
        Exec '"$WINDIR\\explorer.exe" "$SMPROGRAMS\\{APP_NAME}.lnk"'
        FunctionEnd
        """
            )
        )
    check_call(["makensis", str(installer_nsi)])


def create_linux_installer():
    deb_dst_name = f"{APP_SLUG.lower()}-v{APP_VERSION}.deb"
    deb_dst_path = Path(BASE_DIR, "dist", deb_dst_name)
    if deb_dst_path.exists():
        os.remove(deb_dst_path)
    pkg_name = APP_NAME.lower()
    args = [
        "fpm",
        "--input-type=dir",
        "--log=info",
        f"--name={pkg_name}",
        f"--version={APP_VERSION}",
        f"--vendor={BUILD_INFO['author']}",
        "--output-type=deb",
        f"--package={deb_dst_path}",
    ]
    if BUILD_INFO["description"]:
        args.append(f"--description={BUILD_INFO['description']}")
    if BUILD_INFO["author_email"]:
        args.append(
            f"--maintainer={BUILD_INFO['author']} <{BUILD_INFO['author_email']}>"
        )
    if BUILD_INFO["url"]:
        args.append(f"--url={BUILD_INFO['url']}")
    for dependency in BUILD_INFO["depends"]:
        args.append(f"--depends={dependency}")

    try:
        check_call(args)
    except FileNotFoundError:
        raise FileNotFoundError(
            "fbs could not find executable 'fpm'. Please install fpm using the "
            "instructions at "
            "https://fpm.readthedocs.io/en/latest/installing.html."
        )


@cli.command()
def installer():
    if platform.is_mac:
        create_mac_installer()
    elif platform.is_win:
        create_windows_installer()
    elif platform.is_linux:
        create_linux_installer()
    else:
        raise PlatformNotSupportedError


@cli.command()
def run():
    os.chdir(BASE_DIR)
    for i in ["PYTHON_VLC_LIB_PATH", "PYTHON_VLC_MODULE_PATH"]:
        try:
            del os.environ[i]
        except KeyError:
            pass
    check_call([sys.executable, APP_MODULE], env=os.environ)


if __name__ == "__main__":
    cli()
