import logging
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog

from .. import vlcqt
from ..gui import icons
from .model import MediaItem

log = logging.getLogger(__name__)


def get_media_items(paths):
    if isinstance(paths, str):
        paths = [paths]

    file_paths = []
    for p in paths:
        if not os.path.exists(p):
            log.error(f"PATH NOT FOUND path={p}")
        if os.path.isfile(p):
            file_paths.append(p)
            continue
        for i in os.scandir(p):
            if i.is_file():
                file_paths.append(i.path)

    media_items = []
    for p in file_paths:
        media = vlcqt.Media(p)
        media.parse()
        iter_tracks = media.tracks_get()
        if not iter_tracks:
            continue
        media_items.append(MediaItem(media))

    return media_items


class OpenFileAction(QAction):
    def __init__(self, parent, playlist_view):
        super().__init__(parent=parent)
        self.parent = parent
        self.playlist_view = playlist_view
        self.setIcon(icons.open_file)
        self.setText("Open file")
        self.setShortcut("Ctrl+O")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(
            self.parent, self.text(), directory="media"
        )
        if file_path:
            self.playlist_view.add_media([file_path])


class OpenMultipleAction(QAction):
    def __init__(self, parent, playlist_view):
        super().__init__(parent=parent)
        self.parent = parent
        self.playlist_view = playlist_view
        self.setIcon(icons.open_multiple)
        self.setText("Open multiple files")
        self.setShortcut("Ctrl+M")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_paths, filter_desc = QFileDialog.getOpenFileNames(
            self.parent, self.text(), directory="media"
        )
        if file_paths:
            self.playlist_view.add_media(file_paths)
