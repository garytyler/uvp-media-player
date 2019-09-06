import logging

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QGuiApplication, QIcon
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QSizePolicy, QToolButton

from ..base.popup import PopupMenuAction
from ..gui import icons

log = logging.getLogger(__name__)


def get_qscreen_at(widget):
    qguiapp = QGuiApplication.instance()
    return qguiapp.screenAt(widget.geometry().center())


class FullscreenManager(QObject):
    fullscreenstarted = pyqtSignal(QAction)
    fullscreenstopped = pyqtSignal()

    def __init__(self, main_content_frame, status_widget, viewpoint_mngr):
        super().__init__()
        self.vp_manager = viewpoint_mngr
        self.main_content_frame = main_content_frame
        self.status_widget = status_widget

        self._is_fullscreen = False

        self.status_widget.set_status("Main Window", QIcon.Normal, QIcon.Off)

    def start(self, action):
        qscreen = action.qscreen
        self.main_content_frame.start_fullscreen(qscreen)
        self._is_fullscreen = True
        self.fullscreenstarted.emit(action)
        self.status_widget.set_status(action.text(), QIcon.Normal, QIcon.On)

    def stop(self):
        self.main_content_frame.stop_fullscreen()
        self._is_fullscreen = False
        self.fullscreenstopped.emit()
        self.status_widget.set_status("Main Window", QIcon.Normal, QIcon.Off)

    def is_fullscreen(self):
        return self._is_fullscreen


class StartFullscreenAction(QAction):
    id_attr_names = ("name", "manufacturer", "model")

    def __init__(
        self,
        qscreen,
        fullscreen_mngr,
        is_primary=False,
        is_this_screen=False,
        main_win=None,
    ):
        super().__init__(parent=main_win)
        self._main_win = main_win
        self.qscreen = qscreen
        self.fullscreen_mngr = fullscreen_mngr
        self.geo = self.qscreen.geometry()
        self.width = self.geo.width()
        self.height = self.geo.height()
        self.id_string = ""
        for i in self.id_attr_names:
            value = getattr(self.qscreen, i, "")()
            if value:
                self.id_string += value.strip(".\\")
        self.description = f"{self.id_string} - ({self.width},{self.height})"

        self.set_description_as_text(is_primary, is_this_screen)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self, arg):
        self.fullscreen_mngr.start(self)

    def set_description_as_text(
        self, is_primary: bool = False, is_this_screen: bool = False
    ):
        text = self.description
        if is_primary:
            text += " (primary screen)"
        if is_this_screen:
            text += " (this screen)"
        super().setText(text)


class StopFullscreenAction(QAction):
    def __init__(self, parent, fullscreen_mngr):
        super().__init__(parent=parent)
        self.setText("Cancel Fullscreen")
        self.fullscreen_mngr = fullscreen_mngr
        self.triggered.connect(self.fullscreen_mngr.stop)
        self.setIcon(icons.fullscreen_exit)
        self.setEnabled(False)


class FullscreenMenu(QMenu):
    def __init__(self, main_win, fullscreen_mngr):
        super().__init__(parent=main_win)
        self.fullscreen_mngr = fullscreen_mngr
        self.main_win = main_win

        self.setTitle("Fullscreen")
        self.setIcon(icons.fullscreen_menu_bttn)

        self.qguiapp = QGuiApplication.instance()
        self.action_group = QActionGroup(self)
        self.stop_fs_action = StopFullscreenAction(
            parent=self, fullscreen_mngr=self.fullscreen_mngr
        )
        self.qscreens = None
        self.refresh_items()

        self.fullscreen_mngr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_mngr.fullscreenstopped.connect(self.on_fullscreenstopped)

    def refresh_items(self):
        # Clear action group
        for action in self.action_group.actions():
            self.action_group.removeAction(action)
            del action

        # Add qscreen actions to group
        this_qscreen = get_qscreen_at(self.main_win)
        primary_qscreen = self.qguiapp.primaryScreen()
        sorted_qscreens = sorted(self.qguiapp.screens(), key=lambda s: s.name())
        for qscreen in sorted_qscreens:
            is_primary = qscreen == primary_qscreen
            is_this_screen = qscreen == this_qscreen
            action = StartFullscreenAction(
                qscreen=qscreen,
                fullscreen_mngr=self.fullscreen_mngr,
                is_primary=is_primary,
                is_this_screen=is_this_screen,
                main_win=self.main_win,
            )
            action.setCheckable(True)
            action.setIcon(icons.display_screen)
            self.action_group.addAction(action)

        self.action_group.addAction(self.stop_fs_action)
        self.addActions(self.action_group.actions())

    def on_menu_aboutToShow(self):
        self.setChecked(self.fullscreen_mngr.is_fullscreen())

    def on_fullscreenstarted(self, action):
        self.stop_fs_action.setEnabled(True)

    def on_fullscreenstopped(self):
        self.stop_fs_action.setEnabled(False)

    def on_aboutToShow(self):
        self.refresh_items()
