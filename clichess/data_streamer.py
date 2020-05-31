from threading import Thread
from queue import Queue
import asyncio
import json
from config import Config
from datetime import datetime

def decode_datetime_bits(response):
    date_str = response.metadata.timestamp.decode("utf-8")
    return datetime.strptime(date_str, "%a, %d %b %Y %X %Z")

class DataStreamer(Thread):
    def __init__(self, client, loop):
        super(DataStreamer, self).__init__()

        self.client = client
        self.loop = loop
        asyncio.set_event_loop(self.loop)

        # Use queue for thread safe
        self.challenges = Queue()
        self.games = Queue()
        self.updates = Queue()

    def run(self):
        self.loop.run_until_complete(self.stream_events())

    async def stream_game(self, id):
        # Remember asyncio.gather to run functions concurrently
        async for response in self.client.boards.stream_game_state(game_id=id):
            message = json.loads(response.entity.content)
            date = decode_datetime_bits(response)
            if message['type'] == 'gameFull':
                # Send tuple of (message, date)
                self.games.put((message, date))
                stream_game_id = message['id']
            else:
                # Send tuple of (game_id, message, date) as update
                self.updates.put((stream_game_id, message, date))
        
    async def stream_events(self):
        async for response in self.client.boards.stream_incoming_events():
            event = json.loads(response.entity.content)
            if event['type'] == 'gameStart':
                asyncio.ensure_future(self.stream_game(event['game']['id']))
            elif event['type'] == 'challenge':
                self.challenges.put(event['challenge'])

    def delete_challenge(self, challenge_id):
        # Delete a challenge from the queue given an ID
        # Use None as a sentinel value
        self.challenges.put(None)
        while True:
            challenge = self.challenges.get()
            if challenge is None:
                break
            if challenge["id"] != challenge_id:
                self.challenges.put(challenge)