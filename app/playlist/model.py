import logging
from os.path import basename

import config
from ffmpeg import probe as ffmpeg_probe
from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from utils import fraction_string_to_float

log = logging.getLogger(__name__)


class MediaItem(QStandardItem):

    PathRole = Qt.UserRole + 1
    ProbeRole = Qt.UserRole + 3
    SphericalRole = Qt.UserRole + 4

    def __str__(self):
        return self.title()

    def __init__(self, path: str, ffprobe_cmd: str):
        super().__init__()
        # Check probe values
        probe = ffmpeg_probe(path, cmd=ffprobe_cmd)
        try:
            title = probe["format"]["tags"]["title"]
        except KeyError:
            title = probe["format"]["tags"]["title"] = basename(path)

        # Set proprietary data role values
        self.setData(path, MediaItem.PathRole)
        self.setData(probe, MediaItem.ProbeRole)

        # Set Qt data role values
        self.setData(title, Qt.DisplayRole)
        self.setData(title, Qt.WhatsThisRole)
        self.setData(title, Qt.StatusTipRole)

    def title(self):
        return self.probe()["format"]["tags"]["title"]

    def path(self):
        return self.data(MediaItem.PathRole)

    def probe(self):
        return self.data(MediaItem.ProbeRole)

    def size(self):
        probe = self.probe()
        stream = next((i for i in probe["streams"] if i["codec_type"] == "video"), None)
        width = int(stream["width"])
        height = int(stream["height"])
        return width, height

    def info(self):
        probe = self.probe()
        stream = next((i for i in probe["streams"] if i["codec_type"] == "video"), None)
        return {
            "width": int(stream["width"]),
            "height": int(stream["height"]),
            "nb_frames": int(stream["nb_frames"]),
            "has_b_frames": int(stream["has_b_frames"]),
            "avg_frame_rate": fraction_string_to_float(stream["avg_frame_rate"]),
            "r_frame_rate": fraction_string_to_float(stream["r_frame_rate"]),
            "duration": float(stream["duration"]),
            "duration_ts": float(stream["duration_ts"]),  # duration time scale
            "time_base": fraction_string_to_float(stream["time_base"]),
        }

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
            key = config.state.meta_tags[index.column()]  # type: ignore
            return probe["format"]["tags"].get(key, None)
        elif role == (Qt.ToolTipRole):
            return config.state.meta_tags[index.column()]  # type: ignore
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
        last = row + count if row == 0 else row + count - 1
        self.beginInsertRows(parent, first, last)
        result = super().insertRows(row, count, parent)
        self.endInsertRows()
        self.rowCountChanged.emit(self.rowCount())
        return result

    def removeRows(self, row, count, parent=QModelIndex()):
        """Reimplimentation for signal emissions"""
        first = row
        last = row + count if row == 0 else row + count - 1
        self.beginRemoveRows(parent, first, last)
        result = super().removeRows(row, count, parent)
        self.endRemoveRows()
        self.rowCountChanged.emit(self.rowCount())
        return result
