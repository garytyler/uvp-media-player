import logging
from os import path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QAction, QHeaderView, QMenu, QTreeView, QVBoxLayout

from ..base.docking import DockableWidget
from ..base.popup import PopupWindowAction, PopupWindowWidget
from ..gui import icons
from . import files
from .model import MediaItem, PlaylistModel

log = logging.getLogger(__name__)


class Header(QHeaderView):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.get_context_menu)
        self.sectionCountChanged.connect(self.on_sectionCountChanged)

    def on_sectionCountChanged(self, oldCount, newCount):
        if oldCount == newCount:
            return None

        self.actions = []
        for index in range(newCount):
            name = self.model().headerData(index, Qt.Horizontal, Qt.DisplayRole)
            action = QAction(name, self)
            # Store section_index for retreival on trigger
            action.setData(index)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self.toggle_section)
            self.actions.append(action)

        log.info(f"sectionCountChanged oldCount={oldCount}, newCount={newCount}")

    @pyqtSlot(bool)
    def toggle_section(self, hide: bool):
        action: QAction = self.sender()
        logical_index: int = action.data()
        self.setSectionHidden(logical_index, not hide)

    def get_context_menu(self, point):
        menu = QMenu(self)
        self.currentSection = self.logicalIndexAt(point)
        for action in self.actions:
            menu.addAction(action)
        menu.exec_(self.mapToGlobal(point))


class PlaylistView(QTreeView):
    def __init__(self, playlist_player, play_ctrls, parent):
        super().__init__(parent=parent)
        self.pl_player = playlist_player
        self.play_ctrls = play_ctrls

        self.setSelectionBehavior(self.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)
        self.setExpandsOnDoubleClick(False)
        self.setRootIsDecorated(False)

        self._header = Header(parent=self)
        self.setHeader(self._header)

        self.doubleClicked.connect(self.on_doubleClicked)

    def on_doubleClicked(self, index):
        self.pl_player.load_media(index=index)

    def on_model_dataChanged(self, topLeft, bottomRight):
        """Enable/disable playback controls according to contents"""
        self.play_ctrls.setEnabled(bool(self.model().item(0)))

    def add_media(self, paths):
        paths = files.get_media_paths(paths)
        if not paths:
            return None

        items = []
        for p in paths:
            item = MediaItem(path.abspath(p))
            items.append(item)

        if not items:
            return None

        if not self.model():
            self.setModel(PlaylistModel(parent=self))

        for i in items:
            self.model().appendRow(i)

        first_item = self.model().item(0)
        if first_item:
            self.pl_player.load_media(index=first_item.index(), play=False)


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
