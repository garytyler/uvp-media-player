import sys
import vlc
import platform
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QSize


class PlayerGUI(QtWidgets.QMainWindow):
    instance = vlc.Instance()

    def __init__(self, videofile, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # State vars
        self.is_paused = False
        self.media = None

        self.create_mediaplayer(videofile)
        self.create_videoframe()
        self.create_gui()

    def create_mediaplayer(self, videofile):

        # VLC setup
        self.mediaplayer = self.instance.media_player_new()
        self.media = self.instance.media_new(videofile)
        self.media.parse()

        # Get video track dimensions
        videotrack = [t for t in self.media.tracks_get()][0].video
        self.track_framerate = videotrack.contents.frame_rate_num
        self.track_width, self.track_height = (
            videotrack.contents.width,
            videotrack.contents.height,
        )
        self.track_aspectratio = self.track_width / self.track_height

        # Add media to mediaplayer
        self.mediaplayer.set_media(self.media)

        self.setWindowTitle("Media Player")

        self.widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Set track title as window title
        self.setWindowTitle(self.media.get_meta(0))

    def create_videoframe(self):
        # Video frame
        if platform.system() == "Darwin":  # for MacOS
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame(self)

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        if platform.system() == "Linux":  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

    def create_gui(self):
        # Menu bars
        menubar = self.menuBar()
        filemenu = menubar.addMenu("File")

        exitaction = QtWidgets.QAction("Exit", self)
        exitaction.triggered.connect(self.close)
        exitaction.setShortcut("Ctrl+W")
        filemenu.addAction(exitaction)

        # Main layouts
        self.videolayout = QtWidgets.QVBoxLayout()
        self.videowidget = QtWidgets.QWidget(self)
        self.videowidget.setLayout(self.videolayout)

        self.ctrlslayout = QtWidgets.QVBoxLayout()
        self.ctrlswidget = QtWidgets.QWidget(self)
        self.ctrlswidget.setLayout(self.ctrlslayout)

        self.videolayout.addWidget(self.videoframe, 0)
        self.layout.addWidget(self.videowidget, 1)
        self.layout.addWidget(self.ctrlswidget, 0, Qt.AlignBottom)

        """
        For setting the video frame size, it's best to put the videoframe QFrame inside
        of it's own widget, which will resize separately from the videoframe QFrame. Pull that widget's size to set the size of the videoframe QFrame
        """

        self.videoframe.sizeHint = lambda: QSize(
            self.videowidget.width() * self.track_aspectratio, self.videowidget.width()
        )

        self.positionslider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)
        self.ctrlslayout.addWidget(self.positionslider, stretch=0)

        # Player buttons
        self.playbttnslayout = QtWidgets.QHBoxLayout()
        self.ctrlslayout.addLayout(self.playbttnslayout, stretch=0)

        self.playbutton = QtWidgets.QPushButton("Play", self)
        self.playbutton.setToolTip("Play")
        self.playbutton.clicked.connect(self.play_pause_button)

        self.stopbutton = QtWidgets.QPushButton("Stop", self)
        self.stopbutton.setToolTip("Stop")
        self.stopbutton.clicked.connect(self.stop)

        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setToolTip("Volume")
        self.volumeslider.setMaximum(100)
        self.volumeslider.setMinimumWidth(100)
        self.volumeslider.setMaximumWidth(400)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())

        self.playbttnslayout.addWidget(self.playbutton)
        self.playbttnslayout.addWidget(self.stopbutton)
        self.playbttnslayout.addStretch(2)
        self.playbttnslayout.addWidget(QtWidgets.QLabel("Volume"))
        self.playbttnslayout.addWidget(self.volumeslider, stretch=1)

        self.playtimer = QtCore.QTimer(self)
        self.playtimer.setInterval(100)
        self.playtimer.timeout.connect(self.update_ui)

        self.eventmanager = self.mediaplayer.event_manager()
        self.eventmanager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.on_end_reached, self.playtimer
        )

    def on_end_reached(self, e, timer):
        self.mediaplayer.set_position(0)
        self.playbutton.setText("Play")
        self.is_paused = True

    def videoframe_sizeHint(self):
        width = self.mediaplayer.video_get_width()
        height = self.mediaplayer.video_get_height()
        return QSize(width, height)

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.playtimer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.playtimer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.playtimer.start()

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def set_volume(self, value):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(value)
        self.volumeslider.setValue(value)

    def play_pause_button(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.playtimer.stop()
        else:
            if self.mediaplayer.play() == -1:
                # Not sure what this does, but I removed open_file() so disabled it for now
                # self.open_file()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.playtimer.start()
            self.is_paused = False

    def set_viewpoint_by_viewpoint(self, viewpoint):
        self.vp = viewpoint
        try:
            errorcode = self.mediaplayer.video_update_viewpoint(
                p_viewpoint=self.vp, b_absolute=True
            )
        except Exception as e:
            print(e)
            raise KeyboardInterrupt
        finally:
            if errorcode != 0:
                raise RuntimeError("Error setting viewpoint")

    def set_viewpoint_by_data(self, yaw, pitch, roll, fov=80):
        """
        NOTE: Default field of view in VLC-iOS is 80 degrees

        view point yaw in degrees  ]-180;180]
        view point pitch in degrees  ]-90;90]
        view point roll in degrees ]-180;180]
        field of view in degrees ]0;180[ (default 80)

        # Free C++ pointer func
        vlc.libvlc_free(self.vp)
        """

        # # Class instatiation
        # self.vp = vlc.VideoViewpoint()
        # self.vp.field_of_view = 80
        # self.vp.yaw, self.vp.pitch, self.vp.roll, = (-y, -p, -r)

        # Recommended instatiation
        self.vp = vlc.libvlc_video_new_viewpoint()
        self.vp.contents.field_of_view = fov
        self.vp.contents.yaw = yaw
        self.vp.contents.pitch = pitch
        self.vp.contents.roll = roll

        errorcode = self.mediaplayer.video_update_viewpoint(
            p_viewpoint=self.vp, b_absolute=True
        )
        if errorcode != 0:
            raise RuntimeError("Error setting viewpoint")


def autoplay(media_path):
    app = QtWidgets.QApplication(sys.argv)
    playergui = PlayerGUI(media_path)
    playergui.show()
    playergui.play_pause_button()
    sys.exit(app.exec_())
