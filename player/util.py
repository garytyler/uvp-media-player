def get_media_fps(vlc_media) -> float:
    if not vlc_media:
        return None
    if not vlc_media.is_parsed():
        vlc_media.parse()
    track = [t for t in vlc_media.tracks_get()][0]
    return track.video.contents.frame_rate_num


def get_media_size(vlc_media):
    if not vlc_media.is_parsed():
        vlc_media.parse()
    media_tracks = vlc_media.tracks_get()
    if not media_tracks:  # Possibly not necessary. Does all media have a track?
        return None
    track = [t for t in media_tracks][0]
    return track.video.contents.width, track.video.contents.height


def rotate_list(l, n):
    l[:] = l[n:] + l[:n]


def positive_threshold(value: int):
    return value if value > 0 else 0
