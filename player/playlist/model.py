import logging

from ffmpeg import probe
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from ..util import config

log = logging.getLogger(__name__)


class MediaItem(QStandardItem):

    PathRole = Qt.UserRole + 1
    ProbeRole = Qt.UserRole + 3
    SphericalRole = Qt.UserRole + 4

    def __init__(self, path):
        super().__init__()
        _probe = probe(path)
        self.setData(path, MediaItem.PathRole)
        self.setData(_probe, MediaItem.ProbeRole)
        self.setData(self.is_spherical(), MediaItem.SphericalRole)

        _title = _probe["format"]["tags"]["title"]
        self.setData(_title, Qt.DisplayRole)
        self.setData(_title, Qt.ToolTipRole)
        self.setData(_title, Qt.WhatsThisRole)
        self.setData(_title, Qt.StatusTipRole)

    def is_spherical(self) -> bool:
        probe = self.data(MediaItem.ProbeRole)
        for stream in probe["streams"]:
            if stream.get("side_data_list"):
                return True
        return False


class PlaylistModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(0, len(config.state.meta_tags), parent=parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.DisplayRole:
            media_item = self.item(index.row(), 0)
            probe = media_item.data(MediaItem.ProbeRole)
            key = config.state.meta_tags[index.column()]
            return probe["format"]["tags"].get(key, None)
        else:
            item = self.item(index.row(), 0)
            return item.data(role)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section + 1
            elif orientation == Qt.Horizontal:
                return config.state.meta_tags[section]
