from threading import Thread
from queue import Queue


class DataStreamer(Thread):
    def __init__(self, client):
        super(DataStreamer, self).__init__()
        self.client = client

        # Use queue for thread safe
        self.challenges = Queue()
        self.games = Queue()

    def run(self):
        for event in self.client.board.stream_incoming_events():
            if event["type"] == "challenge":
                self.challenges.put(event["challenge"])
            elif event["type"] == "gameStart":
                for event in self.client.board.stream_game_state(
                        event["game"]["id"]):
                    if event["type"] == "gameFull":
                        self.games.put(event)
                        break
