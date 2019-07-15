import logging

from .. import vlcqt

log = logging.getLogger(__name__)


class ViewpointManager:
    """Handles setting viewpoint in vlcqt media player object."""

    differential = 0.01 ** 20  # (0.01 ** 22) is max effective differential

    def __init__(self, client):
        self.mp = vlcqt.media_player
        self.client = client
        self.curr_yaw = self.curr_pitch = self.curr_roll = 0

        self.vp = vlcqt.VideoViewpoint()
        self.vp.field_of_view = 80

        self.mp.newframe.connect(self.on_newframe)
        self.mp.vout.connect(self.on_vout)
        # self.mp.timechanged.connect(self.on_timechanged)

    def on_vout(self):
        print("VOUT")
        self.trigger_redraw()

    def on_newframe(self):
        new_motion_state = self.client.get_new_motion_state()
        if new_motion_state:
            self.set_new_viewpoint(*new_motion_state)

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
        self.set_new_viewpoint(
            self.curr_yaw + self.differential, self.curr_pitch, self.curr_roll
        )
