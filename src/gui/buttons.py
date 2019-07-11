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


class OpenFileButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class OpenMultipleButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class ZoomInButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class ZoomOutButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class PlaybackModeButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class PlayPauseButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class PreviousMediaButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class NextMediaButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class FullscreenButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)


class AlwaysOnTopButton(ActionButton):
    def __init__(self, parent, action, size):
        super().__init__(parent=parent, action=action, size=size)
