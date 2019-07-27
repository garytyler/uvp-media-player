import logging
from pprint import pprint

from ffmpeg import probe
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from .. import vlcqt

log = logging.getLogger(__name__)


Qt.VlcMedia = Qt.UserRole + 1
Qt.IsSpherical = Qt.UserRole + 2


class MediaItem(QStandardItem):
    meta_enum_names = vlcqt.Meta._enum_names_

    def __init__(self, path):
        super().__init__()

        self.setEditable(False)
        self.setDragEnabled(True)

        self.meta = {"vlc": {}, "ffmpeg": probe(path)}

        for enum in sorted(self.meta_enum_names.keys()):
            self.setChild(enum, 0, QStandardItem())

        self._media = vlcqt.Media(path)
        self.update_vlc_meta()

        self.get_media().mediaparsedchanged.connect(self.update_vlc_meta)
        self.get_media().parse_with_options(vlcqt.MediaParseFlag.local, timeout=2)

        self.meta = {"vlc": {}, "ffmpeg": probe(path)}

    def get_media(self):
        return self._media

    def update_vlc_meta(self):
        media = self.get_media()
        for enum, name in sorted(self.meta_enum_names.items()):
            meta = media.get_meta(enum)
            child = self.child(enum, 0)
            child.setData(meta, role=Qt.DisplayRole)
            child.setData(name, role=Qt.WhatsThisRole)
            child.setData(name, role=Qt.ToolTipRole)
        self.emitDataChanged()

    def data(self, role):
        if role == Qt.DisplayRole:
            return self.get_media().get_meta(0)
        elif role == Qt.UserRole:
            return self
        elif role == Qt.VlcMedia:
            return self.get_media()
        elif role == Qt.IsSpherical:
            return self.is_spherical()

    def is_spherical(self):
        streams = self.meta["ffmpeg"]["streams"]
        for stream in streams:
            if stream.get("side_data_list"):
                return True


class PlaylistModel(QStandardItemModel):
    """Read-Only"""

    def __init__(self, media_items=[], parent=None):
        super().__init__(0, len(MediaItem.meta_enum_names), parent=parent)
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
                return MediaItem.meta_enum_names[section]

    def data(self, index, role):
        item = self.item(index.row())
        if not item:
            return None
        elif role == Qt.DisplayRole:
            child = item.child(index.column())
            if child:
                return child.data(role)
        elif role >= Qt.UserRole:
            return item.data(role)
