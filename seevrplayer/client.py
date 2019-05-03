import socketio


_latest_orientation_data = None


def get_latest_orientation_data():
    """Return most recently published orientation data"""
    return _latest_orientation_data


sio = socketio.Client()


@sio.on("forward_orientation")
def receive_orientation(data):
    """Publish orientation data to a module variable"""
    global _latest_orientation_data
    _latest_orientation_data = data


def connect(host="localhost", port="5000"):
    sio.connect(f"http://{host}:{port}")
