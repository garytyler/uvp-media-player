import logging
from os.path import basename

from ffmpeg import probe as ffmpeg_probe
from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from ..util import config

log = logging.getLogger(__name__)


class MediaItem(QStandardItem):

    PathRole = Qt.UserRole + 1
    ProbeRole = Qt.UserRole + 3
    SphericalRole = Qt.UserRole + 4

    def __init__(self, path):
        super().__init__()
        probe = ffmpeg_probe(path)

        # Set Qt data role values
        format_tags = probe["format"]["tags"]
        try:
            title = format_tags["title"]
        except KeyError:
            log.warning(f"No 'title' tag found. path={path}, format_tags={format_tags}")
            title = format_tags["title"] = basename(path)
        self.setData(title, Qt.DisplayRole)
        self.setData(title, Qt.WhatsThisRole)
        self.setData(title, Qt.StatusTipRole)

        # Set proprietary data role values
        self.setData(path, MediaItem.PathRole)
        self.setData(probe, MediaItem.ProbeRole)
        self.setData(self.is_spherical(), MediaItem.SphericalRole)

    def is_spherical(self) -> bool:
        probe = self.data(MediaItem.ProbeRole)
        for stream in probe["streams"]:
            if stream.get("side_data_list"):
                return True
        return False


class PlaylistModel(QStandardItemModel):
    rowCountChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(0, len(config.state.meta_tags), parent=parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            media_item = self.item(index.row(), 0)
            probe = media_item.data(MediaItem.ProbeRole)
            key = config.state.meta_tags[index.column()]
            return probe["format"]["tags"].get(key, None)
        elif role == (Qt.ToolTipRole):
            return config.state.meta_tags[index.column()]
        else:
            item = self.item(index.row(), 0)
            return item.data(role)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section + 1
            elif orientation == Qt.Horizontal:
                return config.state.meta_tags[section]

    def setItem(self, row, item):
        """Reimplimentation for signal emissions"""
        result = super().setItem(row, item)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def takeItem(self, row, column=0):
        """Reimplimentation for signal emissions"""
        result = super().takeItem(row, column)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def takeRow(self, row):
        """Reimplimentation for signal emissions"""
        result = super().takeRow(row)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def insertRow(self, row, items):
        """Reimplimentation for signal emissions"""
        result = super().insertRow(row, items)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def appendRow(self, items):
        """Reimplimentation for signal emissions"""
        result = super().appendRow(items)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def removeRow(self, row):
        """Reimplimentation for signal emissions"""
        result = super().removeRow(row)
        self.rowCountChanged.emit(self.rowCount())
        return result

    def insertRows(self, row, count, parent=QModelIndex()):
        """Reimplimentation for signal emissions"""
        first = row
        last = row + count - 1
        self.beginInsertRows(parent, first, last)
        result = super().insertRows(row, count, parent)
        self.endInsertRows()
        self.rowCountChanged.emit(self.rowCount())
        return result

    def removeRows(self, row, count, parent=QModelIndex()):
        """Reimplimentation for signal emissions"""
        first = row
        last = row + count - 1
        self.beginRemoveRows(parent, first, last)
        result = super().removeRows(row, count, parent)
        self.endRemoveRows()
        self.rowCountChanged.emit(self.rowCount())
        return result
