from PyQt5 import QtCore, QtWidgets


class BaseModalSettingsDialog(QtWidgets.QDialog):
    """Base modal settings dialog that closes when 'Save' is clicked."""

    def __init__(self, main_win, title=None, modal=True):
        super().__init__(main_win)
        self.main_win = main_win
        if title:
            self.setWindowTitle(title)
        self.setModal(modal)
        self.setMinimumWidth(400)

        # Provide a base widget
        self.setLayout(QtWidgets.QVBoxLayout())
        base_widget = QtWidgets.QWidget()
        base_widget.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(base_widget)
        self.create(base_widget)

        # Finish buttons
        self.save_bttn = QtWidgets.QPushButton("Save", parent=self)
        self.cancel_bttn = QtWidgets.QPushButton("Cancel", parent=self)

        self.finish_bttns_lo = QtWidgets.QHBoxLayout()

        self.finish_bttns_lo.addWidget(self.save_bttn, 1, QtCore.Qt.AlignRight)
        self.finish_bttns_lo.addWidget(self.cancel_bttn, 0, QtCore.Qt.AlignRight)
        self.layout().addLayout(self.finish_bttns_lo)

        self.save_bttn.clicked.connect(self.accept)
        self.cancel_bttn.clicked.connect(self.reject)

    @classmethod
    def create(widget) -> QtWidgets.QWidget:
        """Must return a QWidget that will provide the main contents"""
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def accept(self):
        self.save()
        super().accept()


class BaseOpenModalSettingsDialogAction(QtWidgets.QAction):
    def __init__(self, text, main_win, icon):
        super().__init__(text=text)
        self.main_win = main_win

        self.setIcon(icon)
        self.setCheckable(True)
        self.toggled.connect(self.on_toggled)

    def create(self) -> BaseModalSettingsDialog:
        """Must return a BaseModalSettingsDialog"""
        raise NotImplementedError

    def on_toggled(self, checked):
        if checked:
            self.dialog = self.create()
            self.dialog.finished.connect(self.on_dialog_finished)
            self.dialog.show()
        else:
            self.dialog.close()

    def on_dialog_finished(self, result):
        self.dialog.close()
        self.setChecked(False)
