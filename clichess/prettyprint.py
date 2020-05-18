from colorama import Fore, Back, Style

BOARD_SIZE = 8


# Given square position and color perspective, return curses color code
def print_square(x, y, piece, is_white):
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
def print_board(board, is_white):
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
                print_square(x, y, "\u2007", is_white)
            else:
                print_square(x, y, board_string[y * BOARD_SIZE + x], is_white)


def print_challenge(index, challenge):
    idx = (f"[{index}]").ljust(4)
    # No idea what char limit is. Hope 20 is enough
    destUser = challenge["challenger"]["name"].ljust(20)
    # IDs seem to be 12 characters long, but add some extra just in case
    challenge_id = challenge["id"].ljust(14)
    variant = challenge["variant"]["name"].ljust(10)
    rated = "Yes  " if challenge["rated"] else "No   "
    color = challenge["color"].ljust(6)
    perf = challenge["perf"]["name"].ljust(10)
    print(f"{idx} {challenge_id} {destUser} {variant} {rated} {color} {perf}")


def print_challenges(challenges):
    # Pretty print titles
    print(" " * 5 + "ID" + " " * 13 + "Challenger" + " " * 11
          + "Variant" + " " * 4 + "Rated Color  Perf")
    for index, challenge in enumerate(challenges):
        print_challenge(index, challenge)


def print_game(index, game):
    # game variable should be "gameFull" type, first line in stream
    # Max 999 games. Definitely overkill
    idx = (f"[{index}]").ljust(5)
    game_id = game["id"].ljust(14)
    variant = game["variant"]["name"].ljust(10)
    rated = "Yes  " if game["rated"] else "No   "
    white = game["white"]["name"].ljust(20)
    black = game["black"]["name"].ljust(20)
    perf = game["perf"]["name"]
    print(f"{idx} {game_id} {white} {black} {variant} {rated} {perf}")


def print_games(games):
    print(" " * 6 + "ID" + " " * 13 + "White" + " " * 16 + "Black" + " " * 16
          + "Variant" + " " * 4 + "Rated Perf")
    for index, game in enumerate(games):
        print_game(index, game)
