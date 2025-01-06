class Move:
    def __init__(self, start_pos, end_pos, is_promotion=False, captured_piece=None):
        # Initialisation d'un mouvement avec la position de départ, d'arrivée, 
        # une indication de promotion (optionnelle), et la pièce capturée (si existante).
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_promotion = is_promotion
        self.captured_piece = captured_piece
    
    def __eq__(self, other):
        # Permet de comparer deux objets Move en vérifiant leurs attributs.
        return self.__dict__ == other.__dict__

    def __repr__(self):
        # Retourne une représentation lisible du mouvement.
        return f"Move(start={self.start_pos}, end={self.end_pos}, promotion={self.is_promotion}, captured_piece={self.captured_piece})"

    def get_return_move(self):
        # Retourne les positions de départ et d'arrivée sous forme de tuple.
        return self.start_pos, self.end_pos


class Board:
    def __init__(self, board, board_color_top):
        # Initialisation du plateau d'échecs.
        self.board = board # Représentation 2D du plateau.
        self.board_color_top = board_color_top # Couleur en haut (blanc ou noir) (couleur du joueur).
        self.color_to_play = board_color_top # Couleur qui joue actuellement (se met à jour selon les mouvements).
        self.is_game_over = False # Indique si la partie est terminée.
        
        # Valeurs assignées aux pièces pour évaluation.
        self.piece_values = {
            'k': 8000.0,
            'q': 900.0,
            'r': 500.0,
            'b': 320.0,
            'n': 300.0,
            'p': 100.0
        }

        # Encodage des pièces pour générer une clé unique.
        self.piece_encoding = {
            '': '0',
            'pw': '1', 'nw': '2', 'bw': '3', 'rw': '4', 'qw': '5', 'kw': '6',
            'pb': '7', 'nb': '8', 'bb': '9', 'rb': 'A', 'qb': 'B', 'kb': 'C'
        }

        # Clé unique générée pour le plateau.
        self.board_key = self.generate_board_key()

    def generate_board_key(self):
        # Génère une clé unique pour le plateau en encodant les pièces.
        key = ""
        for row in self.board:
            for piece in row:
                key = self.piece_encoding.get(piece, '0') + key
        return int(key, 16)
    
    def get_movements(self):
        # Génère tous les mouvements valides pour le joueur actuel.
        res = []

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '' and self.board[x, y][-1] == self.color_to_play:
                    # Récupère les mouvements possibles pour chaque pièce.
                    piece_moves = self.movement_piece(x, y)
                    for move in piece_moves:
                        res.append(move)
        return res

    def movement_piece(self, x, y):
        # Récupère les mouvements possibles pour une pièce à un emplacement donné (x, y).
        if self.board[x, y] == '':
            return []
        current_color = self.board[x, y][-1]

        # Définitions des mouvements pour chaque type de pièce.
        def get_movement_pawn():
            # Génère les mouvements possibles pour un pion.
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
            # Génère les mouvements pour une tour.
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
            # Génère les mouvements pour un cavalier.
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
            # Génère les mouvements pour un fou.
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
            # Génère les mouvements pour une reine (mouvement de la tour et du fou).
            return get_movement_rook() + get_movement_bishop()

        def get_movement_king():
            # Génère les mouvements pour un roi.
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

        # Identifie le type de pièce pour appliquer les règles correspondantes.
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
        # Effectue un mouvement sur le plateau.
        start_place = move.start_pos
        end_place = move.end_pos
        piece = self.board[start_place[0], start_place[1]]

        # Met à jour la clé unique du plateau pour refléter le retrait de la pièce de la case de départ.
        self.update_board_key(start_place, piece)

        # Retire la pièce de la case de départ.
        self.board[start_place[0], start_place[1]] = ''

        # Vérifie si une pièce est capturée sur la case d'arrivée.
        if self.board[end_place[0], end_place[1]] != '':
            move.captured_piece = self.board[end_place[0], end_place[1]]
            # Met à jour la clé unique pour refléter la capture.
            self.update_board_key(end_place, move.captured_piece)
            if move.captured_piece[0] == 'k': # Si le roi est capturé, la partie est terminée.
                self.is_game_over = True

        piece_add_board_key = piece
        # Promotion des pions en dame si le pion atteint la dernière rangée.
        if piece[0] == 'p' and (end_place[0] == 0 or end_place[0] == 7):
            piece_add_board_key = 'q' + piece[-1]
            self.board[end_place[0], end_place[1]] = piece_add_board_key
        else:
            self.board[end_place[0], end_place[1]] = piece

        # Met à jour la clé unique du plateau pour la pièce sur la case d'arrivée.
        self.update_board_key(end_place, piece_add_board_key)

        # Change le tour du joueur.
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def undo_move(self, move: Move):
        # Annule un mouvement effectué précédemment.
        start_place = move.start_pos
        end_place = move.end_pos
        piece = self.board[end_place[0], end_place[1]]

        # Met à jour la clé unique pour refléter la suppression de la pièce de la case d'arrivée.
        self.update_board_key(end_place, piece)

        # Si une pièce a été capturée, la restituer à sa position initiale.
        if move.captured_piece:
            if move.captured_piece[0] == 'k':
                self.is_game_over = False
            self.board[end_place[0], end_place[1]] = move.captured_piece
            # Met à jour la clé pour la pièce restaurée.
            self.update_board_key(end_place, move.captured_piece)
        else:
            self.board[end_place[0], end_place[1]] = ''

        piece_add_board_key = piece
        # Rétrograder une promotion de pion en pion original si nécessaire.
        if piece[0] == 'q' and move.is_promotion:
            piece_add_board_key = 'p' + piece[-1]
            self.board[start_place[0], start_place[1]] = piece_add_board_key
        else:
            self.board[start_place[0], start_place[1]] = piece

        # Met à jour la clé unique pour la pièce replacée sur la case de départ.
        self.update_board_key(start_place, piece_add_board_key)

        # Change le tour du joueur.
        self.color_to_play = 'b' if self.color_to_play == 'w' else 'w'

    def update_board_key(self, pos, piece):
        # Met à jour la clé unique du plateau en fonction des changements apportés à une case donnée.
        if piece == '':
            return

        # Calcule le décalage correspondant à la position de la case sur l'échiquier.
        shift_amount = (pos[0] * 8 + pos[1]) * 4

        # Utilise XOR pour ajouter ou retirer la pièce correspondante à cette position dans la clé.
        self.board_key ^= int(self.piece_encoding[piece], 16) << shift_amount

    def get_piece_value(self, pos):
        # Renvoie la valeur de la pièce située à une position donnée.
        x = pos[0]
        y = pos[1]

        piece = self.board[x,y]
        if piece == '':
            return 0
        else:
            return self.piece_values[piece[0]]

    def evaluate(self):
        """
        Évalue la position actuelle de l'échiquier pour déterminer qui est avantagé.
        Combine des facteurs comme la valeur des pièces, leur position, et la phase de la partie (milieu ou fin).
        """
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
        endgame_material_start = self.piece_values['r'] * 2 + self.piece_values['b'] + self.piece_values['n']

        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                if self.board[x, y] != '':
                    piece = self.board[x, y]
                    color_piece = piece[-1]
                    type_piece = piece[0]

                    is_positive = color_piece == self.board_color_top
                    table = position_tables[type_piece]
                    eg_table = eg_position_tables[type_piece]

                    if type_piece not in 'kp':
                        material_count += self.piece_values[type_piece]

                    if type_piece == 'k':
                        if color_piece != self.board_color_top:  # Roi adverse
                            distance_to_edge = king_distance_to_edge(x, y)
                            # Bonus si le roi est proche des bords en fin de partie
                            king_endgame_bonus = (4 - distance_to_edge) * 10
                            eg_result -= king_endgame_bonus  # Pénalisation du roi adverse

                    if is_positive:
                        mg_result += self.piece_values[type_piece] + table[x][y]
                        eg_result += self.piece_values[type_piece] + eg_table[x][y]
                    else:
                        mg_result -= self.piece_values[type_piece] + table[7-x][y]
                        eg_result -= self.piece_values[type_piece] + eg_table[7-x][y]
        phase = min(material_count / (2 * endgame_material_start), 1.0)
        return (1 - phase) * eg_result + phase * mg_result

    def get_board_state(self):
        """
        Retourne une représentation immuable de l'état du plateau et du joueur à jouer.
        """
        # Convertir le plateau en une structure immuable (tuple de tuples)
        return self.board_key, self.color_to_play

def order_moves(moves: list[Move], board: Board, hashmove=None):
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
