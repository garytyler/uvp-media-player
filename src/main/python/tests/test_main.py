from PyQt5.QtCore import Qt


def test_main_load_media(qtbot, appwin, play_button, playlist_view):
    appwin.load_media("media/360vid_5sec.mp4")
    qtbot.addWidget(appwin)
    qtbot.mouseClick(play_button, Qt.LeftButton)
    qtbot.waitSignal(appwin.listplayer.mediachanged, timeout=5000)
    assert playlist_view.model().item(0)
