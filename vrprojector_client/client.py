import sys
import socketio

sio = socketio.Client()


@sio.on("forward_orientation")
def receive_orientation(data):
    print(data)


if __name__ == "__main__":
    sio.connect("http://localhost:5000")
