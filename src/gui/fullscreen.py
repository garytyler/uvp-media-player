import logging

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QAction, QActionGroup, QMenu

from . import buttons, icons

log = logging.getLogger(__name__)


class StartFullscreenAction(QAction):
    id_attr_names = ("name", "manufacturer", "model")

    def __init__(
        self, qscreen, fullscreen_ctrlr, primary=False, this_screen=False, parent=None
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
        self.set_description_as_text(primary, this_screen)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self, arg):
        print(arg)
        self.fullscreen_ctrlr.start(self)

    def set_description_as_text(self, primary: bool = False, this_screen: bool = False):
        if primary:
            super().setText(f"{self.description}, (primary screen)")
        elif this_screen:
            super().setText(f"{self.description}, (this screen)")
        else:
            super().setText(self.description)


class StopFullscreenAction(QAction):
    def __init__(self, parent, fullscreen_ctrlr):
        super().__init__(parent=parent)
        self.setText("Cancel Fullscreen")
        self.fullscreen_ctrlr = fullscreen_ctrlr
        self.triggered.connect(self.fullscreen_ctrlr.stop)


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
        self.aboutToShow.connect(self.on_aboutToShow)

    def refresh_items(self):
        # Clear action group
        for action in self.action_group.actions():
            self.action_group.removeAction(action)
            del action

        # Add qscreen actions to group
        this_qscreen = self.get_this_qscreen()
        primary_qscreen = self.qguiapp.primaryScreen()
        sorted_qscreens = sorted(self.qguiapp.screens(), key=lambda s: s.name())
        for qscreen in sorted_qscreens:
            is_primary = qscreen == primary_qscreen
            is_this_screen = qscreen == this_qscreen
            action = StartFullscreenAction(
                qscreen=qscreen,
                fullscreen_ctrlr=self.fullscreen_ctrlr,
                primary=is_primary,
                this_screen=is_this_screen,
            )
            action.setCheckable(True)
            action.setIcon(icons.pc_display["normal"])
            self.action_group.addAction(action)
        self.action_group.addAction(self.stop_fs_action)
        self.addActions(self.action_group.actions())

    def get_this_qscreen(self):
        main_win_geo = self.main_win.geometry()
        return self.qguiapp.screenAt(main_win_geo.center())

    def on_aboutToShow(self):
        self.refresh_items()

    def on_triggered(self, action):
        self.fullscreen_ctrlr.start(action.qscreen)


class FullscreenButton(buttons.MenuButton):
    def __init__(self, parent, menu, fullscreen_ctrlr):
        super().__init__(parent=parent, menu=menu, icons=icons.fullscreen_button)
        self.setToolTip("Fullscreen Mode")

        self.fullscreen_ctrlr = fullscreen_ctrlr

        self.menu = menu

        self.switch_icon("off")
        self.update_icon_hover()
        self.setCheckable(True)
        self.setText(getattr(self.menu.actions()[0], "description", ""))

        self.clicked.connect(self.open_menu)
        self.fullscreen_ctrlr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_ctrlr.fullscreenstopped.connect(self.on_fullscreenstopped)

    def on_fullscreenstarted(self, action):
        self.setText(action.description)
        self.switch_icon("on")
        print(self.text())

    def on_fullscreenstopped(self):
        self.switch_icon("off")
