import logging

import vlc
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot

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
    stopped = pyqtSignal(vlc.Event)
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
            # (vlc.EventType.MediaPlayerAudioDevice, self._audiodevice),
            (vlc.EventType.MediaPlayerAudioVolume, self._audiovolume),
            # (vlc.EventType.MediaPlayerBackward, self._backward),
            (vlc.EventType.MediaPlayerBuffering, self._buffering),
            # (vlc.EventType.MediaPlayerChapterChanged, self._chapterchanged),
            # (vlc.EventType.MediaPlayerCorked, self._corked),
            # (vlc.EventType.MediaPlayerESAdded, self._esadded),
            # (vlc.EventType.MediaPlayerESDeleted, self._esdeleted),
            # (vlc.EventType.MediaPlayerESSelected, self._esselected),
            # (vlc.EventType.MediaPlayerEncounteredError, self._encounterederror),
            (vlc.EventType.MediaPlayerEndReached, self._endreached),
            # (vlc.EventType.MediaPlayerForward, self._forward),
            # (vlc.EventType.MediaPlayerLengthChanged, self._lengthchanged),
            (vlc.EventType.MediaPlayerMediaChanged, self._mediachanged),
            (vlc.EventType.MediaPlayerMuted, self._muted),
            (vlc.EventType.MediaPlayerNothingSpecial, self._nothingspecial),
            (vlc.EventType.MediaPlayerOpening, self._opening),
            (vlc.EventType.MediaPlayerPausableChanged, self._pausablechanged),
            (vlc.EventType.MediaPlayerPaused, self._paused),
            (vlc.EventType.MediaPlayerPlaying, self._playing),
            (vlc.EventType.MediaPlayerPositionChanged, self._positionchanged),
            # (vlc.EventType.MediaPlayerScrambledChanged, self._scrambledchanged),
            # (vlc.EventType.MediaPlayerSeekableChanged, self._seekablechanged),
            # (vlc.EventType.MediaPlayerSnapshotTaken, self._snapshottaken),
            (vlc.EventType.MediaPlayerStopped, self._stopped),
            # (vlc.EventType.MediaPlayerTimeChanged, self._timechanged),
            # (vlc.EventType.MediaPlayerTitleChanged, self._titlechanged),
            # (vlc.EventType.MediaPlayerUncorked, self._uncorked),
            # (vlc.EventType.MediaPlayerUnmuted, self._unmuted),
            (vlc.EventType.MediaPlayerVout, self._vout),
        ]
        event_manager = vlc_media_player.event_manager()
        for e_type, cb_slot in type_slot_pairs:
            event_manager.event_attach(e_type, cb_slot)

    @pyqtSlot(vlc.Event)
    def _audiodevice(self, e):
        self.audiodevice.emit(e)
        log.debug("VLCQT SIGNAL name='audiodevice'")

    @pyqtSlot(vlc.Event)
    def _audiovolume(self, e):
        self.audiovolume.emit(e)
        log.debug("VLCQT SIGNAL name='audiovolume'")

    @pyqtSlot(vlc.Event)
    def _backward(self, e):
        self.backward.emit(e)
        log.debug("VLCQT SIGNAL name='backward'")

    @pyqtSlot(vlc.Event)
    def _buffering(self, e):
        self.buffering.emit(e)
        log.debug("VLCQT SIGNAL name='buffering'")

    @pyqtSlot(vlc.Event)
    def _chapterchanged(self, e):
        self.chapterchanged.emit(e)
        log.debug("VLCQT SIGNAL name='chapterchanged'")

    @pyqtSlot(vlc.Event)
    def _corked(self, e):
        self.corked.emit(e)
        log.debug("VLCQT SIGNAL name='corked'")

    @pyqtSlot(vlc.Event)
    def _esadded(self, e):
        self.esadded.emit(e)
        log.debug("VLCQT SIGNAL name='esadded'")

    @pyqtSlot(vlc.Event)
    def _esdeleted(self, e):
        self.esdeleted.emit(e)
        log.debug("VLCQT SIGNAL name='esdeleted'")

    @pyqtSlot(vlc.Event)
    def _esselected(self, e):
        self.esselected.emit(e)
        log.debug("VLCQT SIGNAL name='esselected'")

    @pyqtSlot(vlc.Event)
    def _encounterederror(self, e):
        self.encounterederror.emit(e)
        log.debug("VLCQT SIGNAL name='encounterederror'")

    @pyqtSlot(vlc.Event)
    def _endreached(self, e):
        self.endreached.emit(e)
        log.debug("VLCQT SIGNAL name='endreached'")

    @pyqtSlot(vlc.Event)
    def _forward(self, e):
        self.forward.emit(e)
        log.debug("VLCQT SIGNAL name='forward'")

    @pyqtSlot(vlc.Event)
    def _lengthchanged(self, e):
        self.lengthchanged.emit(e)
        log.debug("VLCQT SIGNAL name='lengthchanged'")

    @pyqtSlot(vlc.Event)
    def _mediachanged(self, e):
        self.mediachanged.emit(e)
        log.debug("VLCQT SIGNAL name='mediachanged'")

    @pyqtSlot(vlc.Event)
    def _muted(self, e):
        self.muted.emit(e)
        log.debug("VLCQT SIGNAL name='muted'")

    @pyqtSlot(vlc.Event)
    def _nothingspecial(self, e):
        self.nothingspecial.emit(e)
        log.debug("VLCQT SIGNAL name='nothingspecial'")

    @pyqtSlot(vlc.Event)
    def _opening(self, e):
        self.opening.emit(e)
        log.debug("VLCQT SIGNAL name='opening'")

    @pyqtSlot(vlc.Event)
    def _pausablechanged(self, e):
        self.pausablechanged.emit(e)
        log.debug("VLCQT SIGNAL name='pausablechanged'")

    @pyqtSlot(vlc.Event)
    def _paused(self, e):
        self.paused.emit(e)
        log.debug("VLCQT SIGNAL name='paused'")

    @pyqtSlot(vlc.Event)
    def _playing(self, e):
        self.playing.emit(e)
        log.debug("VLCQT SIGNAL name='playing'")

    @pyqtSlot(vlc.Event)
    def _positionchanged(self, e):
        self.positionchanged.emit(e)
        # log.debug("VLCQT SIGNAL name='positionchanged'")

    @pyqtSlot(vlc.Event)
    def _scrambledchanged(self, e):
        self.scrambledchanged.emit(e)
        log.debug("VLCQT SIGNAL name='scrambledchanged'")

    @pyqtSlot(vlc.Event)
    def _seekablechanged(self, e):
        self.seekablechanged.emit(e)
        log.debug("VLCQT SIGNAL name='seekablechanged'")

    @pyqtSlot(vlc.Event)
    def _snapshottaken(self, e):
        self.snapshottaken.emit(e)
        log.debug("VLCQT SIGNAL name='snapshottaken'")

    @pyqtSlot(vlc.Event)
    def _stopped(self, e):
        self.stopped.emit(e)
        log.debug("VLCQT SIGNAL name='stopped'")

    @pyqtSlot(vlc.Event)
    def _timechanged(self, e):
        self.timechanged.emit(e)
        log.debug("VLCQT SIGNAL name='timechanged'")

    @pyqtSlot(vlc.Event)
    def _titlechanged(self, e):
        self.titlechanged.emit(e)
        log.debug("VLCQT SIGNAL name='titlechanged'")

    @pyqtSlot(vlc.Event)
    def _uncorked(self, e):
        self.uncorked.emit(e)
        log.debug("VLCQT SIGNAL name='uncorked'")

    @pyqtSlot(vlc.Event)
    def _unmuted(self, e):
        self.unmuted.emit(e)
        log.debug("VLCQT SIGNAL name='unmuted'")

    @pyqtSlot(vlc.Event)
    def _vout(self, e):
        self.vout.emit(e)
        log.debug("VLCQT SIGNAL name='vout'")


