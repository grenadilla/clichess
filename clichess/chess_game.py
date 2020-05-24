import chess


class ChessGame:
    def __init__(self, player_name, game_data):
        self.game_data = game_data
        self.game_id = game_data["id"]
        # Add clock later

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

    def move_player(self, move):
        # TODO check move is legal
        self.board.push_san(move)

    def move_opponent(self, move):
        self.board.push_uci(move)
