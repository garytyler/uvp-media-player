from pathlib import Path

import pytest

from build import add_to_path, get_ffprobe_binary_path


def pytest_configure():
    add_to_path(get_ffprobe_binary_path().parent.resolve())


@pytest.fixture
def context():
    import app.__main__

    yield app.__main__.AppContext()


@pytest.fixture
def app(context):
    yield context.app


@pytest.fixture
def main_win(qtbot, context):
    qtbot.addWidget(context.main_win)
    context.main_win.show()
    qtbot.waitUntil(lambda: context.main_win.isVisible())
    yield context.main_win


@pytest.fixture
def rootdir(pytestconfig):
    return Path(pytestconfig.rootdir)


@pytest.fixture
def media_dir(rootdir):
    return rootdir / "media"
