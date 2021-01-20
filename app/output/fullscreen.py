import logging
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QMenu

from app.gui import icons
from app.output.status import IconStatusLabel

from .frame import BaseContentFrame

log = logging.getLogger(__name__)


def get_qscreen_at(widget):
    qguiapp = QApplication.instance()
    # return qguiapp.screenAt(widget.geometry().center())
    return qguiapp.screens()[0]


class FullscreenManager(QObject):
    fullscreenstarted = pyqtSignal(QAction)
    fullscreenstopped = pyqtSignal()

    def __init__(self, main_win, main_content_frame, viewpoint_mngr):
        super().__init__()
        self.main_win = main_win
        self.viewpoint_mngr = viewpoint_mngr
        self.main_content_frame = main_content_frame

        self._is_fullscreen = False

    def start(self, action):
        qscreen = action.qscreen
        self.main_content_frame.start_fullscreen(qscreen)
        self._is_fullscreen = True
        self.fullscreenstarted.emit(action)

        # Set a temp frame with a notification in empty window space
        temp_frame = BaseContentFrame()
        temp_frame.setLayout(QtWidgets.QVBoxLayout())
        temp_label = QtWidgets.QLabel(
            f"""- Fullscreen Mode -{os.linesep}{qscreen_description_string(qscreen)}"""
        )
        temp_label.setAlignment(QtCore.Qt.AlignCenter)
        temp_frame.layout().addWidget(temp_label)
        self.main_win.setCentralWidget(temp_frame)

        # Give focus to main window
        self.main_win.activateWindow()

    def stop(self):
        if not self._is_fullscreen:
            return
        self.main_content_frame.stop_fullscreen()
        self._is_fullscreen = False
        self.fullscreenstopped.emit()

    def is_fullscreen(self):
        return self._is_fullscreen


class FullscreenStatusLabel(IconStatusLabel):
    def __init__(self, parent, fullscreen_mngr):
        super().__init__(parent=parent, icon=icons.get("fullscreen"))
        self.fullscreen_mngr = fullscreen_mngr

        self.set_status("Main Window", QIcon.Normal, QIcon.Off)

        self.fullscreen_mngr.fullscreenstarted.connect(self.on_fullscreenstarted)
        self.fullscreen_mngr.fullscreenstopped.connect(self.on_fullscreenstopped)

    @pyqtSlot(QAction)
    def on_fullscreenstarted(self, action: QAction):
        self.set_status(action.text(), QIcon.Normal, QIcon.On)

    @pyqtSlot()
    def on_fullscreenstopped(self):
        self.set_status("Main Window", QIcon.Normal, QIcon.Off)


def qscreen_description_string(qscreen):
    geo = qscreen.geometry()
    id_attr_names = ("name", "manufacturer", "model")
    id_string = ""
    for i in id_attr_names:
        value = getattr(qscreen, i, "")()
        if value:
            id_string += value.strip(".\\")
    return f"{id_string} - ({geo.width()},{geo.height()})"


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
        self.description = qscreen_description_string(qscreen)
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
        self.setIcon(icons.get("fullscreen_exit"))
        self.setEnabled(False)


class FullscreenMenu(QMenu):
    def __init__(self, main_win, fullscreen_mngr):
        super().__init__(parent=main_win)
        self.fullscreen_mngr = fullscreen_mngr
        self.main_win = main_win

        self.setTitle("Fullscreen")
        self.setIcon(icons.get("fullscreen_menu_bttn"))

        self.qguiapp = QApplication.instance()
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
            action.setIcon(icons.get("display_screen"))
            self.action_group.addAction(action)

        self.action_group.addAction(self.stop_fs_action)
        self.addActions(self.action_group.actions())

    def on_menu_aboutToShow(self):
        self.setChecked(self.fullscreen_mngr.is_fullscreen())

    @pyqtSlot(QAction)
    def on_fullscreenstarted(self, action):
        self.stop_fs_action.setEnabled(True)

    @pyqtSlot()
    def on_fullscreenstopped(self):
        self.stop_fs_action.setEnabled(False)

    def on_aboutToShow(self):
        self.refresh_items()
