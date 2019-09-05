import qtawesome
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from ..util import config
from . import icons

LIGHT_PALETTE = None
DARK_PALETTE = None

LIGHT_STYLESHEET = None
DARK_STYLESHEET = "resources/style.qss"


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
        qtawesome.set_global_defaults(**icons.dark_defaults.__dict__)
        qapp.setPalette(_get_dark_palette())
        with open(DARK_STYLESHEET) as stylesheet:
            qapp.setStyleSheet(stylesheet.read())
    else:
        raise ValueError("Available themes are 'light' or 'dark'")


def _get_dark_palette() -> QPalette:
    p = QPalette()
    # Base
    p.setColor(QPalette.WindowText, QColor(175, 175, 175))
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.Light, QColor(135, 135, 135))
    p.setColor(QPalette.Midlight, QColor(110, 110, 110))
    p.setColor(QPalette.Dark, QColor(35, 35, 35))
    p.setColor(QPalette.Text, QColor(175, 175, 175))
    p.setColor(QPalette.BrightText, QColor(175, 175, 175))
    p.setColor(QPalette.ButtonText, QColor(175, 175, 175))
    p.setColor(QPalette.Base, QColor(42, 42, 42))
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    # p.setColor(QPalette.Shadow, QColor(20, 20, 20))
    p.setColor(QPalette.Shadow, QColor(0, 0, 0))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(175, 175, 175))
    p.setColor(QPalette.Link, QColor(56, 252, 196))
    p.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    p.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipText, QColor(175, 175, 175))
    # Disabled
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))  #
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    return p