class MediaPlayerCustomSignals(MediaPlayerVlclibSignals):
    newframe = pyqtSignal()
    slider_precision = 100

    def __init__(self, vlc_media_player: vlc.MediaPlayer):
        super().__init__(vlc_media_player=vlc_media_player)
        self.timer = QTimer()
        self.timer.setTimerType(Qt.CoarseTimer)
        self.timer.timeout.connect(self.on_timeout)

        self.playing.connect(self.timer.start)
        self.stopped.connect(self.timer.stop)
        self.paused.connect(self.timer.stop)

        self.mediachanged.connect(self.on_mediachanged)

    def on_timeout(self):
        self.newframe.emit()

    def has_media(self):
        return True if self._vlc_obj.get_media() else False

    def on_mediachanged(self, e):
        media = self.get_media()
        if not media.is_parsed():
            media.parse()
        media_fps = self._get_media_fps(media)
        playback_fps = media_fps * self.get_rate()
        self.timer.setInterval(self.slider_precision / playback_fps)

    def _get_media_fps(self, vlc_media: vlc.Media) -> float:
        if not vlc_media:
            return 30
        if not vlc_media.is_parsed():
            vlc_media.parse()
        tracks = vlc_media.tracks_get()
        if not tracks:
            return 30
        track = [t for t in tracks if t is not None][0]
        return track.video.contents.frame_rate_num


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
        self.nextitemset.emit(e)
        log.debug("VLCQT SIGNAL name='nextitemset'")

    @pyqtSlot(vlc.Event)
    def _played(self, e):
        self.played.emit(e)
        log.debug("VLCQT SIGNAL name='played'")

    @pyqtSlot(vlc.Event)
    def _stopped(self, e):
        self.stopped.emit(e)
        log.debug("VLCQT SIGNAL name='stopped'")


