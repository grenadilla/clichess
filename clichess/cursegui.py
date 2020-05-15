import curses
import chess

# Chess boards are 8 x 8
BOARD_SIZE = 8

COLOR_LIGHT = 8
COLOR_DARK = 9
WHITE_ON_LIGHT = 10
WHITE_ON_DARK = 11
BLACK_ON_LIGHT = 12
BLACK_ON_DARK = 13


def set_colors():
    if curses.can_change_color():
        # Light
        curses.init_color(COLOR_LIGHT, 240, 217, 181)
        # Dark
        curses.init_color(COLOR_DARK, 181, 136, 99)
        # White on light
        curses.init_pair(WHITE_ON_LIGHT, curses.COLOR_WHITE, COLOR_LIGHT)
        # White on dark
        curses.init_pair(WHITE_ON_DARK, curses.COLOR_WHITE, COLOR_DARK)
        # Black on light
        curses.init_pair(BLACK_ON_LIGHT, curses.COLOR_BLACK, COLOR_LIGHT)
        # Black on dark
        curses.init_pair(BLACK_ON_DARK, curses.COLOR_BLACK, COLOR_DARK)
    else:
        # White on light
        curses.init_pair(WHITE_ON_LIGHT, curses.COLOR_WHITE,
                         curses.COLOR_YELLOW)
        # White on dark
        curses.init_pair(WHITE_ON_DARK, curses.COLOR_WHITE, curses.COLOR_GREEN)
        # Black on light
        curses.init_pair(BLACK_ON_LIGHT, curses.COLOR_BLACK,
                         curses.COLOR_YELLOW)
        # Black on dark
        curses.init_pair(BLACK_ON_DARK, curses.COLOR_BLACK, curses.COLOR_GREEN)


# Given square position and color perspective, return curses color code
def get_square_color(x, y, is_white):
    square_white = (x + y) % 2 == 1
    if is_white:
        if square_white:
            return curses.color_pair(WHITE_ON_LIGHT)
        return curses.color_pair(WHITE_ON_DARK)
    if square_white:
        return curses.color_pair(BLACK_ON_LIGHT)
    return curses.color_pair(BLACK_ON_DARK)


# Prints a chess board with top left corner at (start_x, start_y)
# Flips the board if the player !is_white
def print_board(window, board, start_x, start_y, is_white):
    empty = 'O'
    board_string = board.unicode(invert_color=is_white, empty_square=empty)
    board_string = board_string.replace(' ', '')
    board_string = board_string.replace('\n', '')
    for y in range(0, BOARD_SIZE):
        for x in range(0, BOARD_SIZE):
            # times two since returns string with space between pieces
            # plus 1 from newline character
            if board_string[y * BOARD_SIZE + x] == empty:
                window.addstr(start_y + y, start_x + x, ' ',
                              get_square_color(x, y, is_white))
            else:
                window.addstr(start_y + y,
                              start_x + x,
                              board_string[y * BOARD_SIZE + x],
                              get_square_color(x, y, is_white))


def main(stdscr):
    stdscr.clear()
    set_colors()

    board = chess.Board()
    print_board(stdscr, board, 0, 0, True)

    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    curses.wrapper(main)
