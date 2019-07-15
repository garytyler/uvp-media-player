import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from . import files
from .. import vlcqt

log = logging.getLogger(__name__)


class MediaMetaItem(QStandardItem):
    enum_names = vlcqt.Meta._enum_names_

    def __init__(self, media, enum, parent):
        super().__init__(parent)
        self.media = media
        self.enum = enum
        self.desc = self.enum_names[self.enum]
        self.type = lambda: self.UserType + 2
        self.setEditable(False)
        self.setWhatsThis(self.desc)
        self.update_display_data()
        self.media.mediaparsedchanged.connect(self.update_display_data)

    def update_display_data(self):
        data = self.media.get_meta(self.enum)
        self.setData(data, Qt.DisplayRole)
        self.setWhatsThis(self.desc)
        log.debug(f"UPDATE META DISP desc={self.desc}, data={data}")


class MediaItem(QStandardItem):
    def __init__(self, media):
        super().__init__()
        self.media = media
        self.type = lambda: self.UserType + 1
        self.setEditable(False)
        self.setDragEnabled(True)
        self.setData(self.media, Qt.UserRole)

        for enum in sorted(MediaMetaItem.enum_names.keys()):
            self.setChild(enum, MediaMetaItem(media, enum, parent=self))

        self.media.parse_with_options(vlcqt.MediaParseFlag.local, timeout=2)


class PlaylistModel(QStandardItemModel):
    """Read-Only"""

    def __init__(self, media_items=None, parent=None):
        super().__init__(parent=parent)
        for i in media_items:
            self.appendRow(i)

        self.setColumnCount(len(MediaMetaItem.enum_names))

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            elif orientation == Qt.Horizontal:
                return MediaMetaItem.enum_names[section]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media_item = self.item(index.row())
            meta_item = media_item.child(index.column())
            return meta_item.data(role)
        elif role == Qt.UserRole:
            media_item = self.item(index.row())
            return media_item.data(role)
