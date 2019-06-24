from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QAction, QPushButton


class OpenMenuAction(QAction):
    def __init__(self, icon, text, menu, button):
        super().__init__(icon, text, parent=button)
        self.button = button
        self.menu = menu
        self.triggered.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.button.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.button.mapToGlobal(QPoint(x, y)))


class IconButton(QPushButton):
    enterhover = pyqtSignal()
    leavehover = pyqtSignal()

    def __init__(self, parent, icons, size=None):
        super().__init__(parent=parent)
        self.icons = icons
        self.setFlat(True)

        size = size if size else 40
        self.qsize = QSize(size, size)
        self.setIconSize(self.qsize)

        self.installEventFilter(self)
        self.hovering = False

        self.enterhover.connect(self.on_enterhover)
        self.leavehover.connect(self.on_leavehover)

    def on_enterhover(self):
        self.hovering = True
        self.update_icon_hover()

    def on_leavehover(self):
        self.hovering = False
        self.update_icon_hover()

    def switch_icon(self, name):
        self.curr_icon = self.icons[name]
        self.update_icon_hover()

    def update_icon_hover(self):
        if self.hovering:
            self.setIcon(self.curr_icon["hovered"])
        else:
            self.setIcon(self.curr_icon["normal"])

    def eventFilter(self, src, e):
        _type = e.type()
        if _type == QEvent.Enter and src == self:
            self.enterhover.emit()
        elif _type == QEvent.Leave and src == self:
            self.leavehover.emit()
        elif _type == QMouseEvent.MouseButtonDblClick:
            if src == self and e.button() == Qt.LeftButton:
                return True
        elif _type == QMouseEvent.MouseButtonPress:
            if src == self and e.button() == Qt.LeftButton:
                return True
        elif _type == QMouseEvent.MouseButtonRelease:
            if src == self and e.button() == Qt.LeftButton:
                self.clicked.emit()
        return False


class SquareIconButton(IconButton):
    def __init__(self, parent, size=None, icons=None):
        super().__init__(parent, icons)
        size = size if size else 40
        qsize = QSize(size, size)
        self.setIconSize(qsize)
        self.sizeHint = lambda: qsize


class SquareMenuButton(SquareIconButton):
    def __init__(self, parent, menu, size=None, icons=None):
        super().__init__(parent=parent, size=size, icons=icons)
        self.size = size
        self.menu = menu

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.mapToGlobal(QPoint(x, y)))


class MenuButton(IconButton):
    def __init__(self, parent, menu, icons=None):
        super().__init__(parent=parent, icons=icons)

        self.menu = menu

    def open_menu(self):
        menu_size = self.menu.sizeHint()
        butt_rect = self.rect()
        x = butt_rect.x()
        y = butt_rect.y() - menu_size.height()
        self.menu.popup(self.mapToGlobal(QPoint(x, y)))
