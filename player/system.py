import sys
from contextlib import contextmanager

from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import *


"""
QApplication screen related

# Methods
app.screens()
app.primaryScreen()
app.platformName()

app.screenAt(point)
Parameters:	point  PyQt5.QtCore.QPoint
Return type:	PyQt5.QtGui.QScreen

# Events
app.screenAdded(screen)
app.screenRemoved(screen)

Also:
dt = QDesktopWidget()

"""

"""
def current_screen_size(self):
    wincenter = self.geometry().center()
    curscreen = QApplication.instance().screenAt(wincenter)
    screengeo = curscreen.geometry()
    return screengeo.size()
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


def move_to_qscreen(qwindow, qscreen=None):
    """Move qwindow to given qscreen. If not qscreen is given, try to move it to the
    largest qscreen that is not it's current active qscreen. Call after show()
    method.
    """
    wingeo = qwindow.geometry()
    if qscreen:
        targscreen = qscreen
    elif system.num_screens() <= 1:
        return
    else:
        currscreen = app.screenAt(wingeo.center())
        for s in system.get_current_qscreens():
            if s is not currscreen:
                targscreen = s
    targpos = targscreen.geometry().center()
    wingeo.moveCenter(targpos)
    qwindow.setGeometry(wingeo)


if __name__ == "__main__":
    app = QApplication()
    win = QMainWindow()
    win.show()
    move_to_qscreen(win)
    sys.exit(app.exec_())
