import logging

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStatusBar, QWidget

log = logging.getLogger(__name__)


class TextStatusLabel(QLabel):
    def __init__(self, parent: QStatusBar = None):
        super().__init__(parent=parent)
        self._text = ""
        self._elide_mode = Qt.ElideRight
        self._size_hint = QSize()

    def setText(self, text: str, elide_mode=Qt.ElideRight):
        self._text = text
        self._elide_mode = elide_mode
        self._unelided_width = self.fontMetrics().width(text)
        elided_text = self.fontMetrics().elidedText(
            self._text, self._elide_mode, self.width()
        )
        super().setText(elided_text)

    def resizeEvent(self, e):
        width = e.size().width()
        if width <= self._unelided_width:
            width -= 1
        elided_text = self.fontMetrics().elidedText(self._text, self._elide_mode, width)
        super().setText(elided_text)
        super().resizeEvent(e)


class IconStatusLabel(QWidget):
    def __init__(self, parent: QStatusBar = None, icon=None):
        super().__init__(parent)
        self.icon = icon
        self._mode = None
        self._state = None

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.text_lbl = TextStatusLabel(parent=self)
        self.layout().insertWidget(1, self.text_lbl, 1)

        self.icon_lbl = QLabel(parent=self)
        self.icon_size = self.parent().sizeHint().height() * 0.9
        self.layout().insertWidget(0, self.icon_lbl, stretch=0, alignment=Qt.AlignLeft)

    def set_status(self, text, mode, state, elide_mode=Qt.ElideRight):
        self.text_lbl.setText(text, elide_mode)
        pixmap = self.icon.pixmap(self.icon_size, mode, state)
        self.icon_lbl.setPixmap(pixmap)
