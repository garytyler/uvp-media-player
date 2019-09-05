import logging
from os import path

from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QMainWindow,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .. import vlcqt
from ..base.docking import DockableWidget
from ..base.popup import PopupWindowAction, PopupWindowWidget
from ..gui import icons
from . import files
from .model import MediaItem, PlaylistModel

log = logging.getLogger(__name__)


class PlaylistView(QTreeView):
    def __init__(self, playlist_player, parent):
        super().__init__(parent=parent)
        self.pl_player = playlist_player

        self.setSelectionBehavior(self.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)
        self.setExpandsOnDoubleClick(False)
        self.setItemsExpandable(False)
        self.setAllColumnsShowFocus(True)
        self.setRootIsDecorated(False)

        self.doubleClicked.connect(self.on_doubleClicked)

    def on_doubleClicked(self, index):
        self.pl_player.load_media(index=index)

    def add_media(self, paths):
        paths = files.get_media_paths(paths)
        if not paths:
            return None

        items = []
        for p in paths:
            item = MediaItem(path.abspath(p))
            items.append(item)

        model = self.model()
        if model:
            for i in items:
                model.appendRow(i)
        else:
            model = PlaylistModel(parent=self)
            self.setModel(model)
            for i in items:
                model.appendRow(i)
            self.pl_player.load_media(index=items[0].index(), play=False)


class PopupPlaylistWindow(PopupWindowWidget):
    def __init__(self, playlist_view, main_win):
        super().__init__(parent=None)
        self.playlist_view = playlist_view
        self.main_win = main_win

        self.setWindowTitle("Playlist")
        self.setLayout(QVBoxLayout(self))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.playlist_view)

    def showEvent(self, e):
        width = self.sizeHint().width()
        pos = self.main_win.pos()
        pos.setX(pos.x() - width)
        self.move(pos)

        super().showEvent(e)


class OpenPlaylistAction(QAction):
    def __init__(
        self, parent, split_view, playlist_view, frame_size_mngr, main_content_frame
    ):
        super().__init__(parent=parent)
        self.parent = parent
        self.split_view = split_view
        self.pl_editor = playlist_view
        self.frame_size_mngr = frame_size_mngr
        self.main_content_frame = main_content_frame
        self.setIcon(icons.open_split_view)
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)

        self.toggled.connect(self.setChecked)

        self.setShortcutVisibleInContextMenu(True)
        self.setCheckable(True)
        self.setChecked(False)

    @pyqtSlot(bool)
    def setChecked(self, checked):
        self.split_view.toggle_playlist(checked)


class PopupPlaylistAction(PopupWindowAction):
    def __init__(self, playlist_view, main_win):
        self.playlist_win = PopupPlaylistWindow(
            playlist_view=playlist_view, main_win=main_win
        )
        super().__init__(
            icon=icons.open_playlist,
            text="Open Playlist",
            widget=self.playlist_win,
            main_win=main_win,
        )


class DockablePlaylist(DockableWidget):
    def __init__(self, parent, playlist_view):
        super().__init__(title="Playlist", parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWidget(playlist_view)
        self.setVisible(False)

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setIcon(icons.open_playlist)
        action.setEnabled(True)
        return action
