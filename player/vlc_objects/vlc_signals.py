import logging

import vlc
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot

from .. import util

log = logging.getLogger(__name__)


class MediaPlayerVlclibSignals(QObject):

    audiodevice = pyqtSignal(vlc.Event)
    audiovolume = pyqtSignal(vlc.Event)
    backward = pyqtSignal(vlc.Event)
    buffering = pyqtSignal(vlc.Event)
    chapterchanged = pyqtSignal(vlc.Event)
    corked = pyqtSignal(vlc.Event)
    esadded = pyqtSignal(vlc.Event)
    esdeleted = pyqtSignal(vlc.Event)
    esselected = pyqtSignal(vlc.Event)
    encounterederror = pyqtSignal(vlc.Event)
    endreached = pyqtSignal(vlc.Event)
    forward = pyqtSignal(vlc.Event)
    lengthchanged = pyqtSignal(vlc.Event)
    mediachanged = pyqtSignal(vlc.Event)
    muted = pyqtSignal(vlc.Event)
    nothingspecial = pyqtSignal(vlc.Event)
    opening = pyqtSignal(vlc.Event)
    pausablechanged = pyqtSignal(vlc.Event)
    paused = pyqtSignal(vlc.Event)
    playing = pyqtSignal(vlc.Event)
    positionchanged = pyqtSignal(vlc.Event)
    scrambledchanged = pyqtSignal(vlc.Event)
    seekablechanged = pyqtSignal(vlc.Event)
    snapshottaken = pyqtSignal(vlc.Event)
    stopped = pyqtSignal(vlc.Event)
    timechanged = pyqtSignal(vlc.Event)
    titlechanged = pyqtSignal(vlc.Event)
    uncorked = pyqtSignal(vlc.Event)
    unmuted = pyqtSignal(vlc.Event)
    vout = pyqtSignal(vlc.Event)

    def __init__(self, vlc_media_player: vlc.MediaPlayer):
        super().__init__()

        type_slot_pairs = [
            (vlc.EventType.MediaPlayerAudioDevice, self._audiodevice),
            (vlc.EventType.MediaPlayerAudioVolume, self._audiovolume),
            (vlc.EventType.MediaPlayerBackward, self._backward),
            (vlc.EventType.MediaPlayerBuffering, self._buffering),
            (vlc.EventType.MediaPlayerChapterChanged, self._chapterchanged),
            (vlc.EventType.MediaPlayerCorked, self._corked),
            (vlc.EventType.MediaPlayerESAdded, self._esadded),
            (vlc.EventType.MediaPlayerESDeleted, self._esdeleted),
            (vlc.EventType.MediaPlayerESSelected, self._esselected),
            (vlc.EventType.MediaPlayerEncounteredError, self._encounterederror),
            (vlc.EventType.MediaPlayerEndReached, self._endreached),
            (vlc.EventType.MediaPlayerForward, self._forward),
            (vlc.EventType.MediaPlayerLengthChanged, self._lengthchanged),
            (vlc.EventType.MediaPlayerMediaChanged, self._mediachanged),
            (vlc.EventType.MediaPlayerMuted, self._muted),
            (vlc.EventType.MediaPlayerNothingSpecial, self._nothingspecial),
            (vlc.EventType.MediaPlayerOpening, self._opening),
            (vlc.EventType.MediaPlayerPausableChanged, self._pausablechanged),
            (vlc.EventType.MediaPlayerPaused, self._paused),
            (vlc.EventType.MediaPlayerPlaying, self._playing),
            (vlc.EventType.MediaPlayerPositionChanged, self._positionchanged),
            (vlc.EventType.MediaPlayerScrambledChanged, self._scrambledchanged),
            (vlc.EventType.MediaPlayerSeekableChanged, self._seekablechanged),
            (vlc.EventType.MediaPlayerSnapshotTaken, self._snapshottaken),
            (vlc.EventType.MediaPlayerStopped, self._stopped),
            (vlc.EventType.MediaPlayerTimeChanged, self._timechanged),
            (vlc.EventType.MediaPlayerTitleChanged, self._titlechanged),
            (vlc.EventType.MediaPlayerUncorked, self._uncorked),
            (vlc.EventType.MediaPlayerUnmuted, self._unmuted),
            (vlc.EventType.MediaPlayerVout, self._vout),
        ]
        event_manager = vlc_media_player.event_manager()
        for e_type, cb_slot in type_slot_pairs:
            event_manager.event_attach(e_type, cb_slot)

    @pyqtSlot(vlc.Event)
    def _audiodevice(self, e):
        log.debug("_audiodevice")
        self.audiodevice.emit(e)

    @pyqtSlot(vlc.Event)
    def _audiovolume(self, e):
        log.debug("_audiovolume")
        self.audiovolume.emit(e)

    @pyqtSlot(vlc.Event)
    def _backward(self, e):
        log.debug("_backward")
        self.backward.emit(e)

    @pyqtSlot(vlc.Event)
    def _buffering(self, e):
        log.debug("_buffering")
        self.buffering.emit(e)

    @pyqtSlot(vlc.Event)
    def _chapterchanged(self, e):
        log.debug("_chapterchanged")
        self.chapterchanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _corked(self, e):
        log.debug("_corked")
        self.corked.emit(e)

    @pyqtSlot(vlc.Event)
    def _esadded(self, e):
        log.debug("_esadded")
        self.esadded.emit(e)

    @pyqtSlot(vlc.Event)
    def _esdeleted(self, e):
        log.debug("_esdeleted")
        self.esdeleted.emit(e)

    @pyqtSlot(vlc.Event)
    def _esselected(self, e):
        log.debug("_esselected")
        self.esselected.emit(e)

    @pyqtSlot(vlc.Event)
    def _encounterederror(self, e):
        log.debug("_encounterederror")
        self.encounterederror.emit(e)

    @pyqtSlot(vlc.Event)
    def _endreached(self, e):
        log.debug("_endreached")
        self.endreached.emit(e)

    @pyqtSlot(vlc.Event)
    def _forward(self, e):
        log.debug("_forward")
        self.forward.emit(e)

    @pyqtSlot(vlc.Event)
    def _lengthchanged(self, e):
        log.debug("_lengthchanged")
        self.lengthchanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _mediachanged(self, e):
        log.debug("_mediachanged")
        self.mediachanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _muted(self, e):
        log.debug("_muted")
        self.muted.emit(e)

    @pyqtSlot(vlc.Event)
    def _nothingspecial(self, e):
        log.debug("_nothingspecial")
        self.nothingspecial.emit(e)

    @pyqtSlot(vlc.Event)
    def _opening(self, e):
        log.debug("_opening")
        self.opening.emit(e)

    @pyqtSlot(vlc.Event)
    def _pausablechanged(self, e):
        log.debug("_pausablechanged")
        self.pausablechanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _paused(self, e):
        log.debug("_paused")
        self.paused.emit(e)

    @pyqtSlot(vlc.Event)
    def _playing(self, e):
        log.debug("_playing")
        self.playing.emit(e)

    @pyqtSlot(vlc.Event)
    def _positionchanged(self, e):
        log.debug("_positionchanged")
        self.positionchanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _scrambledchanged(self, e):
        log.debug("_scrambledchanged")
        self.scrambledchanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _seekablechanged(self, e):
        log.debug("_seekablechanged")
        self.seekablechanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _snapshottaken(self, e):
        log.debug("_snapshottaken")
        self.snapshottaken.emit(e)

    @pyqtSlot(vlc.Event)
    def _stopped(self, e):
        log.debug("_stopped")
        self.stopped.emit(e)

    @pyqtSlot(vlc.Event)
    def _timechanged(self, e):
        log.debug("_timechanged")
        self.timechanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _titlechanged(self, e):
        log.debug("_titlechanged")
        self.titlechanged.emit(e)

    @pyqtSlot(vlc.Event)
    def _uncorked(self, e):
        log.debug("_uncorked")
        self.uncorked.emit(e)

    @pyqtSlot(vlc.Event)
    def _unmuted(self, e):
        log.debug("_unmuted")
        self.unmuted.emit(e)

    @pyqtSlot(vlc.Event)
    def _vout(self, e):
        log.debug("_vout")
        self.vout.emit(e)


