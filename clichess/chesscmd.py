import cmd
import colorama
import prettyprint
import asyncio
import json
from config import Config
from data_streamer import DataStreamer
from chess_game import ChessGame
from lichess_client import APIClient
from lichess_client.utils import enums
from collections import OrderedDict


class ChessCmd(cmd.Cmd):
    def __init__(self):
        super(ChessCmd, self).__init__()

        print("Logging in...")

        # Set up login and async
        self.loop = asyncio.new_event_loop()
        self.client = APIClient(token=Config.API_TOKEN, loop=self.loop)
        self.data_streamer = DataStreamer(self.client, self.loop)
        self.data_streamer.setDaemon(True)
        self.data_streamer.start()

        self.challenges = []
        self.games = OrderedDict()
        self.game = None

        # Set prompt and intro
        self.prompt = "(clichess) "
        self.intro = "Welcome! Type help or ? for a list of commands."

        # Get account
        task = asyncio.run_coroutine_threadsafe(
                self.client.account.get_my_profile(), self.loop)
        if task.result().entity.status != enums.StatusTypes.SUCCESS:
            print("There was an error fetching your account data")
            self.account = None
            self.username = None
        else:
            self.account = task.result().entity.content
            self.username = self.account['username']

    def precmd(self, line):
        # Maybe change later for better way to take things out of queue
        # Think about using try except
        while not self.data_streamer.challenges.empty():
            challenge = self.data_streamer.challenges.get()
            self.challenges.append(challenge)
        while not self.data_streamer.games.empty():
            new_game = self.data_streamer.games.get()
            self.games[new_game['id']] = ChessGame(self.username, new_game)
        while not self.data_streamer.updates.empty():
            # update is tuple of (game_id, message)
            update = self.data_streamer.updates.get()
            if update[1]['type'] == 'gameState':
                self.games[update[0]].update_game(update[1])
        return line

    def do_account(self, args):
        if self.account is None:
            task = asyncio.run_coroutine_threadsafe(
                self.client.account.get_my_profile(), self.loop)
            if task.result().entity.status != enums.StatusTypes.SUCCESS:
                print("There was an error fetching your account data")
            else:
                self.account = task.result().entity.content
                self.username = self.account['username']
        else:
            # TODO add pretty printing
            print(self.account)

    def do_board(self, args):
        '''Prints the board of the currently selected game'''
        if self.game is None:
            print("Select a game")
            return
        prettyprint.print_board(self.game.board, self.game.is_white)
        if self.game.is_player_move():
            print("It is your turn")
        else:
            print("Waiting for opponent to move")

    def do_move(self, args):
        '''Make a move in a game using SAN or UCI format, case sensitive'''
        if self.game is None:
            print("Select a game")
            return
        if not self.game.is_player_move():
            print("It is not your move")
        else:
            move = self.game.move_player(args)
            if move is not None:
                task = asyncio.run_coroutine_threadsafe(
                    self.client.boards.make_move(game_id=self.game.game_id, move=move), self.loop) 
                if task.result().entity.status != enums.StatusTypes.SUCCESS:
                    print("There was an error making your move")
                    print(task.result())
                
    def do_draw(self, args):
        '''Offer a draw in a game'''
        if self.game is None:
            print("Select a game")
            return
        task = asyncio.run_coroutine_threadsafe(
                    self.client.boards.handle_draw(game_id=self.game.game_id, accept=True), self.loop)
        if task.result().entity.status != enums.StatusTypes.SUCCESS:
            print("There was an error while offering a draw")

    def do_challenge(self, args):
        args = args.split(' ')
        username = args.pop(0)
        rated = False
        color = enums.ColorType.RANDOM
        days = None
        for arg in args:
            arg = arg.lower()
            arg = arg.split('=')
            if arg[0] == 'rated':
                rated = True
            elif arg[0] == 'days':
                if len(arg) < 2 or not arg[1].isnumeric():
                    print("Please specify the number of days as a whole number")
                    return
                days = int(arg[1])
                if days < 1 or days > 14:
                    print("Days must be between 1 and 14 inclusive")
                    return
            elif arg[0] == 'color':
                if len(arg) < 2:
                    print("Please specify a color: white, black, or random")
                    return
                if arg[1] == 'white':
                    color = enums.ColorType.WHITE
                elif arg[1] == 'black':
                    color = enums.ColorType.BLACK
                elif arg[1] == 'random':
                    color = enums.ColorType.RANDOM
                else:
                    print("Please specify a color: white, black, or random")
                    return

        task = asyncio.run_coroutine_threadsafe(
                self.client.challenges.create(username=username,
                                                    rated=rated,
                                                    days=days,
                                                    color=color), self.loop)

        if task.result().entity.status != enums.StatusTypes.SUCCESS:
            print("There was an error while creating this challenge")
            print(task.result())

    def do_game(self, args):
        '''Choose a game to play'''
        if args == "":
            print("Choose a game")
        else:
            if args.isnumeric():
                index = int(args)
                if index >= len(self.games):
                    print("Index out of bounds")
                    return
                else:
                    self.game = list(self.games.values())[index]
                    self.prompt = f"(clichess/{self.game.game_id}) "
                    return
            elif args in self.games:
                self.game = self.games[args]
                self.prompt = f"(clichess/{self.game.game_id}) "
            else:
                print("Invalid game ID")

    def do_challenges(self, args):
        '''List all incoming challenges'''
        prettyprint.print_challenges(self.challenges)

    def do_accept(self, args):
        '''Accept a challenge, either by index or challenge ID'''
        if args == "":
            print("Choose a challenge to accept")
        else:
            challenge_id = None
            if args.isnumeric():
                index = int(args)
                if index >= len(self.challenges):
                    print("Index out of bounds")
                else:
                    challenge_id = self.challenges[index]["id"]
            # Maybe rewrite this; might be inneficient to keep generating
            elif any(d["id"] == args for d in self.challenges):
                challenge_id = args
            else:
                print("Invalid challenge ID")
            if challenge_id is not None:
                task = asyncio.run_coroutine_threadsafe(
                    self.client.challenges.accept(challenge_id=challenge_id), self.loop)
                if task.result().entity.status == enums.StatusTypes.SUCCESS:
                    self.data_streamer.delete_challenge(challenge_id)
                else:
                    print("There was an error accepting this challenge")

    def do_decline(self, args):
        '''Decline a challenge, either by index or challenge ID'''
        if args == "":
            print("Choose a challenge to decline")
        else:
            challenge_id = None
            if args.isnumeric():
                index = int(args)
                if index >= len(self.challenges):
                    print("Index out of bounds")
                else:
                    challenge_id = self.challenges[index]["id"]
            # Maybe rewrite this; might be inneficient to keep generating
            elif any(d["id"] == args for d in self.challenges):
                challenge_id = args
            else:
                print("Invalid challenge ID")
            if challenge_id is not None:
                task = asyncio.run_coroutine_threadsafe(self.client.challenges.decline(challenge_id=challenge_id), self.loop)
                if task.result().entity.status == enums.StatusTypes.SUCCESS:
                    self.data_streamer.delete_challenge(challenge_id)
                else:
                    print("There was an error declining this challenge")

    def do_games(self, args):
        '''List all ongoing games'''
        prettyprint.print_games(list(self.games.values()))

    def do_exit(self, args):
        '''Exit the application'''
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    colorama.init()
    shell = ChessCmd()
    shell.cmdloop()
    colorama.deinit()
