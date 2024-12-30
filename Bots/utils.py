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
        king_middle_game_table = [
            [5, 0, 0, 0, 0, 0, 0, 5],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30]
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

        pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [10, 10, 10, -20, -20, 10, 10, 10],
            [10, 5, 0, 20, 20, 0, 5, 10],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        position_tables = {
            'k': king_middle_game_table,
            'q': queen_table,
            'r': rook_table,
            'b': bishop_table,
            'n': knight_table,
            'p': pawn_table
        }
        result = 0.0

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    is_positive = color_piece == self.board_color_top
                    table = position_tables[type_piece]

                    """mobility = len(self.movement_piece(x, y))
                    mobility_weights = {'k': 0, 'q': 1.5, 'r': 1.2, 'b': 1.1, 'n': 1.2, 'p': 0.5}
                    mobility_bonus = mobility * mobility_weights.get(type_piece, 1) """

                    if type_piece == 'r':
                        column_open = all(self.board[row, y] == '' or self.board[row, y][0] not in 'pP' for row in range(8))
                        if column_open:
                            result += 20 if is_positive else -20

                    if is_positive:
                        result += self.piece_values[type_piece] + table[x][y] #+ mobility_bonus
                    else:
                        result -= self.piece_values[type_piece] + table[7-x][y] #+ mobility_bonus
        return result

    def evaluate_v4(self):
        #https://www.youtube.com/watch?v=RSIW7k_5eDc
        #How to Evaluate Chess Positions? Ft. Magnus Carlsen
        def piece_value(piece):
            piece_values = {
                'k': 0.0,  # Le roi n'a pas de valeur pour l'évaluation
                'q': 9.0,  # La dame est la pièce la plus puissante
                'r': 5.0,
                'b': 3.0,
                'n': 3.0,
                'p': 1.0
            }
            return piece_values.get(piece[0], 0)
        # Variables pour accumuler les scores de chaque facteur d'évaluation
        material_score = 0  # Score matériel total
        activity_score = 0  # Score d'activité des pièces
        king_safety_score = 0  # Score de sécurité du roi
        pawn_score = 0  # Score de la structure des pions
        king_positions = {'w': None, 'b': None}  # Positions des rois pour chaque couleur
        passed_pawns = {'w': 0, 'b': 0}  # Nombre de pions passés (n'a aucun pion adverse) pour chaque couleur
        # 1. Parcours de l'échiquier pour évaluer chaque pièce et chaque facteur
        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                piece = self.board[x, y]
                if piece != '':
                    color = piece[-1]
                    piece_type = piece[0]
                    # 2. Calcul du score matériel : additionne ou soustrait la valeur de la pièce en fonction de la couleur
                    material_score += piece_value(piece) if color == self.color_to_play else -piece_value(piece)
                    # 3. Calcul de l'activité des pièces : plus une pièce a de mouvements possibles, plus elle est active
                    piece_moves = self.movement_piece(x, y)
                    activity_score += len(piece_moves) * 0.1  # Score basé sur le nombre de déplacements possibles
                    # 4. Enregistrement de la position du roi pour chaque couleur
                    if piece_type == 'k':
                        king_positions[color] = (x, y)
                    # 5. Calcul de la structure des pions (pions passés)
                    if piece_type == 'p':
                        # Vérification si le pion est passé
                        is_passed = True
                        for i in range(-1,
                                       2):  # Vérifie les cases adjacentes pour s'assurer qu'aucun pion adverse ne bloque
                            for j in range(x + 1, self.board.shape[0]):  # Vérifie les cases devant le pion
                                if 0 <= y + i < self.board.shape[1]:
                                    neighbor_piece = self.board[j, y + i]
                                    if neighbor_piece != '' and neighbor_piece[0] == 'p' and neighbor_piece[
                                        -1] != color:
                                        is_passed = False
                                        break
                        if is_passed:
                            passed_pawns[color] += 1  # Incrémente le nombre de pions passés
                            pawn_score += 2 if color == self.color_to_play else -2  # Ajouter au score de structure de pions
        # 6. Calcul de la sécurité du roi : Vérifie si le roi est en échec ou en danger
        def is_king_safe(king_pos):
            safe = True
            for x in range(self.board.shape[0]):
                for y in range(self.board.shape[1]):
                    piece = self.board[x, y]
                    if piece != '' and piece[-1] != self.color_to_play:
                        moves = self.movement_piece(x, y)
                        for move in moves:
                            if move.end_pos == king_pos:  # Si une pièce adverse peut attaquer le roi
                                safe = False
                                break
                    if not safe:
                        break
            return safe
        # Vérification de la sécurité des rois des deux couleurs
        my_king_safe = is_king_safe(king_positions[self.color_to_play])
        opp_king_safe = is_king_safe(king_positions['b' if self.color_to_play == 'w' else 'w'])
        # 7. Calcul du score de sécurité du roi : +1 si votre roi est en sécurité, -1 s'il est en danger
        king_safety_score = (1 if my_king_safe else -1) - (1 if opp_king_safe else -1)
        # 8. Pondération des différents critères pour obtenir le score final
        poids_material = 0.4  # Poids attribué au score matériel
        poids_activity = 0.3  # Poids attribué à l'activité des pièces
        poids_king_safety = 0.2  # Poids attribué à la sécurité du roi
        poids_pawn_structure = 0.1  # Poids attribué à la structure des pions
        # 9. Calcul du score final en combinant tous les facteurs avec leurs poids respectifs
        total_score = (
                poids_material * material_score +
                poids_activity * activity_score +
                poids_king_safety * king_safety_score +
                poids_pawn_structure * pawn_score
        )
        return total_score  # Retourne le score final pour la position donnée


    def evaluate_v5(self):
        def piece_value(piece):
            piece_values = {
                'k': 0.0,  # Le roi n'a pas de valeur pour l'évaluation
                'q': 9.0,  # La dame est la pièce la plus puissante
                'r': 5.0,
                'b': 3.0,
                'n': 3.0,
                'p': 1.0
            }
            return piece_values.get(piece[0], 0)

        # Variables pour accumuler les scores de chaque facteur d'évaluation
        material_score = 0
        activity_score = 0
        king_safety_score = 0
        pawn_score = 0
        king_positions = {'w': None, 'b': None}

        # Parcours de l'échiquier pour évaluer chaque pièce et chaque facteur
        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                piece = self.board[x, y]
                if piece != '':
                    color = piece[-1]
                    piece_type = piece[0]

                    # Calcul du score matériel
                    value = piece_value(piece)
                    material_score += value if color == self.color_to_play else -value

                    # Calcul de l'activité des pièces
                    piece_moves = self.movement_piece(x, y)
                    activity_score += len(piece_moves) * 0.1 if color == self.color_to_play else -len(piece_moves) * 0.1

                    # Enregistrement de la position du roi
                    if piece_type == 'k':
                        king_positions[color] = (x, y)

                    # Calcul de la structure des pions (pions passés)
                    if piece_type == 'p':
                        is_passed = all(
                            self.board[j, y + i] == '' or self.board[j, y + i][-1] == color
                            for i in range(-1, 2)
                            for j in range(x + 1, self.board.shape[0])
                            if 0 <= y + i < self.board.shape[1]
                        )
                        if is_passed:
                            pawn_score += 2 if color == self.color_to_play else -2

        # Calcul de la sécurité du roi
        def is_king_safe(king_pos, opponent_color):
            return all(
                move.end_pos != king_pos
                for x in range(self.board.shape[0])
                for y in range(self.board.shape[1])
                if self.board[x, y] != '' and self.board[x, y][-1] == opponent_color
                for move in self.movement_piece(x, y)
            )

        my_king_safe = is_king_safe(king_positions[self.color_to_play], 'b' if self.color_to_play == 'w' else 'w')
        opp_king_safe = is_king_safe(king_positions['b' if self.color_to_play == 'w' else 'w'], self.color_to_play)
        king_safety_score = (1 if my_king_safe else -1) - (1 if opp_king_safe else -1)

        # Pondération des différents critères pour obtenir le score final
        poids_material = 0.4
        poids_activity = 0.3
        poids_king_safety = 0.2
        poids_pawn_structure = 0.1

        # Calcul du score final
        total_score = (
            poids_material * material_score +
            poids_activity * activity_score +
            poids_king_safety * king_safety_score +
            poids_pawn_structure * pawn_score
        )

        return total_score

    def evaluate_v3(self):
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

        """ king_end_game = [
            [-50, -30, -30, -30, -30, -30, -30, -50],
            [-30, -30, 0, 0, 0, 0, -30, -30],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-30, -10, 30, 40, 40, 30, -10, -30],
            [-30, -10, 30, 40, 40, 30, -10, -30],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-30, -20, -10, 0, 0, -10, -20, -30],
            [-50, -40, -30, -20, -20, -30, -40, -50]
        ] """

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

        piece_values = {
            'k': 2000.0,
            'q': 900.0,
            'r': 500.0,
            'b': 300.0,
            'n': 300.0,
            'p': 100.0
        }

        position_tables = {
            'k': (king_middle_game_table, king_middle_game_table_reversed),
            'q': (queen_table, queen_table_reversed),
            'r': (rook_table, rook_table_reversed),
            'b': (bishop_table, bishop_table_reversed),
            'n': (knight_table, knight_table_reversed),
            'p': (pawn_table, pawn_table_reversed)
        }

        result = 0.0
        mobility_score = 0.0

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    coef = 1.0 if color_piece == self.board_color_top else -1.0

                    table_normal, table_reversed = position_tables[type_piece]
                    table = table_normal if coef == 1.0 else table_reversed

                    result += (piece_values[type_piece] + table[x][y]) * coef

                    # Calculer la mobilité des pièces
                    piece_moves = self.movement_piece(x, y)  # Cette méthode existe déjà dans Board
                    mobility_score += len(piece_moves) * coef  # Mobilité = nombre de mouvements possibles

                    # Combinaison de l'évaluation matérielle et de la mobilité
                    result = result + mobility_score * 0.1  # Poids de la mobilité (ajustable)
        return result

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

def orderMoves_v3(moves: list[Move], board: Board, is_maximizing: bool):
    def evaluate_move(move: Move):
        board.make_move(move)
        evaluation = board.evaluate_v3()
        board.undo_move(move)
        return evaluation

    return sorted(moves, key=evaluate_move, reverse=is_maximizing)
def order_moves2(moves: list[Move], board: Board, is_maximizing, hashmove=None):
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
