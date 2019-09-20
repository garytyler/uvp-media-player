import logging

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QPoint, Qt, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QHeaderView,
    QMenu,
    QShortcut,
    QTableView,
    QVBoxLayout,
    QWidget,
)

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
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.sectionCountChanged.connect(self.on_sectionCountChanged)

    def on_sectionCountChanged(self, oldCount, newCount):
        if oldCount == newCount:
            return None

        self.actions = []
        for index in range(newCount):
            name = self.model().headerData(index, Qt.Horizontal, Qt.DisplayRole)
            action = QAction(str(name), self)
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

    def show_context_menu(self, point):
        menu = QMenu(self)
        self.currentSection = self.logicalIndexAt(point)
        for action in self.actions:
            menu.addAction(action)
        menu.exec_(self.mapToGlobal(point))


class PlaylistView(QTableView):
    def __init__(self, parent, playlist_player, play_ctrls=None):
        super().__init__(parent=parent)
        self.playlist_player = playlist_player
        self.play_ctrls = play_ctrls
        self.create_actions()
        self.create_shortcuts()

        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setDropIndicatorShown(True)
        self._header = Header(parent=self)
        self.setHorizontalHeader(self._header)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.on_doubleClicked)

    def mousePressEvent(self, e):
        """Clear both row and current index selections when clicking away from items."""
        if self.currentIndex().isValid():
            self.selectionModel().clear()
        super().mousePressEvent(e)

    @pyqtSlot(QModelIndex)
    def on_doubleClicked(self, index):
        self.playlist_player.load_media(index=index, play=True)

    def dropEvent(self, e):
        dragged_index = self.currentIndex()
        dropped_index = self.indexAt(e.pos())

        log.debug(
            f"dragged_index={dragged_index.row(), dragged_index.column()} dropped_index={dropped_index.row(), dropped_index.column()} action={e.dropAction()} source={e.source()}"
        )

        if dropped_index.row() == -1:
            return None

        model = self.model()
        item = model.takeRow(dragged_index.row())
        model.insertRow(dropped_index.row(), item)
        self.setCurrentIndex(dropped_index)
        e.ignore()

    def on_model_dataChanged(self, topLeft, bottomRight, roles: list = None):
        """Enable/disable playback controls according to contents"""
        self.play_ctrls.setEnabled(bool(self.model().item(0)))

    def setModel(self, model):
        # Disconnect old model
        old_model = self.model()
        if old_model:
            old_model.dataChanged.disconnect(self.on_model_dataChanged)
        # Connect new model
        super().setModel(model)
        self.model().dataChanged.connect(self.on_model_dataChanged)
        self.setSelectionModel(QItemSelectionModel(model=self.model()))

    def create_actions(self):
        self.rem_curr_row_action = RemoveCurrentRowAction(parent=self)

    def create_shortcuts(self):
        """Create shortcuts for manipulating items when this widget is selected.

        - Use QShortcut instances with context 'Qt.WidgetWithChildrenShortcut'
        """
        self.rem_item_shortcut = QShortcut(self)
        self.rem_item_shortcut.setKey(QKeySequence.Delete)
        self.rem_item_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.rem_item_shortcut.activated.connect(self.rem_curr_row_action.trigger)

    def show_context_menu(self, pos: QPoint):
        # Get title of targeted item to use in context menu item text strings
        curr_index = self.currentIndex().siblingAtColumn(0)
        item_title = curr_index.data(Qt.DisplayRole)

        # Create context menu object
        menu = QMenu(self)

        # Create context menu actions
        remove_item_menu_action = menu.addAction(
            icons.file_remove,
            f"Remove '{item_title}'",
            self.rem_curr_row_action.trigger,
        )

        # Add shortcut labels as reference. Key presses will not reach this menu.
        remove_item_menu_action.setShortcut(self.rem_item_shortcut.key())
        menu.exec_(self.mapToGlobal(pos))

        return menu


class RemoveCurrentRowAction(QAction):
    def __init__(self, parent: QAbstractItemView):
        super().__init__(parent)
        self.setIcon(icons.file_remove)
        self.triggered.connect(self.on_triggered)
        self.setText("Remove")

    def on_triggered(self):
        curr_index = self.parent().currentIndex().siblingAtColumn(0)
        item_title = curr_index.data(role=Qt.DisplayRole)
        self.parent().model().removeRow(curr_index.row())
        self.setStatusTip(f"Removed '{item_title}' from playlist")


class PlaylistWidget(QWidget):
    def __init__(self, playlist_player, play_ctrls, parent):
        super().__init__(parent=parent)
        self.playlist_player = playlist_player
        self.play_ctrls = play_ctrls

        self.view = PlaylistView(
            playlist_player=self.playlist_player,
            play_ctrls=self.play_ctrls,
            parent=parent,
        )

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.view)

    def add_media(self, paths):
        paths = files.get_media_paths(paths)
        if not paths:
            log.error(f"No media paths found in {paths}")
            return None

        if not self.view.model():
            self.view.setModel(PlaylistModel(parent=self))

        model = self.view.model()
        for path in paths:
            item = MediaItem(path)
            model.appendRow(item)

        first_item = self.view.model().item(0)
        if first_item:
            self.playlist_player.load_media(index=first_item.index(), play=False)


class DockablePlaylist(DockableWidget):
    def __init__(self, parent, playlist_widget):
        super().__init__(title="Playlist", parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWidget(playlist_widget)
        self.setVisible(False)

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setIcon(icons.open_playlist)
        action.setEnabled(True)
        return action


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
        self, parent, split_view, playlist_widget, frame_size_mngr, main_content_frame
    ):
        super().__init__(parent=parent)
        self.parent = parent
        self.split_view = split_view
        self.playlist_widget = playlist_widget
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
