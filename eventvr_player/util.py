def get_media_fps(vlc_media) -> float:
    if not vlc_media:
        return None
    if not vlc_media.is_parsed():
        vlc_media.parse()
    track = [t for t in vlc_media.tracks_get()][0]
    return track.video.contents.frame_rate_num
