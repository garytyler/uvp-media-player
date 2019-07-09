from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QFileDialog, QWidget

from .. import vlcqt


class MediaController(QObject):
    def __init__(self, media_frame_layout):
        super().__init__()
        self.lp = vlcqt.list_player
        self.mf_layout = media_frame_layout

    def load_media_paths(self, paths: list):
        self.load_media_list(vlcqt.MediaList(paths))

    def load_media_list(self, media_list: vlcqt.MediaList):
        self.mf_layout.clear_media_frame()
        self.lp.stop()
        self.mf_layout.reset_media_frame()
        self.lp.set_media_list(media_list)
        self.media_list = media_list


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
        self.media_ctrlr.load_media(file_paths)
