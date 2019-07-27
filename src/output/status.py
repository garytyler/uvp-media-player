import logging

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QWidget,
)

from ..gui import icons

log = logging.getLogger(__name__)


class TextStatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("text_status")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._text = ""
        self._elide_mode = Qt.ElideRight

    def setText(self, text, elide_mode=Qt.ElideRight):
        self._text = text
        self._elide_mode = elide_mode
        self.parent().adjustSize()
        self.update_output(width=self.sizeHint().width())

    def resizeEvent(self, e):
        self.update_output(width=e.size().width())

    def update_output(self, width):
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(self._text, self._elide_mode, width)
        super().setText(elided_text)


class IconStatusLabel(QLabel):
    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self.setObjectName("icon_status")
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.icon = icon

        self.text_lbl = TextStatusLabel(parent=self)
        self.layout().insertWidget(1, self.text_lbl, 0)

        self.icon_lbl = QLabel(parent=self)
        self.icon_size = self.parent().sizeHint().height() * 0.9
        self.layout().insertWidget(0, self.icon_lbl, stretch=0, alignment=Qt.AlignLeft)

    def set_status(self, text, mode, state, elide_mode=Qt.ElideRight):
        self.text_lbl.setText(text, elide_mode)
        pixmap = self.icon.pixmap(self.icon_size, mode, state)
        self.icon_lbl.setPixmap(pixmap)


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(super().sizeHint().height())
        self.setContentsMargins(0, 0, 0, 0)

        self.connect_status_widget = IconStatusLabel(
            parent=self, icon=icons.connect_to_server_status
        )
        self.fullscreen_status_widget = IconStatusLabel(
            parent=self, icon=icons.fullscreen
        )

        for widget in [self.fullscreen_status_widget, self.connect_status_widget]:
            self.insertPermanentWidget(-1, widget)