MediaListPlayerSignals = MediaListPlayerVlclibSignals


class MediaVlclibSignals(QObject):

    mediadurationchanged = pyqtSignal(vlc.Event)
    mediafreed = pyqtSignal(vlc.Event)
    mediametachanged = pyqtSignal(vlc.Event)
    mediaparsedchanged = pyqtSignal(vlc.Event)
    mediastatechanged = pyqtSignal(vlc.Event)
    mediasubitemadded = pyqtSignal(vlc.Event)
    mediasubitemtreeadded = pyqtSignal(vlc.Event)
    mediathumbnailgenerated = pyqtSignal(vlc.Event)
    metadataready = pyqtSignal(dict)

    def __init__(self, vlc_media: vlc.Media):
        super().__init__()

        type_slot_pairs = [
            (vlc.EventType.MediaDurationChanged, self.__MediaDurationChanged),
            (vlc.EventType.MediaFreed, self.__MediaFreed),
            (vlc.EventType.MediaMetaChanged, self.__MediaMetaChanged),
            (vlc.EventType.MediaParsedChanged, self.__MediaParsedChanged),
            (vlc.EventType.MediaStateChanged, self.__MediaStateChanged),
            (vlc.EventType.MediaSubItemAdded, self.__MediaSubItemAdded),
            (vlc.EventType.MediaSubItemTreeAdded, self.__MediaSubItemTreeAdded),
        ]
        event_manager = vlc_media.event_manager()
        for e_type, cb_slot in type_slot_pairs:
            event_manager.event_attach(e_type, cb_slot)

    @pyqtSlot(vlc.Event)
    def __MediaDurationChanged(self, e):
        try:
            self.mediadurationchanged.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediadurationchanged'")

    @pyqtSlot(vlc.Event)
    def __MediaFreed(self, e):
        try:
            self.mediafreed.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediafreed'")

    @pyqtSlot(vlc.Event)
    def __MediaMetaChanged(self, e):
        try:
            self.mediametachanged.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediametachanged'")

    @pyqtSlot(vlc.Event)
    def __MediaParsedChanged(self, e):
        try:
            self.mediaparsedchanged.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediaparsedchanged'")

    @pyqtSlot(vlc.Event)
    def __MediaStateChanged(self, e):
        try:
            self.mediastatechanged.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediastatechanged'")

    @pyqtSlot(vlc.Event)
    def __MediaSubItemAdded(self, e):
        try:
            self.mediasubitemadded.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediasubitemadded'")

    @pyqtSlot(vlc.Event)
    def __MediaSubItemTreeAdded(self, e):
        try:
            self.mediasubitemtreeadded.emit(e)
        except AttributeError as e:
            log.error(e)
        log.debug("VLCQT SIGNAL name='mediasubitemtreeadded'")


MediaSignals = MediaVlclibSignals
