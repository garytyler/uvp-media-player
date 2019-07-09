from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QFileDialog, QWidget

from .. import vlcqt


class MediaController(QObject):
    def __init__(self, media_frame_layout, frame_size_ctrlr):
        super().__init__()
        self.mf_layout = media_frame_layout
        self.frame_size_ctrlr = frame_size_ctrlr
        self.lp = vlcqt.list_player
        self.mp = vlcqt.media_player

    def load_media_paths(self, paths: list):
        self.media_list = vlcqt.MediaList(paths)
        self.load_media_list(self.media_list)

    def load_media_list(self, media_list: vlcqt.MediaList):
        self.media_list = media_list

        self.mf_layout.clear_media_frame()
        self.lp.stop()
        self.lp.set_media_list(media_list)
        self.mf_layout.reset_media_frame()

        self.frame_size_ctrlr.conform_to_media(self.media_list.item_at_index(0))


class OpenFileAction(QAction):
    def __init__(self, parent, media_ctrlr):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_ctrlr = media_ctrlr
        self.setText("Open file")
        self.setShortcut("Ctrl+O")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(
            self.parent, self.text(), directory="media"
        )
        self.media_ctrlr.load_media_paths([file_path])


class OpenMultipleFilesAction(QAction):
    def __init__(self, parent, media_ctrlr):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_ctrlr = media_ctrlr
        self.setText("Open multiple files")
        self.setShortcut("Ctrl+M")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_paths, filter_desc = QFileDialog.getOpenFileNames(
            self.parent, self.text(), directory="media"
        )
        self.media_ctrlr.load_media_paths(file_paths)
