import os
import vlc

SAMPLE_MEDIA = {
    name: os.path.abspath(name)
    for name in os.listdir(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
    )
}


i = vlc.Instance()
p = i.media_player_new()
p.set_mrl(SAMPLE_MEDIA["360video_5sec.mp4"])
p.autoplay()
