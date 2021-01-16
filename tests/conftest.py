import pytest
from main import AppWindow


@pytest.fixture
def appwin(qtbot):
    return AppWindow()


@pytest.fixture
def play_action(appwin):
    return appwin.play_actions.play


@pytest.fixture
def play_button(appwin, play_action):
    return appwin.pb_ctrls_middle_toolbar.widgetForAction(play_action)


@pytest.fixture
def listplayer(appwin):
    return appwin.playlist_widget.listplayer


@pytest.fixture
def playlist_view(appwin):
    return appwin.playlist_widget.view
