import logging
from os.path import exists

from PyQt5.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QVBoxLayout,
    QWidget,
)

# from . import picture
from . import (
    buttons,
    config,
    connect,
    frame,
    fullscreen,
    icons,
    main,
    playback,
    scale,
    sound,
    util,
    vlcqt,
    window,
)

log = logging.getLogger(__name__)


class MainMenuButton(buttons.SquareMenuButton):
    def __init__(self, parent, menu, size=None):
        super().__init__(
            parent=parent, menu=menu, size=size, icons=icons.main_menu_button
        )
        self.setToolTip("More Options")
        self.menu = menu
        self.curr_icon = icons.main_menu_button
        self.update_icon_hover()
        self.clicked.connect(self.open_menu)

    def on_clicked(self):
        is_checked = self.isChecked()
        self.setChecked(not is_checked)


class PlaybackSliderComponents(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        l, t, r, b = self.layout.getContentsMargins()
        self.layout.setContentsMargins(l, 0, r, 0)
        self.slider = playback.FrameResPlaybackSlider(parent=parent)
        self.layout.addWidget(self.slider)


class MainMenu(QMenu):
    def __init__(self, main_win: QMainWindow):
        super().__init__(parent=main_win)
        self.main_win = main_win

        # Open file
        self.open_file = QAction("Open file", self)
        self.open_file.triggered.connect(self._open_file)
        self.open_file.setShortcut("Ctrl+O")
        self.open_file.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.open_file.setShortcutVisibleInContextMenu(True)

        self.addAction(self.open_file)
        self.addMenu(scale.ViewScaleMenu(main_win=main_win))
        self.addAction(window.StayOnTop(main_win=main_win))

    def _open_file(self):
        file_path, filter_desc = QFileDialog.getOpenFileName(self, "Open file")
        if exists(file_path):
            vlcqt.list_player.set_mrls([file_path])


class AppWindow(QMainWindow):
    initialized = pyqtSignal()

    def __init__(self, flags=None):
        QMainWindow.__init__(self, flags=flags if flags else Qt.WindowFlags())
        self.qapp = QApplication.instance()
        self.mp = vlcqt.media_player

        # Set window title
        self.qapplication = QApplication.instance()
        self.app_display_name = self.qapplication.applicationDisplayName().strip()
        self.setWindowTitle(self.app_display_name)

        self.create_components()
        self.add_components()

        self.initialized.emit()

    def create_components(self):
        self.connect_label = connect.ServerConnectionWidget()
        self.frame_size_ctrlr = scale.MainMediaFrameSizeController(main_win=self)
        self.view_scale_menu = scale.ViewScaleMenu(main_win=self)
        self.mf_layout = frame.MainMediaFrameLayout(
            main_win=self, frame_size_ctrlr=self.frame_size_ctrlr
        )
        self.fullscreen_ctrlr = frame.FullscreenController(mf_layout=self.mf_layout)
        self.target_screen_menu = fullscreen.FullscreenMenu(
            main_win=self, fullscreen_ctrlr=self.fullscreen_ctrlr
        )
        self.fullscreen_button = fullscreen.FullscreenButton(
            parent=self,
            menu=self.target_screen_menu,
            fullscreen_ctrlr=self.fullscreen_ctrlr,
        )

        self.main_menu = MainMenu(main_win=self)

        self.skip_backward_button = playback.SkipBackwardButton(parent=self, size=48)
        self.play_pause_button = playback.PlayPauseButton(parent=self, size=48)
        self.skip_forward_button = playback.SkipForwardButton(parent=self, size=48)

        self.playback_mode_button = playback.PlaybackModeButton(parent=self, size=32)
        self.view_scale_menu_button = scale.ViewScaleButton(
            parent=self, view_scale_menu=self.view_scale_menu, size=32
        )

        self.volume_button = sound.VolumeButton(parent=self, size=32)
        self.main_menu_button = main.MainMenuButton(
            parent=self, size=48, menu=self.main_menu
        )

    def add_components(self):
        # Main layout
        self.widget = QWidget(self)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.widget)

        # Media frame
        # self.layout.addWidget(self.media_frame, 1)
        self.layout.addLayout(self.mf_layout, 1)

        # Controls layout
        self.ctrls_widget = QWidget(self)
        self.ctrls_layout = QGridLayout(self.ctrls_widget)
        self.ctrls_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ctrls_widget, 0)

        # Control components
        self.lower_right_buttons = QHBoxLayout()
        self.lower_right_buttons.setContentsMargins(0, 0, 0, 0)
        self.lower_right_buttons.addWidget(self.playback_mode_button)
        self.lower_right_buttons.addWidget(self.view_scale_menu_button)
        self.lower_right_buttons.addWidget(self.volume_button)
        self.lower_right_buttons.addWidget(self.main_menu_button)

        self.time_buttons = QHBoxLayout()
        self.time_buttons.setContentsMargins(0, 0, 0, 0)
        self.time_buttons.addWidget(self.skip_backward_button)
        self.time_buttons.addWidget(self.play_pause_button)
        self.time_buttons.addWidget(self.skip_forward_button)

        # self.midside_spacer = QSpacerItem(20, 0)
        # self.ctrls_layout.addItem(self.midside_spacer, 2, 1, 1, 1)
        # self.ctrls_layout.addItem(self.midside_spacer, 2, 3, 1, 1)

        self.lower_left_buttons = QHBoxLayout()
        # self.lower_left_buttons.setContentsMargins(0, 0, 0, 0)
        self.lower_left_buttons.addWidget(self.fullscreen_button)
        print(self.lower_left_buttons.totalSizeHint())
        self.upper_left_buttons = QHBoxLayout()

        # self.ctrls_layout.addWidget(self.pb_slider_components, 2, 0, 1, -1)
        self.ctrls_layout.addLayout(self.time_buttons, 3, 0, 1, -1, Qt.AlignHCenter)
        # self.ctrls_layout.addLayout(self.upper_left_buttons, 3, 0, 1, 2, Qt.AlignLeft)
        self.ctrls_layout.addLayout(self.lower_left_buttons, 4, 0, 1, 3, Qt.AlignLeft)
        self.ctrls_layout.addLayout(self.lower_right_buttons, 4, 4, 1, 1, Qt.AlignRight)

        self.ctrls_layout.setColumnStretch(0, 0)
        self.ctrls_layout.setColumnStretch(1, 0)
        self.ctrls_layout.setColumnStretch(2, 1)
        self.ctrls_layout.setColumnStretch(3, 0)
        self.ctrls_layout.setColumnStretch(5, 0)

        # lower_left_buttons_w = self.lower_right_buttons.sizeHint().width()
        # self.ctrls_layout.setColumnMinimumWidth(0, lower_left_buttons_w)
        # right_buttons_w = self.lower_left_buttons.sizeHint().width()
        # self.ctrls_layout.setColumnMinimumWidth(4, right_buttons_w)

    # def create_window_shortcuts(self):
    #     self.ctrl_w = QShortcut("Ctrl+W", self, self.close)
    #     # self.ctrl_plus = QShortcut(QKeySequence.ZoomIn, self, self.zoomer.zoom_in)
    #     # self.ctrl_i = QShortcut("Ctrl+I", self, self.zoomer.zoom_in)
    #     # self.ctrl_minus = QShortcut(QKeySequence.ZoomOut, self, self.zoomer.zoom_out)
    #     # self.shortcut_fullscreen = QShortcut("Ctrl+F", self, self.toggle_fullscreen)

    def set_window_subtitle(self, subtitle):
        self.app_display_name = self.qapplication.applicationDisplayName()
        if not subtitle.strip():
            raise ValueError("set_window_subtitle() requires a str value")
        if self.app_display_name and bool("python" != self.app_display_name):
            self.setWindowTitle(f"{self.app_display_name} - {subtitle}")
        else:
            self.setWindowTitle(subtitle)

    def set_stay_on_top(self):
        _args = self.main_win.windowFlags() | Qt.WindowStaysOnTopHint
        self.main_win.setWindowFlags(_args)
        self.main_win.show()

    def calculate_resize_values(self, media_w, media_h) -> (int, int):
        """Calculate total window resize values from current compoment displacement"""
        self.layout.removeWidget(self.ctrls_widget)
        wo_other_qsize = self.layout.totalSizeHint()
        self.layout.addWidget(self.ctrls_widget)
        with_other_qsize = self.layout.totalSizeHint()
        wo_other_w = util.positive_threshold(wo_other_qsize.width())
        wo_other_h = util.positive_threshold(wo_other_qsize.height())
        with_other_w = util.positive_threshold(with_other_qsize.width())
        with_other_h = util.positive_threshold(with_other_qsize.height())
        total_disp_w = with_other_w - wo_other_w
        total_disp_h = with_other_h - wo_other_h
        targ_w = media_w + total_disp_w
        targ_h = media_h + total_disp_h
        return targ_w, targ_h

    def screen_size_threshold_filter(self, target_width, target_height):
        main_win_geo = self.geometry()
        screen = self.qapp.screenAt(main_win_geo.center())
        screen_geo = screen.geometry()
        screen_w = screen_geo.width()
        screen_h = screen_geo.height()
        w = target_width if target_width < screen_w else screen_w
        h = target_height if target_height < screen_h else screen_h
        return w, h

    @pyqtSlot(int, int)
    def resize_to_media(self, media_w, media_h):
        targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
        self.showNormal()
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def showEvent(self, e):
        if 1 < config.state.view_scale:
            config.state.view_scale = 1
        media_w, media_h = self.frame_size_ctrlr.get_media_size(scaled=True)
        targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
        self.resize(targ_w, targ_h)
        self.size_hint_qsize = QSize(targ_w, targ_h)

    def sizeHint(self):
        try:
            return self.size_hint_qsize
        except AttributeError:
            media_w, media_h = self.frame_size_ctrlr.get_media_size(scaled=True)
            targ_w, targ_h = self.calculate_resize_values(media_w, media_h)
            self.size_hint_qsize = QSize(targ_w, targ_h)
        finally:
            return self.size_hint_qsize
