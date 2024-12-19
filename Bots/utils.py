class Move:
    def __init__(self, start_pos, end_pos, is_promotion=False, captured_piece=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_promotion = is_promotion
        self.captured_piece = captured_piece

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

        self.board[start_place[0], start_place[1]] = ''
        if self.board[end_place[0], end_place[1]] != '':
            move.captured_piece = self.board[end_place[0], end_place[1]]
            if move.captured_piece[0] == 'k':
                self.is_game_over = True

        if piece[0] == 'p' and (end_place[0] == 0 or end_place[0] == 7):
            self.board[end_place[0], end_place[1]] = 'q' + piece[-1]
        else:
            self.board[end_place[0], end_place[1]] = piece
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def undo_move(self, move: Move):
        start_place = move.start_pos
        end_place = move.end_pos
        piece = self.board[end_place[0], end_place[1]]

        if move.captured_piece:
            if move.captured_piece[0] == 'k':
                self.is_game_over = False
            self.board[end_place[0], end_place[1]] = move.captured_piece
        else:
            self.board[end_place[0], end_place[1]] = ''

        if piece[0] == 'q' and move.is_promotion:
            self.board[start_place[0], start_place[1]] = 'p' + piece[-1]
        else:
            self.board[start_place[0], start_place[1]] = piece
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def get_board_state(self):
        """
        Retourne une représentation immuable de l'état du plateau et du joueur à jouer.
        """
        # Convertir le plateau en une structure immuable (tuple de tuples)
        board_state = tuple(tuple(row) for row in self.board)

        # Inclure la couleur du joueur à jouer
        return board_state, self.color_to_play
