from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtWidgets import QAction, QFrame, QToolButton


class ActionButton(QToolButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent)
        self.action = action
        self.setDefaultAction(self.action)

        self.setToolTip(self.action.text())
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)


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


class PopUpMenuAction(QAction):
    def __init__(self, icon, text, menu, parent):
        super().__init__(icon, text)
        self.parent = parent
        self.menu = menu
        self.triggered.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.parent.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.parent.mapToGlobal(QPoint(x, y)))
