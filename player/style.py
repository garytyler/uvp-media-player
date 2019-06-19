from os.path import abspath, dirname, join

import qtawesome
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from . import config, icons

LIGHT_PALETTE = None
DARK_PALETTE = None

LIGHT_STYLESHEET = None
DARK_STYLESHEET = join(dirname(abspath(__file__)), "resources/style.qss")


def initialize_style(qapp):
    qapp.setStyle("fusion")
    set_color_theme(config.state.color_theme)


def set_color_theme(name):
    global LIGHT_PALETTE, LIGHT_STYLESHEET

    qapp = QApplication.instance()
    LIGHT_PALETTE = LIGHT_PALETTE if LIGHT_PALETTE else qapp.palette()
    LIGHT_STYLESHEET = qapp.styleSheet()

    if name == "light":
        qtawesome.set_global_defaults(**icons.light_defaults)
        qapp.setPalette(LIGHT_PALETTE)
    elif name == "dark":
        qtawesome.set_global_defaults(**icons.dark_defaults)
        qapp.setPalette(_get_dark_palette())
        with open(DARK_STYLESHEET) as stylesheet:
            qapp.setStyleSheet(stylesheet.read())
    else:
        raise ValueError("Available themes are 'light' or 'dark'")


def _get_dark_palette() -> QPalette:
    p = QPalette()
    # base
    p.setColor(QPalette.WindowText, QColor(180, 180, 180))
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.Light, QColor(180, 180, 180))
    p.setColor(QPalette.Midlight, QColor(110, 110, 110))
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
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))  #
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    return p
