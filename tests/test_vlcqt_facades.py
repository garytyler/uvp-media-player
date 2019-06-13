from eventvr_player.vlc_facades import Instance, MediaListPlayer, MediaPlayer


def instance_is_singleton():
    instance = Instance()
    assert instance == Instance() == Instance()


def test_implicit_instances():
    instance = Instance()
    media_list_player = MediaListPlayer()
    media_player = MediaPlayer()
    assert instance == media_list_player.get_instance()
    assert instance == media_player.get_instance()
