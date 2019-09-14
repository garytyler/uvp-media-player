import logging

from ffmpeg import probe
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from .. import vlcqt
from ..util import config

log = logging.getLogger(__name__)


Qt.VlcMedia = Qt.UserRole + 1
Qt.IsSpherical = Qt.UserRole + 2


class MediaItem(QStandardItem):
    meta_enum_names = vlcqt.Meta._enum_names_

    def __init__(self, path):
        super().__init__()
        self._path = path

        self.setDragEnabled(True)

        self._media = vlcqt.Media(path)
        self.probe = probe(path)

    def data(self, role):
        if role == Qt.DisplayRole:
            return self.probe["format"]["tags"]["title"]
        elif role == Qt.VlcMedia:
            return self._media
        elif role == Qt.IsSpherical:
            return self.is_spherical()

    def is_spherical(self) -> bool:
        for stream in self.probe["streams"]:
            if stream.get("side_data_list"):
                return True
        return False


class PlaylistModel(QStandardItemModel):
    """Read-Only"""

    def __init__(self, media_items=[], parent=None):
        super().__init__(0, len(config.state.meta_tags), parent=parent)
        for i in media_items:
            self.appendRow(i)

    def add_media_items(self, items):
        for i in items:
            self.appendRow(i)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            elif orientation == Qt.Horizontal:
                return config.state.meta_tags[section].title()

    def data(self, index, role):
        item = self.item(index.row())
        if not item:
            return None
        elif role == Qt.DisplayRole:
            header_key = config.state.meta_tags[index.column()]
            return item.probe["format"]["tags"].get(header_key)
        elif role >= Qt.UserRole:
            return item.data(role)
