import berserk
import colorama
from colorama import Fore, Back, Style
import chess
from config import Config

# Lichess board colors:
# Light: #F0D9B5
# Dark: #B58863


# Chess boards are 8 x 8
BOARD_SIZE = 8

eventurl = "https://lichess.org/api/stream/event"


def stream():
    session = berserk.TokenSession(Config.API_TOKEN)
    client = berserk.Client(session)
    for event in client.board.stream_incoming_events():
        print(event)


# Given square position and color perspective, return curses color code
def print_square(x, y, piece, is_white):
    square_white = (x + y) % 2 == 1
    if square_white:
        # White on light
        print(Fore.BLACK + Back.WHITE + piece, end="")
    else:
        # White on dark
        print(Fore.BLACK + Back.MAGENTA + piece, end="")
    if x == 7:
        print(Style.RESET_ALL)


# Prints a chess board with top left corner at (start_x, start_y)
# Flips the board if the player !is_white
def print_board(board, is_white):
    empty = 'O'
    board_string = board.unicode(invert_color=is_white, empty_square=empty)
    board_string = board_string.replace(' ', '')
    board_string = board_string.replace('\n', '')
    for y in range(0, BOARD_SIZE):
        for x in range(0, BOARD_SIZE):
            # times two since returns string with space between pieces
            # plus 1 from newline character
            if board_string[y * BOARD_SIZE + x] == empty:
                print_square(x, y, '\u2007', is_white)
            else:
                print_square(x, y, board_string[y * BOARD_SIZE + x], is_white)


if __name__ == '__main__':
    colorama.init()
    board = chess.Board()
    print_board(board, True)
    print(Style.RESET_ALL)
