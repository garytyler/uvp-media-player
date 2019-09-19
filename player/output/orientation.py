import logging
from itertools import cycle

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStatusBar

from .. import vlcqt
from ..gui import fonts, icons
from .status import IconStatusLabel

log = logging.getLogger(__name__)


class ViewpointManager(QObject):
    """Handles setting viewpoint in vlcqt media player object."""

    updatedviewpoint = pyqtSignal(float, float, float)

    def __init__(self, io_ctrlr):
        super().__init__()
        self.mp = vlcqt.media_player
        self.io_ctrlr = io_ctrlr

        self.user_vp = vlcqt.VideoViewpoint()
        self.user_vp.field_of_view = 80
        self.user_vp.yaw = self.user_vp.pitch = self.user_vp.roll = 0
        self.vp_params = [self.user_vp.yaw, self.user_vp.pitch, self.user_vp.roll]

        self.adjusted_vp = vlcqt.VideoViewpoint()
        minor_diff = 0.01
        self.minor_diffs_cycle = cycle((minor_diff, -minor_diff))
        self.param_indexes_cycle = cycle((0, 1, 2))
        self.is_enabled = False

        self.mp.newframe.connect(self.on_newframe)
        self.mp.vout.connect(self.trigger_redraw)  # Not needed if updating per frame

    def enable_per_frame_updates(self, value):
        self.is_enabled = value
        if value:
            self.trigger_redraw()

    @pyqtSlot()
    def on_newframe(self):
        if not self.is_enabled:
            return
        new_motion_state = self.io_ctrlr.get_new_motion_state()
        if new_motion_state:
            self.set_new_user_viewpoint(*new_motion_state)
        else:
            self.trigger_redraw()

    def _update_viewpoint(self, viewpoint: vlcqt.VideoViewpoint):
        """Update given viewpoint in player"""
        errorcode = self.mp.video_update_viewpoint(
            p_viewpoint=viewpoint, b_absolute=True
        )
        if errorcode != 0:
            log.error("Error setting viewpoint")
        self.updatedviewpoint.emit(
            self.user_vp.yaw, self.user_vp.pitch, self.user_vp.roll
        )

    def set_new_user_viewpoint(self, yaw, pitch, roll):
        """Set a new user viewpoint."""
        self.user_vp.yaw = -yaw
        self.user_vp.pitch = -pitch
        self.user_vp.roll = -roll
        self._update_viewpoint(self.user_vp)

    def set_new_adjusted_viewpoint(self, yaw_diff, pitch_diff, roll_diff):
        """Set new adjusted viewpoint. Passed values are applied as adjustments to the
        latest user viewpoint.
        """
        self.adjusted_vp.yaw = self.user_vp.yaw + -yaw_diff
        self.adjusted_vp.pitch = self.user_vp.pitch + -pitch_diff
        self.adjusted_vp.roll = self.user_vp.roll + -roll_diff
        self._update_viewpoint(self.adjusted_vp)

    def trigger_redraw(self):
        """Force a redraw of the video frame to correct the displayed aspect ratio
        of a 360 video.

        The redraw is triggered by a hack... setting a new viewpoint with an
        unobservable differential applied to the yaw value. This is probably only
        necessary because of the the implementation of viewpoints in vlclib 3.0, and
        will hopefully be unnecessary in 4.0.
        """
        diff = next(self.minor_diffs_cycle)
        index = next(self.param_indexes_cycle)
        param = self.vp_params[index]
        self.vp_params[index] = param + diff
        self.set_new_adjusted_viewpoint(*self.vp_params)


class OrientationStatusLabel(IconStatusLabel):
    def __init__(self, viewpoint_mngr: ViewpointManager, parent: QStatusBar = None):
        super().__init__(parent=parent, icon=icons.virtual_reality)
        self.viewpoint_mngr = viewpoint_mngr
        self.set_status("- - -", QIcon.Disabled, QIcon.Off)

        self.text_lbl.setFont(fonts.get_fixed_pitch_font())
        self.viewpoint_mngr.updatedviewpoint.connect(self.on_updatedviewpoint)

    @pyqtSlot(float, float, float)
    def on_updatedviewpoint(self, yaw, pitch, roll):
        self.set_status(f"{yaw:+.2f} {pitch:+.2f} {roll:+.2f}", QIcon.Normal, QIcon.Off)
