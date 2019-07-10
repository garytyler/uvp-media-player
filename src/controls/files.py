from PyQt5.QtCore import QObject, QSize, Qt
from PyQt5.QtWidgets import QAction, QFileDialog, QToolButton

from .. import vlcqt
from ..gui import icons


class FileLoader(QObject):
    def __init__(self, content_frame_layout, frame_size_ctrlr):
        super().__init__()
        self.content_frame_layout = content_frame_layout
        self.frame_size_ctrlr = frame_size_ctrlr
        self.lp = vlcqt.list_player
        self.mp = vlcqt.media_player

    def load_media_paths(self, paths: list):
        self.media_list = vlcqt.MediaList(paths)
        self.load_media_list(self.media_list)

    def load_media_list(self, media_list: vlcqt.MediaList):
        self.media_list = media_list
        self.content_frame_layout.clear_content_frame()
        self.lp.stop()
        self.lp.set_media_list(media_list)
        self.content_frame_layout.reset_content_frame()
        self.lp.stop()
        first_list_item = self.media_list.item_at_index(0)
        self.frame_size_ctrlr.conform_to_media(first_list_item)


class OpenFileAction(QAction):
    def __init__(self, parent, media_loader):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_loader = media_loader
        self.setIcon(icons.open_file)
        self.setText("Open file")
        self.setShortcut("Ctrl+O")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(
            self.parent, self.text(), directory="media"
        )
        if file_path:
            self.media_loader.load_media_paths([file_path])


class OpenMultipleAction(QAction):
    def __init__(self, parent, media_loader):
        super().__init__(parent=parent)
        self.parent = parent
        self.media_loader = media_loader
        self.setIcon(icons.open_multiple)
        self.setText("Open multiple files")
        self.setShortcut("Ctrl+M")
        self.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.setShortcutVisibleInContextMenu(True)

        self.triggered.connect(self.on_triggered)

    def on_triggered(self):
        file_paths, filter_desc = QFileDialog.getOpenFileNames(
            self.parent, self.text(), directory="media"
        )
        if file_paths:
            self.media_loader.load_media_paths(file_paths)


class OpenFileButton(QToolButton):
    def __init__(self, parent, size, action: OpenFileAction):
        super().__init__(parent=parent)
        self.action = action

        self.setToolTip("")
        self.setCheckable(False)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.setDefaultAction(self.action)


class OpenMultipleButton(QToolButton):
    def __init__(self, parent, size, action: OpenMultipleAction):
        super().__init__(parent=parent)
        self.action = action

        self.setToolTip("")
        self.setCheckable(False)
        self.setIconSize(QSize(size, size))
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.setDefaultAction(self.action)
