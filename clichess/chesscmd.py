import cmd
import chess
import berserk
import colorama
from prettyprint import print_board
from config import Config


class ChessCmd(cmd.Cmd):
    prompt = "(clichess) "
    intro = "Welcome! Type help or ? for a list of commands."

    def __init__(self, board):
        super(ChessCmd, self).__init__()
        self.session = berserk.TokenSession(Config.API_TOKEN)
        self.client = berserk.Client(self.session)
        self.board = board

    def do_board(self, inp):
        print_board(self.board, True)

    def do_challenge(self, inp):
        challenge = self.client.challenges.create(username=inp, rated=False)
        print(challenge)

    def do_game(self, inp):
        game = self.client.games.export(game_id=inp)
        print(game)

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
