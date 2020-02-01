import logging

from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QActionGroup, QSlider

from player import config
from player.gui import icons
from player.playlist.model import MediaItem

log = logging.getLogger(__name__)


class LoopModeManager(QObject):
    playbackmodechanged = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.option_names = ["off", "one", "all"]
        for index, item in enumerate(self.option_names):
            if item == config.state.loop_mode:
                self.rotate_list(self.option_names, index)
                break

    @staticmethod
    def rotate_list(l, n):
        l[:] = l[n:] + l[:n]

    def rotate_mode(self):
        self.rotate_list(self.option_names, 1)
        option_name = self.option_names[0]
        self.playbackmodechanged.emit(option_name)
        config.state.loop_mode = option_name

    def get_mode(self):
        return self.option_names[0]


class PlaybackModeAction(QAction):
    def __init__(self, parent, loop_mode_mngr):
        super().__init__(parent=parent)
        self.loop_mode_mngr = loop_mode_mngr

        self.icons = {
            "off": icons.get("loop_mode_off"),
            "one": icons.get("loop_mode_one"),
            "all": icons.get("loop_mode_all"),
        }
        self.setText("Toggle Playback Mode")
        self.setToolTip("Toggle Playback Mode")
        self.setIconText("Playback Mode")
        self.setCheckable(True)

        self.update()
        self.triggered.connect(self.loop_mode_mngr.rotate_mode)
        self.loop_mode_mngr.playbackmodechanged.connect(self.on_playbackmodechanged)

    def on_playbackmodechanged(self, mode: str):
        self.update(mode)

    def update(self, mode: str = None):
        mode = self.loop_mode_mngr.get_mode()
        self.setIcon(self.icons[mode])
        self.setChecked(True if mode != "off" else False)


class PlayActions(QActionGroup):
    def __init__(self, parent, listplayer, media_player):
        super().__init__(parent)
        self.listplayer = listplayer
        self.mp = media_player

        self.prev = PreviousMediaAction(parent=parent, listplayer=listplayer)
        self.play = PlayPauseAction(
            parent=parent, listplayer=listplayer, media_player=media_player
        )
        self.next = NextMediaAction(parent=parent, listplayer=listplayer)
        self.addAction(self.prev)
        self.addAction(self.play)
        self.addAction(self.next)
        self.setEnabled(False)

        listplayer.mediachanged.connect(self.on_mediaplayer_mediachanged)

    def on_mediaplayer_mediachanged(self, e):
        self.setEnabled(self.mp.has_media())


class PlayPauseAction(QAction):
    def __init__(self, parent, listplayer, media_player):
        super().__init__(parent=parent)
        self.listplayer = listplayer
        self.mp = media_player

        self.setToolTip("Play/Pause")
        self.setCheckable(True)
        self.setIcon(icons.get("play_pause"))

        self.mp.playing.connect(self.on_playing)
        self.mp.paused.connect(self.on_paused)
        self.mp.stopped.connect(self.on_paused)
        self.triggered.connect(self.on_triggered)

    @pyqtSlot()
    def on_playing(self):
        self.setChecked(True)

    @pyqtSlot()
    def on_paused(self):
        self.setChecked(False)

    @pyqtSlot(bool)
    def on_triggered(self, checked):
        if self.mp.is_playing():
            self.mp.pause()
        else:
            self.mp.play()
        self.setChecked(checked)


class PreviousMediaAction(QAction):
    def __init__(self, parent, listplayer):
        super().__init__(parent=parent)
        self.listplayer = listplayer

        self.setToolTip("Previous Media")
        self.setIcon(icons.get("previous_media"))

        self.triggered.connect(self.on_triggered)

    @pyqtSlot(bool)
    def on_triggered(self, checked):
        self.listplayer.skip_previous()


class NextMediaAction(QAction):
    def __init__(self, parent, listplayer):
        super().__init__(parent=parent)
        self.setToolTip("Next Media")
        self.setIcon(icons.get("next_media"))
        self.listplayer = listplayer

        self.triggered.connect(self.on_triggered)

    @pyqtSlot(bool)
    def on_triggered(self, checked):
        self.listplayer.skip_next()


class FrameResolutionTimeSlider(QSlider):
    """Basic playback time slider that updates per position change signal from vlc."""

    # slider_precision = 100  # Must match multiplier used by timer

    def __init__(self, parent, listplayer, media_player):
        super().__init__(Qt.Horizontal, parent)
        self.lp = listplayer
        self.mp = media_player
        self.setToolTip("Position")

        self.mp_pos = None
        self.mouse_down = False

        self.lp.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)
        self.mp.stopped.connect(self.on_stopped)
        self.mp.playing.connect(self.on_playing)
        self.newframe_conn = self.lp.newframe.connect(self.on_newframe)

    @pyqtSlot(MediaItem)
    def on_mediachanged(self, media_item: MediaItem):
        self.conform_to_media(media_item)

    @pyqtSlot()
    def on_stopped(self):
        self.setValue(0)

    @pyqtSlot()
    def on_playing(self):
        self.curr_pos = self.mp.get_position()
        self.mouse_down = False

    @pyqtSlot()
    def on_positionchanged(self):
        pos = self.mp.get_position()
        if pos and pos > 0:
            self.mp_pos = pos * self.length
        self.mouse_down = False

    @pyqtSlot()
    def on_newframe(self):
        if self.mp_pos and self.mp_pos <= 0:
            self.curr_pos = self.mp_pos
        elif self.mp_pos and self.mp_pos > 0:
            self.curr_pos = self.mp_pos
            self.mp_pos = None
        else:
            num_frames = self.media_info["nb_frames"]
            has_b_frames = self.media_info["has_b_frames"]
            pos_incr = self.length / num_frames + has_b_frames
            self.curr_pos = self.curr_pos + pos_incr
        self.setValue(self.curr_pos)

    def conform_to_media(self, media_item):
        self.media_info = media_item.info()
        # self.set_length(self.media_info['nb_frames'])
        self.set_length(100000)

    def setValue(self, value):
        if self.mouse_down:
            return
        super().setValue(value)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mouse_down = True
        self.mp.positionchanged.disconnect()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        super().setValue(as_slider_val)
        self.mp_pos = as_proportion

    def mouseMoveEvent(self, e):
        e.accept()
        as_proportion, as_slider_val = self.get_mouse_pos(e)
        self.mp.set_position(as_proportion)
        self.mp_pos = as_proportion
        super().setValue(as_slider_val)

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(self, e)
        e.accept()
        self.mp.positionchanged.connect(self.on_positionchanged)

    def set_length(self, value):
        self.setMinimum(0)
        self.setMaximum(min((value, 2147483647)))
        self.length = self.maximum() - self.minimum()

    def get_mouse_pos(self, e):
        slider_min, slider_max = self.minimum(), self.maximum()
        slider_range = slider_max - slider_min
        pos_as_proportion = e.pos().x() / self.width()
        pos_as_slider_val = slider_range * pos_as_proportion + slider_min
        return pos_as_proportion, pos_as_slider_val
