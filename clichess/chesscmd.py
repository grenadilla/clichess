import cmd
import berserk
import colorama
import prettyprint
from config import Config
from data_streamer import DataStreamer
from chess_game import ChessGame


class ChessCmd(cmd.Cmd):
    def __init__(self):
        super(ChessCmd, self).__init__()

        print("Logging in...")

        # Set prompt and intro
        self.prompt = "(clichess) "
        self.intro = "Welcome! Type help or ? for a list of commands."

        # Login
        self.session = berserk.TokenSession(Config.API_TOKEN)
        self.client = berserk.Client(self.session)
        self.account = self.client.account.get()
        self.username = self.account['username']

        # Set up data
        self.data_streamer = DataStreamer(self.client)
        self.data_streamer.setDaemon(True)
        self.data_streamer.start()
        self.challenges = []
        self.games = []

        # Current game viewing
        self.game = None
        self.game_data = None
        self.board = None

    def do_account(self, args):
        # TODO add pretty printing
        print(self.account)

    def do_board(self, args):
        '''Updates the game and prints the board'''
        if self.game is None:
            print("Select a game")
            return
        self.game.update_game(self.data_streamer.get_game(self.game.game_id))
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
                if not self.client.board.make_move(self.game.game_id, move):
                    print("There was an error making your move")

    def do_draw(self, args):
        '''Offer a draw in a game'''
        if self.game is None:
            print("Select a game")
            return
        if not self.client.board.offer_draw(self.game.game_id):
            print("There was an error while offering a draw")

    def do_challenge(self, args):
        args = args.split(' ')
        username = args.pop(0)
        rated = False
        color = None
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
                    color = 'white'
                elif arg[1] == 'black':
                    color = 'black'
                elif arg[1] == 'random':
                    color = None
                else:
                    print("Please specify a color: white, black, or random")
                    return
            
        self.client.challenges.create(username=username, rated=rated, days=days, color=color)

    def do_game(self, args):
        '''Choose a game to play'''
        if args == "":
            print("Choose a game")
        else:
            game_id = None
            if args.isnumeric():
                index = int(args)
                if index >= len(self.games):
                    print("Index out of bounds")
                else:
                    game_id = self.games[index]["id"]
            elif any(d["id"] == args for d in self.games):
                game_id = args
            else:
                print("Invalid game ID")
            if game_id is not None:
                self.game = ChessGame(self.username,
                                      self.data_streamer.get_game(game_id))
                self.prompt = f"(clichess/{self.game.game_id}) "

    def do_challenges(self, args):
        '''Refresh the list of challenges, then list all challenges'''
        # Get all challenges from queue and convert to local copy
        # to deal with thread issues
        self.challenges = list(self.data_streamer.challenges.queue)
        prettyprint.print_challenges(self.challenges)

    def do_accept(self, args):
        '''Accept a challenge, either by index or challenge ID'''
        if args == "":
            print("Choose a challenge to accept")
        else:
            challenge_id = None
            if args.isnumeric():
                index = int(args)
                if index >= len(self.games):
                    print("Index out of bounds")
                else:
                    challenge_id = self.challenges[index]["id"]
            # Maybe rewrite this; might be inneficient to keep generating
            elif any(d["id"] == args for d in self.challenges):
                challenge_id = args
            else:
                print("Invalid challenge ID")
            if challenge_id is not None:
                if self.client.challenges.accept(challenge_id):
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
                if index >= len(self.games):
                    print("Index out of bounds")
                else:
                    challenge_id = self.challenges[index]["id"]
            # Maybe rewrite this; might be inneficient to keep generating
            elif any(d["id"] == args for d in self.challenges):
                challenge_id = args
            else:
                print("Invalid challenge ID")
            if challenge_id is not None:
                if self.client.challenges.decline(challenge_id):
                    self.data_streamer.delete_challenge(challenge_id)
                else:
                    print("There was an error declining this challenge")

    def do_games(self, args):
        '''Refresh the list of games, then list all games'''
        self.games = list(self.data_streamer.games.queue)
        prettyprint.print_games(self.games)

    def do_exit(self, args):
        '''Exit the application'''
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    colorama.init()
    shell = ChessCmd()
    shell.cmdloop()
    colorama.deinit()
