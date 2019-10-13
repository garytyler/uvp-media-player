import logging

import vlc
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QActionGroup, QSlider

import vlcqt
from gui import icons
from util import config

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
    def __init__(self, parent, listplayer):
        super().__init__(parent)
        self.listplayer = listplayer
        self.mp = vlcqt.media_player

        self.prev = PreviousMediaAction(parent=parent, listplayer=listplayer)
        self.play = PlayPauseAction(parent=parent, listplayer=listplayer)
        self.next = NextMediaAction(parent=parent, listplayer=listplayer)
        self.addAction(self.prev)
        self.addAction(self.play)
        self.addAction(self.next)
        self.setEnabled(False)

        listplayer.mediachanged.connect(self.on_mediaplayer_mediachanged)

    def on_mediaplayer_mediachanged(self, e):
        self.setEnabled(self.mp.has_media())


class PlayPauseAction(QAction):
    def __init__(self, parent, listplayer):
        super().__init__(parent=parent)
        self.listplayer = listplayer
        self.mp = vlcqt.media_player

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


class FrameResPlaybackSlider(QSlider):
    slider_precision = 100  # Must match multiplier used by timer

    def __init__(self, parent, listplayer):
        super().__init__(Qt.Horizontal, parent)
        self.listplayer = listplayer
        self.mp = vlcqt.media_player
        self.setToolTip("Position")
        self.curr_pos = self.mp.get_position()
        self.mp_pos = None
        self.mouse_down = False

        self.slider_precision = self.slider_precision
        self.proportion_per_frame = 1
        self.length = 1

        _media = self.mp.get_media()
        if _media:
            self.conform_to_media(media=_media)

        self.listplayer.mediachanged.connect(self.on_mediachanged)
        self.mp.positionchanged.connect(self.on_positionchanged)
        self.mp.stopped.connect(self.on_stopped)

        self.newframe_conn = self.mp.newframe.connect(self.on_newframe)

    def conform_to_media(self, media):
        duration_secs = media.get_duration() / self.slider_precision
        self.total_frames = duration_secs * self.get_media_fps(media)
        self.proportion_per_frame = 1 / self.total_frames
        self.set_length(self.total_frames)
        self.curr_pos = self.mp_pos = self.mp.get_position()

    def setValue(self, value):
        if not self.mouse_down:
            super().setValue(value)

    def on_stopped(self, e):
        self.setValue(0)

    @pyqtSlot(vlc.Event)
    def on_mediachanged(self, e):
        self.conform_to_media(media=self.mp.get_media())

    @pyqtSlot(vlc.Event)
    def on_positionchanged(self, e):
        self.mp_pos = self.mp.get_position()
        self.mouse_down = False

    @pyqtSlot()
    def on_newframe(self):
        if self.mp_pos:
            self.curr_pos = self.mp_pos
            self.mp_pos = None
        else:
            self.curr_pos = self.curr_pos + self.proportion_per_frame
        self.setValue(self.curr_pos * self.length)

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
        # If length more than float max use float max.
        # This is for setting ticks. Can also just be set to 1.
        self.setMaximum(min((value, 2147483647)))
        self.length = self.maximum() - self.minimum()

    def get_mouse_pos(self, e):
        slider_min, slider_max = self.minimum(), self.maximum()
        slider_range = slider_max - slider_min
        pos_as_proportion = e.pos().x() / self.width()
        pos_as_slider_val = slider_range * pos_as_proportion + slider_min
        return pos_as_proportion, pos_as_slider_val

    @staticmethod
    def get_media_fps(vlc_media):
        if not vlc_media:
            return None
        if not vlc_media.is_parsed():
            vlc_media.parse()
        # track = [t for t in vlc_media.tracks_get()][0]
        return 30
