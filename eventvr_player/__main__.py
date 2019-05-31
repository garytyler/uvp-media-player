import sys


def main():
    from eventvr_player import viewer

    viewer.play(media_path=sys.argv[1], socket_url=sys.argv[2])


if __name__ == "__main__":
    main()
