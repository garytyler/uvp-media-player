import logging

from PyQt5.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QGuiApplication
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QLabel,
    QMenu,
    QSizePolicy,
    QToolButton,
)

from ..controls import base
from ..gui import icons

log = logging.getLogger(__name__)


def get_qscreen_at(widget):
    qguiapp = QGuiApplication.instance()
    return qguiapp.screenAt(widget.geometry().center())


class FullscreenController(QObject):
    fullscreenstarted = pyqtSignal(QAction)
    fullscreenstopped = pyqtSignal()

    def __init__(self, media_frame_layout, viewpoint_manager):
        super().__init__()
        self.vp_manager = viewpoint_manager
        self._is_fullscreen = False
        self.media_frame_layout = media_frame_layout

        self.fullscreenstarted.connect(self.vp_manager.trigger_redraw)
        self.fullscreenstopped.connect(self.vp_manager.trigger_redraw)

    def start(self, action):
        qscreen = action.qscreen
        print(action.description, qscreen)
        self.media_frame_layout.start_fullscreen(qscreen)
        self._is_fullscreen = True
        self.fullscreenstarted.emit(action)

    def stop(self):
        self.media_frame_layout.stop_fullscreen()
        self._is_fullscreen = False
        self.fullscreenstopped.emit()

    def is_fullscreen(self):
        return self._is_fullscreen


class StartFullscreenAction(QAction):
    id_attr_names = ("name", "manufacturer", "model")

    def __init__(
        self,
        qscreen,
        fullscreen_ctrlr,
        is_primary=False,
        is_this_screen=False,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.qscreen = qscreen
        self.fullscreen_ctrlr = fullscreen_ctrlr
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
        self.fullscreen_ctrlr.start(self)

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
    def __init__(self, parent, fullscreen_ctrlr):
        super().__init__(parent=parent)
        self.setText("Cancel Fullscreen")
        self.fullscreen_ctrlr = fullscreen_ctrlr
        self.triggered.connect(self.fullscreen_ctrlr.stop)
        self.setIcon(icons.fullscreen_exit)
        self.setEnabled(False)


class FullscreenMenu(QMenu):
    def __init__(self, main_win, fullscreen_ctrlr):
        super().__init__(parent=main_win)
        self.fullscreen_ctrlr = fullscreen_ctrlr
        self.qguiapp = QGuiApplication.instance()
        self.main_win = main_win
        self.action_group = QActionGroup(self)
        self.stop_fs_action = StopFullscreenAction(
            parent=self, fullscreen_ctrlr=self.fullscreen_ctrlr
        )
        self.qscreens = None
        self.refresh_items()

        self.fullscreen_ctrlr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_ctrlr.fullscreenstopped.connect(self.on_fullscreenstopped)

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
                fullscreen_ctrlr=self.fullscreen_ctrlr,
                is_primary=is_primary,
                is_this_screen=is_this_screen,
            )
            action.setCheckable(True)
            action.setIcon(icons.display_screen)
            self.action_group.addAction(action)

        self.action_group.addAction(self.stop_fs_action)
        self.addActions(self.action_group.actions())

    def on_menu_aboutToShow(self):
        self.setChecked(self.fullscreen_ctrlr.is_fullscreen())

    def on_fullscreenstarted(self, action):
        self.stop_fs_action.setEnabled(True)

    def on_fullscreenstopped(self):
        self.stop_fs_action.setEnabled(False)

    def on_aboutToShow(self):
        self.refresh_items()


class ScreenLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)


class FullscreenMenuAction(base.OpenMenuAction):
    def __init__(self, button, fullscreen_menu, fullscreen_ctrlr):
        super().__init__(
            icons.fullscreen_enter,
            fullscreen_menu.title(),
            menu=fullscreen_menu,
            button=button,
        )
        self.button = button
        self.fullscreen_menu = fullscreen_menu
        self.fullscreen_ctrlr = fullscreen_ctrlr
        self.setToolTip("Fullscreen Mode")
        self.setCheckable(True)

        self.fullscreen_ctrlr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_ctrlr.fullscreenstopped.connect(self.on_fullscreenstopped)
        self.fullscreen_menu.aboutToShow.connect(self.on_menu_aboutToShow)

    def on_menu_aboutToShow(self):
        self.setChecked(self.fullscreen_ctrlr.is_fullscreen())

    def on_fullscreenstarted(self, action):
        self.setChecked(True)

    def on_fullscreenstopped(self):
        self.setChecked(False)


class FullscreenButton(QToolButton):
    def __init__(self, parent, menu, fullscreen_ctrlr, size):
        super().__init__(parent=parent)
        self.fullscreen_ctrlr = fullscreen_ctrlr
        self.menu = menu

        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.sizeHint())

        self.action = FullscreenMenuAction(
            button=self,
            fullscreen_menu=self.menu,
            fullscreen_ctrlr=self.fullscreen_ctrlr,
        )
        self.setDefaultAction(self.action)

        self.curr_screen_desc = ""

        self.fullscreen_ctrlr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_ctrlr.fullscreenstopped.connect(self.on_fullscreenstopped)

    def on_fullscreenstarted(self, action):
        self.update_screen_desc_display(action.description)

    def on_fullscreenstopped(self):
        self.update_screen_desc_display("")

    def update_screen_desc_display(self, text=None):
        if text is not None:
            self.curr_screen_desc = text
        elided_text = self.get_elided_txt(self.curr_screen_desc)
        self.action.setIconText(elided_text)

    def get_elided_txt(self, string):
        return QFontMetrics(self.font()).elidedText(
            string, Qt.ElideRight, self.sizeHint().width()
        )

    def resizeEvent(self, e):
        self.update_screen_desc_display()
