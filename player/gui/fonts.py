from PyQt5.QtGui import QFont, QFontInfo


def get_fixed_pitch_font(font: QFont = None) -> QFont:
    font = font if font else QFont()

    # Try QFont.Monospace style hint
    font.setStyleHint(QFont.Monospace)
    if QFontInfo(font).fixedPitch():
        return font

    # Try QFont.TypeWriter style hint
    font.setStyleHint(QFont.TypeWriter)
    if QFontInfo(font).fixedPitch():
        return font

    # Use courier as backup
    font.setFamily("courier")
    return font
