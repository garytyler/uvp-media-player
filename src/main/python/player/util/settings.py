from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from player.gui import icons, ontop
from player.util import config


class SettingsDialog(QDialog):
    def __init__(self, main_win):
        super().__init__(main_win)
        self.main_win = main_win
        self.setModal(True)
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


class OpenSettingsAction(QAction):
    def __init__(self, main_win):
        super().__init__("Settings")

        self.main_win = main_win
        self.setIcon(icons.get("open_settings"))
        self.setCheckable(True)

        self.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        if checked:
            self.dialog = SettingsDialog(self.main_win)
            self.dialog.finished.connect(self.on_dialog_finished)
            self.dialog.open()
        else:
            self.dialog.close()

    def on_dialog_finished(self, result):
        self.dialog.close()
        self.setChecked(False)
