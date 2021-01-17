from PyQt5 import QtWidgets

from app import base, config, gui


class ClientSettingsDialog(base.modal.BaseModalSettingsDialog):
    def __init__(self, main_win):
        super().__init__(main_win=main_win, modal=True)

    def create(self, widget):
        form_lo = QtWidgets.QFormLayout()
        widget.setLayout(form_lo)

        self.server_url_edit = QtWidgets.QLineEdit()
        self.server_url_edit.setText(config.state.url)
        form_lo.addRow(self.tr("Server URL"), self.server_url_edit)

    def save(self):
        config.state.url = self.server_url_edit.text()


class OpenClientSettingsDialogAction(base.modal.BaseOpenModalSettingsDialogAction):
    def __init__(self, main_win):
        super().__init__(
            text="Client Settings",
            main_win=main_win,
            icon=gui.icons.get("open_client_settings"),
        )

    def create(self):
        return ClientSettingsDialog(self.main_win)
