import cmd
import chess
import berserk
import colorama
from prettyprint import print_board
from config import Config
from data_streamer import DataStreamer


class ChessCmd(cmd.Cmd):
    prompt = "(clichess) "
    intro = "Welcome! Type help or ? for a list of commands."

    def __init__(self, board):
        super(ChessCmd, self).__init__()
        self.session = berserk.TokenSession(Config.API_TOKEN)
        self.client = berserk.Client(self.session)
        self.board = board
        self.data_streamer = DataStreamer(self.client)
        self.data_streamer.setDaemon(True)
        self.data_streamer.start()
        self.challenges = []

    def do_board(self, inp):
        print_board(self.board, True)

    def do_challenge(self, inp):
        challenge = self.client.challenges.create(username=inp, rated=False)
        print(challenge)

    def do_game(self, inp):
        game = self.client.games.export(game_id=inp)
        print(game)

    def do_challenges(self, inp):
        # Get all challenges from queue and convert to local copy
        # to deal with thread issues
        self.challenges = list(self.data_streamer.challenges.queue)
        for challenge in self.challenges:
            print(challenge["id"])

    def do_exit(self, inp):
        '''Exit the application'''
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    colorama.init()
    board = chess.Board()
    shell = ChessCmd(board)
    shell.cmdloop()
    colorama.deinit()
