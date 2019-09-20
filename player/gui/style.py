from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from ..util import config
from . import icons


def dark_palette():
    p = QPalette()
    # Normal
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.WindowText, QColor(170, 170, 170))
    p.setColor(QPalette.Base, QColor(42, 42, 42))
    p.setColor(QPalette.AlternateBase, QColor(60, 60, 60))
    p.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipText, QColor(170, 170, 170))
    p.setColor(QPalette.Text, QColor(160, 160, 160))
    p.setColor(QPalette.Button, QColor(50, 50, 50))
    p.setColor(QPalette.ButtonText, QColor(170, 170, 170))
    p.setColor(QPalette.BrightText, QColor(230, 230, 230))
    p.setColor(QPalette.Light, QColor(135, 135, 135))
    p.setColor(QPalette.Midlight, QColor(105, 105, 105))
    p.setColor(QPalette.Dark, QColor(33, 33, 33))
    p.setColor(QPalette.Mid, QColor(65, 65, 65))
    p.setColor(QPalette.Shadow, QColor(29, 29, 29))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, QColor(190, 190, 190))
    p.setColor(QPalette.Link, QColor(56, 252, 196))
    p.setColor(QPalette.LinkVisited, QColor(134, 191, 95))
    # Disabled
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))  #
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(75, 75, 75))
    p.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    return p


def set_color_theme(name):
    qapp = QApplication.instance()
    if name == "light":
        icons.initialize_icon_defaults_light(app_palette=qapp.palette())
    elif name == "dark":
        app_palette = dark_palette()
        icons.initialize_icon_defaults_dark(app_palette=app_palette)
        qapp.setPalette(app_palette)
        with open("resources/darkstyle.qss") as stylesheet:
            qapp.setStyleSheet(stylesheet.read())
    else:
        raise ValueError("Available themes are 'light' or 'dark'")


def initialize_style(qapp):
    qapp.setStyle("fusion")
    set_color_theme(config.state.color_theme)
