import logging

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QPushButton

from . import config, icons, util, vlc_objects

log = logging.getLogger(__name__)


class SquareIconButton(QPushButton):
    enterhover = pyqtSignal()
    leavehover = pyqtSignal()

    def __init__(self, parent, icons, size=None):
        super().__init__(parent=parent)
        self.icons = icons
        self.setFlat(True)
        size = size if size else 40
        qsize = QSize(size, size)
        self.setIconSize(qsize)
        self.sizeHint = lambda: qsize
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


class PlaybackModeButton(SquareIconButton):
    setplaybackmode = pyqtSignal(str)

    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.playback_mode_button)
        self.lp = vlc_objects.list_player
        self.option_names = ["off", "one", "all"]
        for index, item in enumerate(self.option_names):
            if item == config.state.playback_mode:
                util.rotate_list(self.option_names, index)
                break

        self.switch_icon(self.option_names[0])

        self.clicked.connect(self.on_clicked)
        self.setplaybackmode.connect(self.lp.on_setplaybackmode)

    def on_clicked(self):
        util.rotate_list(self.option_names, 1)
        option_name = self.option_names[0]
        self.switch_icon(self.option_names[0])
        config.state.playback_mode = option_name
        self.setplaybackmode.emit(option_name)


class PlayPauseButton(SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.play_pause_button)
        self.switch_icon("play")
        self.mp = vlc_objects.media_player
        self.lp = vlc_objects.list_player
        self.setToolTip("Play")

        if self.mp.is_playing():
            self.on_playing()
        else:
            self.on_paused()

        self.mp.playing.connect(self.on_playing)
        self.mp.paused.connect(self.on_paused)
        self.mp.stopped.connect(self.on_paused)

        self.clicked.connect(self.on_clicked)

    @pyqtSlot()
    def on_playing(self):
        self.switch_icon("play")

    @pyqtSlot()
    def on_paused(self):
        self.switch_icon("pause")

    @pyqtSlot()
    def on_clicked(self):
        if self.mp.is_playing():
            # self.lp.pause()
            self.mp.pause()
        else:
            # self.lp.play()
            self.mp.play()


class MainMenuButton(SquareIconButton):
    def __init__(self, parent, main_menu, size=None):
        super().__init__(parent=parent, size=size, icons=icons.main_menu_button)
        self.main_menu = main_menu
        self.curr_icon = icons.main_menu_button
        self.update_icon_hover()
        self.clicked.connect(self.open_menu)

    def open_menu(self):
        menu_size = self.main_menu.sizeHint()
        x = self.pos().x() - menu_size.width()
        y = self.pos().y() - menu_size.height()
        self.main_menu.popup(self.mapToGlobal(QPoint(x, y)))


class VolumeButton(SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.volume_button)
        self.switch_icon("off")
        self.setDisabled(True)
        self.update_icon_hover()


class SkipBackwardButton(SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.skip_backward_button)
        self.curr_icon = self.icons
        self.update_icon_hover()
        pass


class SkipForwardButton(SquareIconButton):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size, icons=icons.skip_forward_button)
        self.curr_icon = self.icons
        self.update_icon_hover()
        pass
