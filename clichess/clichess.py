import requests, berserk
from config import Config

eventurl = "https://lichess.org/api/stream/event"


def stream():
    session = berserk.TokenSession(Config.API_TOKEN)
    client = berserk.Client(session)
    for event in client.board.stream_incoming_events():
        print(event)


if __name__ == '__main__':
    stream()
