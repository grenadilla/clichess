from threading import Thread
from queue import Queue
import asyncio
import json
from lichess_client import APIClient
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
        '''for event in self.client.board.stream_incoming_events():
            if event["type"] == "challenge":
                self.challenges.put(event["challenge"])
            elif event["type"] == "gameStart":
                for event in self.client.board.stream_game_state(
                        event["game"]["id"]):
                    if event["type"] == "gameFull":
                        self.games.put(event)
                        break'''
        self.loop.run_until_complete(self.stream_data())
    
    async def stream_data(self):
        await asyncio.gather(self.stream_events(), self.stream_game("e0rDmdnhY07Q"))

    async def stream_game(self, id):
        async for response in self.async_client.boards.stream_game_state(game_id=id):
            print(json.loads(response.entity.content))
            
        
    async def stream_events(self):
        async for response in self.async_client.boards.stream_incoming_events():
            print(json.loads(response.entity.content))
            

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
