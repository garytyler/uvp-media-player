from . import image  # noqa:F401
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from player import gui


class PopupWindowWidget(QtWidgets.QWidget):
    hiddenchanged = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

    def showEvent(self, e):
        is_always_on_top = gui.ontop.get_always_on_top(self.main_win)
        gui.ontop.set_always_on_top(self, is_always_on_top)

        self.raise_()
        self.hiddenchanged.emit(True)

    def hideEvent(self, e):
        self.hiddenchanged.emit(False)

    def closeEvent(self, e):
        self.hide()
        e.ignore()


class PopupWindowAction(QtWidgets.QAction):
    def __init__(self, icon, text, widget: PopupWindowWidget, main_win):
        super().__init__(icon, text)
        self.main_win = main_win
        self.widget = widget
        self.widget_pos = None
        self.setCheckable(True)
        self.setChecked(False)
        self.triggered.connect(self.on_triggered)
        self.widget.hiddenchanged.connect(self.on_win_hiddenchanged)

    def on_triggered(self, checked):
        if checked:
            self.widget.show()
            if self.widget_pos:
                self.widget.move(self.widget_pos)
            self.widget.raise_()
        else:
            self.widget.hide()

    @QtCore.pyqtSlot(bool)
    def on_win_hiddenchanged(self, checked):
        self.setChecked(checked)


class MediaPlayerAdjustmentsWindow(PopupWindowWidget):
    def __init__(self, main_win, media_player, parent):
        super().__init__(parent)
        self.main_win = main_win
        self.setWindowTitle("Media Player Adjustments")
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(
            image.ImageEffectsWidget(parent=self, media_player=media_player)
        )


class OpenMediaPlayerAdjustmentsWindowAction(PopupWindowAction):
    def __init__(self, main_win, media_player):
        super().__init__(
            icon=gui.icons.get("open_media_player_adjustments"),
            text="Media Player Adjustments",
            widget=MediaPlayerAdjustmentsWindow(
                main_win=main_win, media_player=media_player, parent=main_win
            ),
            main_win=main_win,
        )
