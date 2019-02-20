import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import QWindow
from contextlib import contextmanager

"""
QApplication screen related

# Methods
app.screens()
app.primaryScreen()
app.platformName()

app.screenAt(point)
Parameters:	point  PySide2.QtCore.QPoint
Return type:	PySide2.QtGui.QScreen

# Events
app.screenAdded(screen)
app.screenRemoved(screen)

Also:
dt = QDesktopWidget()

"""


@contextmanager
def qapp():
    _qapplication = QApplication.instance()

    if _qapplication:
        yield _qapplication
    else:
        yield QApplication(sys.argv)
    del _qapplication


def num_screens():
    with qapp() as app:
        return len(app.screens())


def qscreen_area(qscreen) -> int:
    """Return screen area of given QScreen"""
    return qscreen.geometry().width() * qscreen.geometry().height()


def get_current_qscreens() -> list:
    """Return screens sorted largest to smallest"""
    with qapp() as app:
        return sorted(app.screens(), key=qscreen_area, reverse=True)


if __name__ == "__main__":
    app = QApplication()
    win = QMainWindow()
    win.show()
    sys.exit(app.exec_())
