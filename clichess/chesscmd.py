import cmd
import chess
import colorama
from colorama import Fore, Back, Style

BOARD_SIZE = 8


class ChessCmd(cmd.Cmd):
    prompt = "(clichess) "
    intro = "Welcome! Type help or ? for a list of commands."

    def __init__(self, board):
        super(ChessCmd, self).__init__()
        colorama.init()
        self.board = board

    # Given square position and color perspective, return curses color code
    def print_square(self, x, y, piece, is_white):
        square_white = (x + y) % 2 == 0
        if square_white:
            # White on light
            print(Fore.BLACK + Back.WHITE + '\u2007' + piece + '\u2007',
                  end="")
        else:
            # White on dark
            print(Fore.BLACK + Back.MAGENTA + '\u2007' + piece + '\u2007',
                  end="")
        if x == 7:
            print(Style.RESET_ALL)

    # Prints a chess board with top left corner at (start_x, start_y)
    # Flips the board if the player !is_white
    def print_board(self, board, is_white):
        empty = 'O'
        invert = not is_white
        board_string = board.unicode(invert_color=invert, empty_square=empty)
        board_string = board_string.replace(' ', '')
        board_string = board_string.replace('\n', '')
        for y in range(0, BOARD_SIZE):
            for x in range(0, BOARD_SIZE):
                # times two since returns string with space between pieces
                # plus 1 from newline character
                if board_string[y * BOARD_SIZE + x] == empty:
                    # \u2007 is a space character
                    self.print_square(x, y, "\u2007", is_white)
                else:
                    self.print_square(x, y, board_string[y * BOARD_SIZE + x],
                                      is_white)

    def do_board(self, inp):
        self.print_board(self.board, True)

    def do_exit(self, inp):
        '''Exit the application'''
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    board = chess.Board()
    shell = ChessCmd(board)
    shell.cmdloop()
