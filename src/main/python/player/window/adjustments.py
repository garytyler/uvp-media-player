from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from player import config
from player.common.popup import PopupWindowAction, PopupWindowWidget
from player.gui import icons, ontop


class VolumeSlider(QSlider):
    def __init__(self, parent, vol_mngr):
        super().__init__(parent=parent)
        self.vol_mngr = vol_mngr
        self.vol_mngr.set_volume(100)

        self.setToolTip("Volume")
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        self.valueChanged.connect(self.on_slider_valueChanged)

    def on_slider_valueChanged(self, value):
        self.vol_mngr.set_volume(value)


class AdjustmentsDialog(QDialog):
    def __init__(self, main_win):
        super().__init__(main_win)
        self.main_win = main_win
        self.setModal(False)
        self.setMinimumWidth(400)

        self.load()

        frame_geo = self.frameGeometry()
        center_pos = self.main_win.geometry().center()
        frame_geo.moveCenter(center_pos)
        self.move(frame_geo.topLeft())

    def load(self):
        self.setLayout(QVBoxLayout())
        self.form_lo = QFormLayout()
        self.layout().insertLayout(0, self.form_lo)

        # Settings
        self.server_url_edit = QLineEdit()
        self.server_url_edit.setText(config.state.url)
        self.form_lo.addRow(self.tr("Server URL"), self.server_url_edit)
        # self.form_lo.addRow(self.tr("Server URL"), self.server_url_edit)

        # Finish buttons
        self.save_bttn = QPushButton("Save", parent=self)
        self.cancel_bttn = QPushButton("Cancel", parent=self)

        self.finish_bttns_lo = QHBoxLayout()

        self.finish_bttns_lo.addWidget(self.save_bttn, 1, Qt.AlignRight)
        self.finish_bttns_lo.addWidget(self.cancel_bttn, 0, Qt.AlignRight)
        self.layout().addLayout(self.finish_bttns_lo)

        self.save_bttn.clicked.connect(self.accept)
        self.cancel_bttn.clicked.connect(self.reject)

    def save(self):
        config.state.url = self.server_url_edit.text()

    def accept(self):
        self.save()
        super().accept()

    def showEvent(self, e):
        main_always_on_top = ontop.get_always_on_top(self.main_win)
        ontop.set_always_on_top(self, main_always_on_top)
        self.raise_()


class ImageAdjustmentControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Adjustments")
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(QSlider())


class AdjustmentsPopupWindow(PopupWindowWidget):
    def __init__(self, main_win):
        super().__init__(parent=None)
        self.img_adjustment_ctrls_widget = ImageAdjustmentControlsWidget(parent=self)
        self.main_win = main_win

        self.setWindowTitle("Playlist")
        self.setLayout(QVBoxLayout(self))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.img_adjustment_ctrls_widget)

    def set_position(self):
        frame_geo = self.frameGeometry()
        center_pos = self.main_win.geometry().center()
        frame_geo.moveCenter(center_pos)
        self.move(frame_geo.topLeft())

    def showEvent(self, e):
        self.set_position()
        main_always_on_top = ontop.get_always_on_top(self.main_win)
        ontop.set_always_on_top(self, main_always_on_top)
        self.raise_()
        super().showEvent(e)


class OpenAdjustmentsPopupWindowAction(PopupWindowAction):
    def __init__(self, main_win):
        super().__init__(
            icon=icons.get("open_adjustments"),
            text="Adjustments",
            widget=AdjustmentsPopupWindow(main_win=main_win),
            main_win=main_win,
        )


class OpenAdjustmentsDialogAction(QAction):
    def __init__(self, main_win):
        super().__init__("Adjustments")

        self.main_win = main_win
        self.setIcon(icons.get("open_adjustments"))
        self.setCheckable(True)

        self.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        if checked:
            self.dialog = AdjustmentsDialog(self.main_win)
            self.dialog.finished.connect(self.on_dialog_finished)
            self.dialog.open()
        else:
            self.dialog.close()

    def on_dialog_finished(self, result):
        self.dialog.close()
        self.setChecked(False)
