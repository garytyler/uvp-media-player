import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QTableView, QVBoxLayout, QWidget

from .. import vlcqt


def get_media_file_paths(paths):
    results = []

    def add_files_from_dir(path):
        for i in os.scandir(path):
            if i.is_file():
                results.append(i.path)

    def add_results_from_path(paths):
        for p in paths:
            if os.path.isfile(p):
                results.append(p)
            elif os.path.isdir(p):
                add_files_from_dir(p)

    if isinstance(paths, str):
        paths = [paths]
    add_results_from_path(paths)
    return results


class MediaMetaItem(QStandardItem):
    enum_names = vlcqt.Meta._enum_names_

    def __init__(self, media, enum, parent=None):
        super().__init__(parent)
        self.media = media
        self.enum = enum
        self.update_data()
        self.media.mediaparsedchanged.connect(self.update_data)

    def update_data(self):
        data = self.media.get_meta(self.enum)
        self.setData(data, Qt.DisplayRole)


class MediaListModel(QStandardItemModel):
    def __init__(self, paths=None, parent=None):
        super().__init__(parent=parent)
        file_paths = get_media_file_paths(paths)

        self.media_items = []
        for p in file_paths:
            media = vlcqt.Media(p)
            self.media_items.append(media)
            self.add_meta_items(media=media)

        self.setColumnCount(len(MediaMetaItem.enum_names))

    def add_meta_items(self, media):
        enums = MediaMetaItem.enum_names.keys()
        row = (MediaMetaItem(media, n) for n in enums)
        self.appendRow(row)
        media.parse_with_options(vlcqt.MediaParseFlag.local, timeout=5)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            elif orientation == Qt.Horizontal:
                return MediaMetaItem.enum_names[section]


class MediaListView(QTableView):
    def __init__(self):
        super().__init__()
        pass


class PlaylistWidget(QWidget):
    def __init__(self, paths):
        super().__init__()
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.view = MediaListView()
        self.layout().addWidget(self.view)

        self.load_playlist(paths)

    def load_playlist(self, paths):
        self.model = MediaListModel(paths=paths, parent=self.view)
        self.view.setModel(self.model)
