from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QToolButton


class ActionButton(QToolButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent)
        self.action = action
        self.setDefaultAction(self.action)

        self.setToolTip(self.action.text())
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)


class MenuButton(QToolButton):
    def __init__(self, parent, menu, icon, size):
        super().__init__(parent=parent)
        self.setMenu(menu)
        self.setText(self.menu().title())
        self.setIcon(icon)
        self.setIconSize(QSize(size, size))
        # self.setPopupMode(QToolButton.InstantPopup)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        # self.setToolTip(self.action.text())
        self.setAutoRaise(True)
        self.setCheckable(True)
        # self.setToolButtonStyle(Qt.ToolButtonIconOnly)
