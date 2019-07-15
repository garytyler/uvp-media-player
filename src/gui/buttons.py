from .components import ActionButton


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