class MediaPlayerCustomSignals(MediaPlayerVlclibSignals):
    newframe = pyqtSignal()

    def __init__(self, vlc_media_player: vlc.MediaPlayer):
        super().__init__(vlc_media_player=vlc_media_player)

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.on_timeout)

        self.playing.connect(self.timer.start)
        self.stopped.connect(self.timer.stop)
        self.paused.connect(self.timer.stop)

        self.__has_media = True if self._vlc_obj.get_media() else False
        self.mediachanged.connect(self.on_mediachanged)

    def on_timeout(self):
        self.newframe.emit()

    @property
    def has_media(self):
        return self.__has_media

    @property
    def media_size(self):
        return self.__has_media

    def on_mediachanged(self, e):
        media = self._vlc_obj.get_media()

        # Update common has_media bool
        self.__has_media = True if self._vlc_obj.get_media() else False

        # Set timer
        media_fps = util.get_media_fps(media)
        playback_fps = media_fps * self.get_rate()
        self.timer.setInterval(1000 / playback_fps)


MediaPlayerSignals = MediaPlayerCustomSignals


class MediaListPlayerVlclibSignals(QObject):

    nextitemset = pyqtSignal(vlc.Event)
    played = pyqtSignal(vlc.Event)
    stopped = pyqtSignal(vlc.Event)

    def __init__(self, vlc_media_list_player: vlc.MediaListPlayer):
        super().__init__()

        type_slot_pairs = [
            (vlc.EventType.MediaListPlayerNextItemSet, self._nextitemset),
            (vlc.EventType.MediaListPlayerPlayed, self._played),
            (vlc.EventType.MediaListPlayerStopped, self._stopped),
        ]
        event_manager = vlc_media_list_player.event_manager()
        for e_type, cb_slot in type_slot_pairs:
            event_manager.event_attach(e_type, cb_slot)

    @pyqtSlot(vlc.Event)
    def _nextitemset(self, e):
        log.debug("_nextitemset")
        self.nextitemset.emit(e)

    @pyqtSlot(vlc.Event)
    def _played(self, e):
        log.debug("_played")
        self.played.emit(e)

    @pyqtSlot(vlc.Event)
    def _stopped(self, e):
        log.debug("_stopped")
        self.stopped.emit(e)


MediaListPlayerSignals = MediaListPlayerVlclibSignals
