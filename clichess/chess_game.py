import chess
from datetime import datetime, timedelta


class ChessGame:
    def __init__(self, player_name, game_data, date):
        self.game_data = game_data
        self.game_id = game_data["id"]
        # Add clock later
        self.update_time = date

        self.white = game_data["white"]["name"]
        self.black = game_data["black"]["name"]
        self.moves = game_data["state"]["moves"].split(' ')
        self.board = chess.Board()

        if self.moves[0] != '':
            for move in self.moves:
                self.board.push_uci(move)
            assert self.board.is_valid()
        else:
            self.moves = []

        if player_name.lower() == self.white.lower():
            self.is_white = True
        else:
            self.is_white = False

    def is_player_move(self):
        return self.is_white == self.board.turn

    def move_player(self, move_str):
        move = None
        try:
            move = self.board.parse_san(move_str)
        except ValueError:
            try:
                move = self.board.parse_uci(move_str)
            except ValueError:
                print("Illegal move")
                return None

        self.board.push_uci(move.uci())
        self.moves.append(move.uci())
        return move.uci()

    def update_game(self, game_data, date):
        assert game_data['type'] == 'gameState'
        new_moves = game_data["moves"].split(' ')
        if new_moves[0] == '':
            new_moves = []

        for i in range(len(self.moves), len(new_moves)):
            self.board.push_uci(new_moves[i])
        self.moves = new_moves
        self.game_data['state'] = game_data
        self.update_time = date

    def get_clock(self):
        white_turn = self.board.turn
        diff = datetime.utcnow() - self.update_time
        white_time = timedelta(milliseconds=self.game_data['state']['wtime'])
        black_time = timedelta(milliseconds=self.game_data['state']['btime'])
        zero = timedelta(0)
        if white_turn:
            white_time -= diff
            if white_time < zero:
                white_time = zero
        else:
            black_time -= diff
            if black_time < zero:
                black_time = zero
        return (white_time, black_time)

    def print_clock(self):
        white_time, black_time = self.get_clock()
        print(self.white + " " + self.black)
        print(str(white_time) + " " + str(black_time))