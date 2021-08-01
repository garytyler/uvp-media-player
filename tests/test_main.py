from PyQt5.QtWidgets import QWidget


def test_play_on_load(qtbot, main_win, media_dir):
    playlist_view = main_win.findChild(QWidget, "playlist-view")
    time_slider = main_win.findChild(QWidget, "main-time-slider")
    main_win.load_media(str(media_dir / "360vid_5sec.mp4"))
    qtbot.waitUntil(lambda: playlist_view.model().rowCount() > 0)
    time_at_load = time_slider.value()
    qtbot.wait(500)
    time_check = time_slider.value()
    assert time_check
    assert time_at_load != time_check
