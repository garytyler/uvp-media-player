import socketio

sio = socketio.Client()


@sio.on("forward_orientation")
def receive_orientation(data):
    print(data)


def connect(host="localhost", port="5000"):
    sio.connect(f"http://{host}:{port}")
