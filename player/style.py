from os.path import abspath, dirname, join

import qtawesome
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

# from qtawesome import iconic_font

LIGHT_PALETTE = None
DARK_PALETTE = None

LIGHT_STYLESHEET = None
DARK_STYLESHEET = join(dirname(abspath(__file__)), "resources/style.qss")

QTA_DEFAULTS_LIGHT = {
    "color": QColor(50, 50, 50),
    "color_disabled": QColor(150, 150, 150),
}

QTA_DEFAULTS_DARK = {
    "color": QColor(180, 180, 180),
    "color_disabled": QColor(127, 127, 127),
}


def set_color_theme(name):
    global LIGHT_PALETTE, LIGHT_STYLESHEET

    qapp = QApplication.instance()
    LIGHT_PALETTE = LIGHT_PALETTE if LIGHT_PALETTE else qapp.palette()
    LIGHT_STYLESHEET = qapp.styleSheet()

    if name == "light":
        qtawesome.set_global_defaults(**QTA_DEFAULTS_LIGHT)
        qapp.setPalette(LIGHT_PALETTE)
    elif name == "dark":
        qtawesome.set_global_defaults(**QTA_DEFAULTS_DARK)
        qapp.setPalette(_get_dark_palette())
        with open(DARK_STYLESHEET) as stylesheet:
            qapp.setStyleSheet(stylesheet.read())
    else:
        raise ValueError("Available themes are 'light' or 'dark'")


class p(QPalette):
    def __init__(self):
        super().__init__()
        # base
        self.setColor(QPalette.WindowText, QColor(180, 180, 180))
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.Light, QColor(180, 180, 180))
        self.setColor(QPalette.Midlight, QColor(90, 90, 90))
        self.setColor(QPalette.Dark, QColor(35, 35, 35))
        self.setColor(QPalette.Text, QColor(180, 180, 180))
        self.setColor(QPalette.BrightText, QColor(180, 180, 180))
        self.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        self.setColor(QPalette.Base, QColor(42, 42, 42))
        self.setColor(QPalette.Window, QColor(53, 53, 53))
        self.setColor(QPalette.Shadow, QColor(20, 20, 20))
        self.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
        self.setColor(QPalette.Link, QColor(56, 252, 196))
        self.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        self.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
        # disabled
        self.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        self.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        self.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        self.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        self.setColor(
            QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127)
        )


def _get_dark_palette() -> QPalette:
    p = QPalette()

    # base
    p.setColor(QPalette.WindowText, QColor(180, 180, 180))
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.Light, QColor(180, 180, 180))
    p.setColor(QPalette.Midlight, QColor(90, 90, 90))
    p.setColor(QPalette.Dark, QColor(35, 35, 35))
    p.setColor(QPalette.Text, QColor(180, 180, 180))
    p.setColor(QPalette.BrightText, QColor(180, 180, 180))
    p.setColor(QPalette.ButtonText, QColor(180, 180, 180))
    p.setColor(QPalette.Base, QColor(42, 42, 42))
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.Shadow, QColor(20, 20, 20))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    p.setColor(QPalette.Link, QColor(56, 252, 196))
    p.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    p.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipText, QColor(180, 180, 180))

    # disabled
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    return p


def set_custom_dark_theme(qapp):
    foreground = QColor(229, 229, 229)
    background = QColor(47, 47, 47)

    qtawesome.set_global_defaults(color=foreground)

    p = qapp.palette()
    p.setColor(QPalette.Window, background)
    p.setColor(QPalette.WindowText, foreground)
    p.setColor(QPalette.Base, QColor(63, 63, 63))
    p.setColor(QPalette.AlternateBase, background)
    p.setColor(QPalette.ToolTipBase, foreground)
    p.setColor(QPalette.ToolTipText, foreground)
    p.setColor(QPalette.Text, foreground)
    p.setColor(QPalette.Button, foreground)
    p.setColor(QPalette.ButtonText, foreground)
    p.setColor(QPalette.BrightText, Qt.red)
    p.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    p.setColor(QPalette.HighlightedText, Qt.black)
    p.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
    qapp.setPalette(p)


def set_test_theme(qapp):
    error = QColor(204, 92, 0)

    p = qapp.palette()
    p.setColor(QPalette.AlternateBase, error)
    p.setColor(QPalette.Background, error)
    p.setColor(QPalette.Base, error)
    p.setColor(QPalette.BrightText, error)
    p.setColor(QPalette.Button, error)
    p.setColor(QPalette.ButtonText, error)
    p.setColor(QPalette.Dark, error)
    p.setColor(QPalette.Foreground, error)
    p.setColor(QPalette.Highlight, error)
    p.setColor(QPalette.HighlightedText, error)
    p.setColor(QPalette.Light, error)
    p.setColor(QPalette.Link, error)
    p.setColor(QPalette.LinkVisited, error)
    p.setColor(QPalette.Mid, error)
    p.setColor(QPalette.Midlight, error)
    p.setColor(QPalette.NoRole, error)
    p.setColor(QPalette.PlaceholderText, error)
    p.setColor(QPalette.Shadow, error)
    p.setColor(QPalette.Text, error)
    p.setColor(QPalette.ToolTipBase, error)
    p.setColor(QPalette.ToolTipText, error)
    p.setColor(QPalette.Window, error)
    qapp.setPalette(p)
