import logging
from os.path import exists

from ffmpeg import probe
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from .. import vlcqt

log = logging.getLogger(__name__)


Qt.VlcMedia = Qt.UserRole + 1
Qt.IsSpherical = Qt.UserRole + 2

META_TAG_KEYS = [
    "title",
    "artist",
    "genre",
    "album",
    "duration",
    "track_number",
    "description",
    "url",
    "id",
    "rating",
    "cover",
    "disc_number",
    "date",
]


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
        super().__init__(0, len(META_TAG_KEYS), parent=parent)
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
                return META_TAG_KEYS[section]

    def data(self, index, role):
        item = self.item(index.row())
        if not item:
            return None
        elif role == Qt.DisplayRole:
            header_key = META_TAG_KEYS[index.column()]
            return item.probe["format"]["tags"].get(header_key)
        elif role >= Qt.UserRole:
            return item.data(role)
