import cmd
import berserk
import colorama
from prettyprint import print_board, print_challenges, print_games
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

    def do_account(self, inp):
        # TODO add pretty printing
        print(self.account)

    def do_board(self, inp):
        '''Updates the game and prints the board'''
        if self.game is None:
            print("Select a game")
            return
        self.game.update_game(self.data_streamer.get_game(self.game.game_id))
        print_board(self.game.board, self.game.is_white)

    def do_move(self, inp):
        if self.game is None:
            print("Select a game")
            return
        if not self.game.is_player_move():
            print("It is not your move")
        elif self.game.move_player(inp):
            self.client.board.make_move(self.game.game_id, inp)

    def do_challenge(self, inp):
        challenge = self.client.challenges.create(username=inp, rated=False)
        print(challenge)

    def do_game(self, inp):
        '''Choose a game to play'''
        if inp == "":
            print("Choose a game")
        else:
            game_id = None
            if inp.isnumeric():
                index = int(inp)
                if index >= len(self.games):
                    print("Index out of bounds")
                else:
                    game_id = self.games[index]["id"]
            elif any(d["id"] == inp for d in self.games):
                game_id = inp
            else:
                print("Invalid game ID")
            if game_id is not None:
                self.game = ChessGame(self.username,
                                      self.data_streamer.get_game(game_id))
                self.prompt = f"(clichess/{self.game.game_id}) "

    def do_challenges(self, inp):
        '''Refresh the list of challenges, then list all challenges'''
        # Get all challenges from queue and convert to local copy
        # to deal with thread issues
        self.challenges = list(self.data_streamer.challenges.queue)
        print_challenges(self.challenges)

    def do_accept(self, inp):
        '''Accept a challenge, either by index or challenge ID'''
        if inp == "":
            print("Choose a challenge to accept")
        else:
            challenge_id = None
            if inp.isnumeric():
                index = int(inp)
                if index >= len(self.games):
                    print("Index out of bounds")
                else:
                    challenge_id = self.challenges[index]["id"]
            # Maybe rewrite this; might be inneficient to keep generating
            elif any(d["id"] == inp for d in self.challenges):
                challenge_id = inp
            else:
                print("Invalid challenge ID")
            if challenge_id is not None:
                if self.client.challenges.accept(challenge_id):
                    self.data_streamer.delete_challenge(challenge_id)
                else:
                    print("There was an error accepting this challenge")

    def do_games(self, inp):
        '''Refresh the list of games, then list all games'''
        self.games = list(self.data_streamer.games.queue)
        print_games(self.games)

    def do_exit(self, inp):
        '''Exit the application'''
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    colorama.init()
    shell = ChessCmd()
    shell.cmdloop()
    colorama.deinit()
