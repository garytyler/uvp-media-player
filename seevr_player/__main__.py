import os
from seevr_player import viewer


# def main():
#     MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
#     SAMPLE_MEDIA = {
#         name: os.path.join(MEDIA_DIR, name) for name in os.listdir(MEDIA_DIR)
#     }

#     path = SAMPLE_MEDIA["360video_2min.mp4"]
#     # url = "wss://seevr.herokuapp.com/player"
#     url = "ws://127.0.0.1:8000/example/player"


if __name__ == "__main__":
    # main()
    viewer.play()
