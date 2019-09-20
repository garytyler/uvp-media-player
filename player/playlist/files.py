import logging
import os
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu

from .. import vlcqt
from ..gui import icons

log = logging.getLogger(__name__)


def get_file_paths(paths: list):
    file_paths = []
    for p in paths:
        if os.path.isfile(p):
            file_paths.append(p)
        elif os.path.isdir(p):
            for i in os.scandir(p):
                if i.is_file():
                    file_paths.append(i.path)
        else:
            log.warning(f"Path does not exist: {p}")
    return file_paths


def get_media_object(path: str):
    media = vlcqt.Media(path)
    media.parse()
    iter_tracks = media.tracks_get()
    if not iter_tracks:
        return None
    else:
        return media


def get_media_objects(paths: Union[list, str]):
    if isinstance(paths, str):
        paths = [paths]

    media_objects = []
    for p in get_file_paths(paths):
        obj = get_media_object(p)
        if obj:
            media_objects.append(obj)

    return media_objects


def get_media_paths(paths):
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

    media_paths = []
    for p in file_paths:
        _media = vlcqt.Media(p)
        _media.parse()
        iter_tracks = _media.tracks_get()
        if not iter_tracks:
            continue
        media_paths.append(os.path.abspath(p))
        del _media

    return media_paths


class OpenFileAction(QAction):
    def __init__(self, parent, playlist_widget):
        super().__init__(parent=parent)
        self.parent = parent
        self.playlist_widget = playlist_widget
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
            self.playlist_widget.add_media([file_path])


class OpenMultipleAction(QAction):
    def __init__(self, parent, playlist_widget):
        super().__init__(parent=parent)
        self.parent = parent
        self.playlist_widget = playlist_widget
        self.setIcon(icons.open_multiple)
        self.setText("Open Multiple Files")
        self.setShortcut("Ctrl+M")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_paths, filter_desc = QFileDialog.getOpenFileNames(
            self.parent, self.text(), directory="media"
        )
        if file_paths:
            self.playlist_widget.add_media(file_paths)


class OpenMediaMenu(QMenu):
    def __init__(self, parent, playlist_widget):
        super().__init__(parent=parent)
        self.parent = parent
        self.playlist_widget = playlist_widget
        self.setIcon(icons.open_file_menu)
        self.setTitle("Open Media")
        self.addAction(OpenMultipleAction(parent=self, playlist_widget=playlist_widget))
        self.addAction(OpenFileAction(parent=self, playlist_widget=playlist_widget))
