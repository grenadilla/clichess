from colorama import Fore, Back, Style
from datetime import timedelta

BOARD_SIZE = 8


# Given square position and color perspective, return curses color code
def print_square(x, y, piece, is_white):
    square_white = (x + y) % 2 == 0
    # Note that \u2007 is a space and \ufe0f makes characters double width
    if square_white:
        # White on light
        print(Fore.BLACK + Back.WHITE + '\u2007' + piece + '\ufe0f' + '\u2007',
              end="")
    else:
        # White on dark
        print(Fore.BLACK + Back.MAGENTA + '\u2007' + piece + '\ufe0f'
              + '\u2007', end="")
    if x == 7:
        print(Style.RESET_ALL, end="")


# Flips the board if the player !is_white
def print_board(board, is_white):
    empty = 'O'
    board_string = board.unicode(empty_square=empty)
    if not is_white:
        # Reverse the board string
        board_string = board_string[::-1]
    board_string = board_string.replace(' ', '')
    board_string = board_string.replace('\n', '')

    # Print letters on top
    if is_white:
        print("\u2009" + ("ABCDEFGH").replace("", "\ufe0f\u2007\u2007")[1:-1])
    else:
        print("\u2009" + ("HGFEDCBA").replace("", "\ufe0f\u2007\u2007")[1:-1])

    for y in range(0, BOARD_SIZE):
        # Print numbers on left side
        if is_white:
            print(str(8 - y) + '\u2009', end="")
        else:
            print(str(y + 1) + '\u2009', end="")
        for x in range(0, BOARD_SIZE):
            # times two since returns string with space between pieces
            # plus 1 from newline character
            if board_string[y * BOARD_SIZE + x] == empty:
                # \u2007 is a space character
                print_square(x, y, "\u2007", is_white)
            else:
                print_square(x, y, board_string[y * BOARD_SIZE + x], is_white)
        # Print numbers on right side
        if is_white:
            print('\u2009' + str(8 - y))
        else:
            print('\u2009' + str(y + 1))

    # Print letters on bottom
    if is_white:
        print("\u2009" + ("ABCDEFGH").replace("", "\ufe0f\u2007\u2007")[1:-1])
    else:
        print("\u2009" + ("HGFEDCBA").replace("", "\ufe0f\u2007\u2007")[1:-1])


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
    for index, challenge in enumerate(challenges.values()):
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
        print_game(index, game.game_data)

def print_account(account):
    print(account['username'])
    bullet_string = ("Bullet" + " " * 9 +
                    str(account['perfs']['bullet']['rating']).ljust(4) + 
                    "   " + str(account['perfs']['bullet']['games']).ljust(5))
    blitz_string = ('Blitz' + " " * 10 +
                    str(account['perfs']['blitz']['rating']).ljust(4) + 
                    "   " + str(account['perfs']['blitz']['games']).ljust(5))
    rapid_string = ('Rapid' + " " * 10 +
                    str(account['perfs']['rapid']['rating']).ljust(4) + 
                    "   " + str(account['perfs']['rapid']['games']).ljust(5))
    classical_string = ('Classical' + " " * 6 +
                    str(account['perfs']['classical']['rating']).ljust(4) + 
                    "   " + str(account['perfs']['classical']['games']).ljust(5))
    correspondence_string = ('Correspondence ' +
                    str(account['perfs']['correspondence']['rating']).ljust(4) + 
                    "   " + str(account['perfs']['correspondence']['games']).ljust(5))
    print("-" * max((len(bullet_string), len(blitz_string), len(rapid_string), 
                    len(classical_string), len(correspondence_string))))
    print("Variant" + " " * 8 + "Rating Games")
    print(bullet_string)
    print(blitz_string)
    print(rapid_string)
    print(classical_string)
    print(correspondence_string)

def get_time(time):
    time_str = ""
    days = time.days
    hours = int(time.seconds / 3600)
    if days > 0:
        if days == 1:
            time_str += "1 day"
        else:
            time_str += f"{days} days"
        if hours == 1:
            time_str += ", 1 hour"
        elif hours > 1:
            time_str += f", {hours} hours"
    else:
        time_str = str(timedelta(seconds=time.seconds))
    return time_str

def print_clock(game):
    white_time, black_time = game.get_clock()
    print("White".ljust(20) + " " + "Black".ljust(20))
    print(game.white.ljust(20) + " " + game.black.ljust(20))
    print(get_time(white_time).ljust(20) + " " + get_time(black_time).ljust(20))

    state = game.game_data["state"]
    status = state["status"]

    if status == "started":
        if game.is_player_move():
            print("It is your turn")
        else:
            print("Waiting for your opponent to move")
    elif status == "aborted":
        print("This game was aborted")
    elif status == "mate":
        if (state["winner"] == "white"):
            print("Checkmate! White wins")
        else:
            print("Checkmate! Black wins")
    elif status == "resign":
        if (state["winner"] == "white"):
            print("Black has resigned. White wins!")
        else:
            print("White has resigned. Black wins!")
    elif status == "draw":
        print("The players have decided on a draw")
    elif status == "outoftime":
        if (state["winner"] == "white"):
            print("Black is out of time. White wins!")
        else:
            print("White is out of time. Black wins!")
