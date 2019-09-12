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
        qtawesome.set_global_defaults(**icons.QTA_DEFAULTS_LIGHT)
        qapp.setPalette(LIGHT_PALETTE)
    elif name == "dark":
        qtawesome.set_global_defaults(**icons.QTA_DEFAULTS_DARK)
        qapp.setPalette(dark_palette())
        with open(DARK_STYLESHEET) as stylesheet:
            qapp.setStyleSheet(stylesheet.read())
    else:
        raise ValueError("Available themes are 'light' or 'dark'")


def dark_palette():
    p = QPalette()
    # Base
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.WindowText, QColor(170, 170, 170))
    p.setColor(QPalette.Base, QColor(42, 42, 42))
    p.setColor(QPalette.AlternateBase, QColor(57, 57, 57))
    p.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipText, QColor(170, 170, 170))
    p.setColor(QPalette.Text, QColor(160, 160, 160))
    p.setColor(QPalette.Button, QColor(50, 50, 50))
    p.setColor(QPalette.ButtonText, QColor(160, 160, 160))
    p.setColor(QPalette.BrightText, QColor(175, 175, 175))

    p.setColor(QPalette.Light, QColor(135, 135, 135))
    p.setColor(QPalette.Midlight, QColor(105, 105, 105))
    p.setColor(QPalette.Dark, QColor(33, 33, 33))
    p.setColor(QPalette.Mid, QColor(65, 65, 65))
    p.setColor(QPalette.Shadow, QColor(30, 30, 30))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(190, 190, 190))
    p.setColor(QPalette.Link, QColor(56, 252, 196))
    p.setColor(QPalette.LinkVisited, QColor(134, 191, 95))

    # Disabled
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))  #
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(112, 112, 112))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    return p
