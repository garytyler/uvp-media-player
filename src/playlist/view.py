import logging

from PyQt5.QtWidgets import QTableView

from . import files
from .model import PlaylistModel

log = logging.getLogger(__name__)


class PlaylistView(QTableView):
    def __init__(self, playlist_player, parent):
        super().__init__(parent=parent)
        self.pl_player = playlist_player

        self.setSelectionBehavior(self.SelectRows)
        self.doubleClicked.connect(self.on_doubleClicked)

    def setModel(self, model):
        super().setModel(model)
        index = model.index(0, 0)
        if index.isValid():
            self.pl_player.load_media(index=index)

    def on_doubleClicked(self, index):
        self.pl_player.load_media(index=index)

    def add_media(self, paths):
        items = files.get_media_items(paths)
        if not items:
            return None
        model = self.model()
        if model:
            for i in items:
                model.appendRow(i)
        else:
            self.setModel(PlaylistModel(media_items=items))
