import logging
from itertools import cycle

from PyQt5.QtCore import QObject, pyqtSlot

from .. import vlcqt

log = logging.getLogger(__name__)


class ViewpointManager(QObject):
    """Handles setting viewpoint in vlcqt media player object."""

    def __init__(self, remote_input_mngr):
        super().__init__()
        self.mp = vlcqt.media_player
        self.remote_input_mngr = remote_input_mngr

        self.vp = vlcqt.VideoViewpoint()
        self.vp.field_of_view = 80
        self.vp.yaw = self.vp.pitch = self.vp.roll = 0
        self.vp_params = [self.vp.yaw, self.vp.pitch, self.vp.roll]

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
        new_motion_state = self.remote_input_mngr.get_new_motion_state()
        if new_motion_state:
            self.set_new_viewpoint(*new_motion_state)
        else:
            self.trigger_redraw()

    def set_new_viewpoint(self, yaw, pitch, roll):
        self.vp.yaw, self.vp.pitch, self.vp.roll = -yaw, -pitch, -roll
        errorcode = self.mp.video_update_viewpoint(p_viewpoint=self.vp, b_absolute=True)
        if errorcode != 0:
            log.error("Error setting viewpoint")

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
        self.set_new_viewpoint(*self.vp_params)
