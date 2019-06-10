from vlc import Event


class TestListSignals:
    def __init__(self, list_events):
        self.list_events = list_events
        self.list_events.next_item_set.connect(self.on_next_item_set)
        self.list_events.stopped.connect(self.on_stopped)
        self.list_events.played.connect(self.on_played)

    def on_next_item_set(self, e: Event):
        self.log_event_call(e)

    def on_played(self, e: Event):
        self.log_event_call(e)

    def on_stopped(self, e: Event):
        self.log_event_call(e)
