from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QAction, QFrame, QToolButton


class PopUpWidget(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("popup")
        self.setFrameShape(QFrame.Box)
        self.setWindowFlags(self.windowFlags() | Qt.Popup)

    def popup(self):
        self.show()
        menu_size = self.size()
        butt_rect = self.parent.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.move(self.parent.mapToGlobal(QPoint(x, y)))


class PopUpWidgetAction(QAction):
    def __init__(self, text: str, widget: PopUpWidget, button: QToolButton):
        super().__init__(text, parent=widget)
        self.button = button
        self.text = text
        self.widget = widget
        self.triggered.connect(self.widget.popup)


class OpenMenuAction(QAction):
    def __init__(self, icon, text, menu, button):
        super().__init__(icon, text, parent=button)
        self.button = button
        self.menu = menu
        self.triggered.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.button.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.button.mapToGlobal(QPoint(x, y)))
