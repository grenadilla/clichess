from threading import Thread
from queue import Queue
import asyncio
import json
from config import Config

class DataStreamer(Thread):
    def __init__(self, client, loop, async_client):
        super(DataStreamer, self).__init__()
        self.client = client

        # Use queue for thread safe
        self.challenges = Queue()
        self.games = Queue()

        self.loop = loop
        self.async_client = async_client
        asyncio.set_event_loop(self.loop)

    def run(self):
        self.loop.run_until_complete(self.stream_events())

    async def stream_game(self, id):
        # Remember asyncio.gather to run functions concurrently
        async for response in self.async_client.boards.stream_game_state(game_id=id):
            data = json.loads(response.entity.content)
            print(data)
            
        
    async def stream_events(self):
        async for response in self.async_client.boards.stream_incoming_events():
            data = json.loads(response.entity.content)
            print(data)
            if data['type'] == 'gameStart':
                asyncio.ensure_future(self.stream_game(data['game']['id']))
            

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

    def get_game(self, game_id):
        for event in self.client.board.stream_game_state(game_id):
            if event["type"] == "gameFull":
                return event
