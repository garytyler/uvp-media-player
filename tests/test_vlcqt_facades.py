from src.vlcqt.vlc_facades import Instance, MediaPlayerFacade


def instance_is_singleton():
    instance = Instance()
    assert instance == Instance() == Instance()


def test_implicit_instances():
    instance = Instance()
    media_list_player = MediaPlayerFacade()
    media_player = MediaPlayerFacade()
    assert instance == media_list_player.get_instance()
    assert instance == media_player.get_instance()
