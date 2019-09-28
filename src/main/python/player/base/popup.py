from PyQt5.QtCore import QPoint, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QFrame, QWidget

from ..gui import ontop


class PopupControlWidget(QFrame):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.setObjectName("popupcontrolwin")
        self.setFrameShape(QFrame.Box)
        self.setWindowFlags(self.windowFlags() | Qt.Popup)

    def popup(self):
        self.show()
        menu_size = self.size()
        butt_rect = self.parent.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.move(self.parent.mapToGlobal(QPoint(x, y)))


class PopupWindowWidget(QWidget):
    hiddenchanged = pyqtSignal(bool)

    def __init__(self, parent, widget=None):
        super().__init__(parent=None)
        self.parent = parent
        self.position = None
        self.setWindowFlags(self.windowFlags() | Qt.Window)

    def showEvent(self, e):
        if self.position:
            self.move(self.position)

        is_always_on_top = window.get_always_on_top(self.main_win)
        window.set_always_on_top(self, is_always_on_top)

        self.raise_()
        self.hiddenchanged.emit(True)

    def hideEvent(self, e):
        self.position = self.pos()
        self.hiddenchanged.emit(False)

    def closeEvent(self, e):
        self.position = self.pos()
        self.hide()
        e.ignore()


class PopupWindowAction(QAction):
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

    @pyqtSlot(bool)
    def on_win_hiddenchanged(self, checked):
        self.setChecked(checked)


class PopupMenuAction(QAction):
    def __init__(self, icon, text, menu, parent):
        super().__init__(icon, text)
        self.parent = parent
        self.menu = menu
        self.triggered.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.parent.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.parent.mapToGlobal(QPoint(x, y)))
