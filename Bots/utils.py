class Move:
    def __init__(self, start_pos, end_pos, is_promotion=False, captured_piece=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_promotion = is_promotion
        self.captured_piece = captured_piece
    
    def __eq__(self, other) : 
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Move(start={self.start_pos}, end={self.end_pos}, promotion={self.is_promotion}, captured_piece={self.captured_piece})"

    def get_return_move(self):
        return self.start_pos, self.end_pos


class Board:
    def __init__(self, board, board_color_top):
        self.board = board
        self.board_color_top = board_color_top
        self.color_to_play = board_color_top
        self.is_game_over = False
        self.piece_values = {
            'k': 8000.0,
            'q': 900.0,
            'r': 500.0,
            'b': 320.0,
            'n': 300.0,
            'p': 100.0
        }
        self.piece_encoding = {
            '': '0',
            'pw': '1', 'nw': '2', 'bw': '3', 'rw': '4', 'qw': '5', 'kw': '6',
            'pb': '7', 'nb': '8', 'bb': '9', 'rb': 'A', 'qb': 'B', 'kb': 'C'
        }
        self.board_key = self.generate_board_key()
        self.king_pos = self.get_king_positions()

    def generate_board_key(self):
        key = ""
        for row in self.board:
            for piece in row:
                key = self.piece_encoding.get(piece, '0') + key
        return int(key, 16)
    
    def get_king_positions(self):
        res = {}
        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] and self.board[x, y][0] == 'k':
                    res[self.board[x, y][1]] = (x,y)
                if len(res) == 2:
                    return res
        return res

    def is_in_check(self, color):
        king_pos = self.king_pos.get(color)
        if not king_pos:
            return False

        x, y = king_pos

        # Vérifier les menaces des pions
        if self.is_attacked_by_pawn(x, y, color):
            return True
        # Vérifier les menaces des cavaliers
        if self.is_attacked_by_knight(x, y, color):
            return True
        # Vérifier les menaces sur les lignes et colonnes (tours et dames)
        if self.is_attacked_on_line(x, y, color):
            return True
        # Vérifier les menaces sur les diagonales (fous et dames)
        if self.is_attacked_on_diagonal(x, y, color):
            return True
        return False
    
    def opposite_color(self, color):
        return 'w' if color == 'b' else 'b'

    def is_attacked_by_pawn(self, x, y, color):
        direction = -1 if color == self.board_color_top else 1
        enemy_pawn = 'p' + self.opposite_color(color)
       
        for dx, dy in [(-1, direction), (1, direction)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.shape[0] and 0 <= ny < self.board.shape[1]:
                if self.board[nx, ny] == enemy_pawn:
                    return True
        return False

    def is_attacked_by_knight(self, x, y, color):
        enemy_knight = 'n' + self.opposite_color(color)
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.shape[0] and 0 <= ny < self.board.shape[1]:
                if self.board[nx, ny] == enemy_knight:
                    return True
        return False

    def is_attacked_on_line(self, x, y, color):
        enemy_rook = 'r' + self.opposite_color(color)
        enemy_queen = 'q' + self.opposite_color(color)

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return self.is_attacked_in_directions(x, y, directions, [enemy_rook, enemy_queen])

    def is_attacked_on_diagonal(self, x, y, color):
        enemy_bishop = 'b' + self.opposite_color(color)
        enemy_queen = 'q' + self.opposite_color(color)

        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self.is_attacked_in_directions(x, y, directions, [enemy_bishop, enemy_queen])

    def is_attacked_in_directions(self, x, y, directions, attackers):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < self.board.shape[0] and 0 <= ny < self.board.shape[1]:
                piece = self.board[nx, ny]
                if piece:
                    if piece in attackers:
                        return True
                    break
                nx, ny = nx + dx, ny + dy
        return False
    
    def get_movements(self):
        res = []

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '' and self.board[x, y][-1] == self.color_to_play:
                    piece_moves = self.movement_piece(x, y)
                    for move in piece_moves:
                        res.append(move)
        return res

    def movement_piece(self, x, y):
        if self.board[x, y] == '':
            return []
        current_color = self.board[x, y][-1]

        def get_movement_pawn():
            res = []
            if x + 1 >= self.board.shape[0]:
                return res

            pawn_dir = 1
            if self.board_color_top != current_color:
                pawn_dir = -1

            new_x = x + pawn_dir
            is_promotion = False
            if new_x == 0 or new_x == self.board.shape[0] - 1:
                is_promotion = True
            for i in range(3):
                new_y = y + i - 1
                if 0 <= new_y < self.board.shape[1]:
                    if i == 1:
                        if self.board[new_x, new_y] == '':
                            res.append(Move((x, y), (new_x, new_y), is_promotion))
                    else:
                        if self.board[new_x, new_y] != '' and self.board[new_x, new_y][-1] != current_color:
                            res.append(Move((x, y), (new_x, new_y), is_promotion))
            return res

        def get_movement_rook():
            res = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dx, dy in directions:
                i = 1
                while True:
                    new_x = x + dx * i
                    new_y = y + dy * i

                    if 0 <= new_x < self.board.shape[0] and 0 <= new_y < self.board.shape[1]:
                        next_new_mov = self.board[new_x, new_y]
                        if next_new_mov == '':
                            res.append(Move((x, y), (new_x, new_y)))
                        elif next_new_mov[-1] != current_color:
                            res.append(Move((x, y), (new_x, new_y)))
                            break
                        else:
                            break
                    else:
                        break
                    i += 1
            return res

        def get_movement_knight():
            res = []
            moves = [
                (-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (1, -2), (-1, 2), (1, 2)
            ]

            for dx, dy in moves:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.board.shape[0] and 0 <= ny < self.board.shape[1]:
                    next_new_mov = self.board[nx, ny]
                    if next_new_mov == '' or next_new_mov[-1] != current_color:
                        res.append(Move((x, y), (nx, ny)))
            return res

        def get_movement_bishop():
            res = []
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for dx, dy in directions:
                i = 1
                while True:
                    new_x = x + dx * i
                    new_y = y + dy * i

                    if 0 <= new_x < self.board.shape[0] and 0 <= new_y < self.board.shape[1]:
                        next_new_mov = self.board[new_x, new_y]
                        if next_new_mov == '':
                            res.append(Move((x, y), (new_x, new_y)))
                        elif next_new_mov[-1] != current_color:
                            res.append(Move((x, y), (new_x, new_y)))
                            break
                        else:
                            break
                    else:
                        break
                    i += 1
            return res

        def get_movement_queen():
            return get_movement_rook() + get_movement_bishop()

        def get_movement_king():
            res = []
            moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
            for dx, dy in moves:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.board.shape[0] and 0 <= ny < self.board.shape[1]:
                    next_new_mov = self.board[nx, ny]
                    if next_new_mov == '' or next_new_mov[-1] != current_color:
                        res.append(Move((x, y), (nx, ny)))
            return res

        match self.board[x][y][0]:
            case 'p':
                return get_movement_pawn()
            case 'r':
                return get_movement_rook()
            case 'n':
                return get_movement_knight()
            case 'b':
                return get_movement_bishop()
            case 'q':
                return get_movement_queen()
            case 'k':
                return get_movement_king()
            case _:
                print('no valid piece')
                return []

    def make_move(self, move: Move):
        start_place = move.start_pos
        end_place = move.end_pos
        piece = self.board[start_place[0], start_place[1]]

        self.update_board_key(start_place, piece)

        self.board[start_place[0], start_place[1]] = ''
        if self.board[end_place[0], end_place[1]] != '':
            move.captured_piece = self.board[end_place[0], end_place[1]]
            self.update_board_key(end_place, move.captured_piece)
            if move.captured_piece[0] == 'k':
                self.is_game_over = True

        piece_add_board_key = piece
        if piece[0] == 'p' and (end_place[0] == 0 or end_place[0] == 7):
            piece_add_board_key = 'q' + piece[-1]
            self.board[end_place[0], end_place[1]] = piece_add_board_key
        else:
            self.board[end_place[0], end_place[1]] = piece
        self.update_board_key(end_place, piece_add_board_key)

        if piece[0] == 'k':
            self.king_pos[piece[1]] = end_place
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def undo_move(self, move: Move):
        start_place = move.start_pos
        end_place = move.end_pos
        piece = self.board[end_place[0], end_place[1]]

        self.update_board_key(end_place, piece)

        if move.captured_piece:
            if move.captured_piece[0] == 'k':
                self.is_game_over = False
            self.board[end_place[0], end_place[1]] = move.captured_piece
            self.update_board_key(end_place, move.captured_piece)
        else:
            self.board[end_place[0], end_place[1]] = ''

        piece_add_board_key = piece
        if piece[0] == 'q' and move.is_promotion:
            piece_add_board_key = 'p' + piece[-1]
            self.board[start_place[0], start_place[1]] = piece_add_board_key
        else:
            self.board[start_place[0], start_place[1]] = piece
        self.update_board_key(start_place, piece_add_board_key)

        if piece[0] == 'k':
            self.king_pos[piece[1]] = start_place
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def update_board_key(self, pos, piece):
        if piece == '':
            return
    
        shift_amount = (pos[0] * 8 + pos[1]) * 4
        self.board_key ^= int(self.piece_encoding[piece], 16) << shift_amount

    def get_piece_value(self, pos):
        x = pos[0]
        y = pos[1]

        piece = self.board[x,y]
        if piece == '':
            return 0
        else:
            return self.piece_values[piece[0]]

    def evaluate_v1(self):

        result = 0.0

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    coef = 1.0 if color_piece == self.board_color_top else -1.0

                    result += (self.piece_values[type_piece]) * coef
        return result


    def evaluate_v2(self):
        king_middle_game_table = [
            [20, 30, 10, 0, 0, 10, 30, 20],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30]
        ]

        king_middle_game_table_reversed = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]

        queen_table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]

        queen_table_reversed = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]

        ]

        rook_table = [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        rook_table_reversed = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ]

        bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]

        bishop_table_reversed = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]

        knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]

        knight_table_reversed = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]

        pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [10, 5, 0, 20, 20, 0, 5, 10],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        pawn_table_reversed = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [10, 5, 0, 20, 20, 0, 5, 10],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        position_tables = {
            'k': (king_middle_game_table, king_middle_game_table_reversed),
            'q': (queen_table, queen_table_reversed),
            'r': (rook_table, rook_table_reversed),
            'b': (bishop_table, bishop_table_reversed),
            'n': (knight_table, knight_table_reversed),
            'p': (pawn_table, pawn_table_reversed)
        }

        result = 0.0

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    coef = 1.0 if color_piece == self.board_color_top else -1.0

                    table_normal, table_reversed = position_tables[type_piece]
                    table = table_normal if coef == 1.0 else table_reversed

                    result += (self.piece_values[type_piece] + table[x][y]) * coef
        return result

    def evaluate_v3(self):
        def king_distance_to_edge(x, y):
            """Calcule la distance du roi aux bords de l'échiquier."""
            return min(x, 7 - x, y, 7 - y)

        mg_king_table = [
            [20, 30, 10, 0, 0, 10, 30, 20],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30]
        ]

        eg_king_table = [
			[-50, -30, -30, -30, -30, -30, -30, -50],
			[-30, -25, 0, 0, 0, 0, -25, -30],
			[-25, -20, 20, 25, 25, 20, -20, -25],
			[-20, -15, 30, 40, 40, 30, -15, -20],
			[-15, -10, 35, 45, 45, 35, -10, -15],
			[-10, -5, 20, 30, 30, 20, -5, -10],
			[-5, 0, 5, 5, 5, 5, 0, -5],
			[-20, -10, -10, -10, -10, -10, -10, -20]
		]

        queen_table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]

        rook_table = [
            [0, 0, 5, 5, 5, 5, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]

        knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]

        mg_pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [10, 5, 0, 20, 20, 0, 5, 10],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        eg_pawn_table = [
			[0, 0, 0, 0, 0, 0, 0, 0],
			[10, 10, 10, 10, 10, 10, 10, 10],
			[10, 10, 10, 10, 10, 10, 10, 10],
			[20, 20, 20, 20, 20, 20, 20, 20],
			[30, 30, 30, 30, 30, 30, 30, 30],
			[50, 50, 50, 50, 50, 50, 50, 50],
			[80, 80, 80, 80, 80, 80, 80, 80],
			[0, 0, 0, 0, 0, 0, 0, 0]
        ]

        position_tables = {
            'k': mg_king_table,
            'q': queen_table,
            'r': rook_table,
            'b': bishop_table,
            'n': knight_table,
            'p': mg_pawn_table
        }
        eg_position_tables = {
            'k': eg_king_table,
            'q': queen_table,
            'r': rook_table,
            'b': bishop_table,
            'n': knight_table,
            'p': eg_pawn_table
        }
        mg_result = 0.0
        eg_result = 0.0
        material_count = 0

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    is_positive = color_piece == self.board_color_top
                    table = position_tables[type_piece]
                    eg_table = eg_position_tables[type_piece]

                    if type_piece not in 'k':
                        material_count += self.piece_values[type_piece]

                    """mobility = len(self.movement_piece(x, y))
                    mobility_weights = {'k': 0, 'q': 1.5, 'r': 1.2, 'b': 1.1, 'n': 1.2, 'p': 0.5}
                    mobility_bonus = mobility * mobility_weights.get(type_piece, 1) """

                    """ if type_piece == 'r':
                        column_open = all(self.board[row, y] == '' or self.board[row, y][0] not in 'pP' for row in range(8))
                        if column_open:
                            result += 20 if is_positive else -20 """

                    if type_piece == 'k':
                        if color_piece != self.board_color_top:  # Roi adverse
                            distance_to_edge = king_distance_to_edge(x, y)
                            # Bonus si le roi est proche des bords en fin de partie
                            king_endgame_bonus = (4 - distance_to_edge) * 10
                            eg_result -= king_endgame_bonus  # Pénalisation du roi adverse

                    if is_positive:
                        mg_result += self.piece_values[type_piece] + table[x][y] #+ mobility_bonus
                        eg_result += self.piece_values[type_piece] + eg_table[x][y]
                    else:
                        mg_result -= self.piece_values[type_piece] + table[7-x][y] #+ mobility_bonus
                        eg_result -= self.piece_values[type_piece] + eg_table[7-x][y]
        phase = min(material_count / (2 * (self.piece_values['r'] * 2 + self.piece_values['b'] + self.piece_values['n'])), 1.0)
        return (1 - phase) * eg_result + phase * mg_result

    def get_board_state(self):
        """
        Retourne une représentation immuable de l'état du plateau et du joueur à jouer.
        """
        # Convertir le plateau en une structure immuable (tuple de tuples)
        board_state = tuple(tuple(row) for row in self.board)
        # Inclure la couleur du joueur à jouer
        return board_state, self.color_to_play

    def get_board_state_v2(self):
        """
        Retourne une représentation immuable de l'état du plateau et du joueur à jouer.
        """
        # Convertir le plateau en une structure immuable (tuple de tuples)
        return self.board_key, self.color_to_play

def orderMoves(moves: list[Move], board: Board, is_maximizing: bool):
    def evaluate_move(move: Move):
        board.make_move(move)
        evaluation = board.evaluate_v2()
        board.undo_move(move)
        return evaluation

    return sorted(moves, key=evaluate_move, reverse=is_maximizing)

def order_moves2(moves: list[Move], board: Board, hashmove=None):
    def move_heuristic(move: Move):
        if hashmove and move == hashmove:
            return float('inf')   # Priorité maximale pour le hashmove

        # Priorité aux captures (valeur cible - valeur source)
        priority = board.get_piece_value(move.end_pos) - board.get_piece_value(move.start_pos)
        
        if move.is_promotion:
            priority += 900
        return priority

    # Trier les mouvements en fonction de leur heuristique
    return sorted(moves, key=move_heuristic, reverse=True)
