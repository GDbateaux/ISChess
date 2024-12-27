import csv
import os
import time

from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
turn = 0

def chess_bot(player_sequence, board, time_budget, **kwargs):
    # Pour les stats
    global turn
    turn += 1
    counter_leaf = 0
    counter_depth = 0
    csv_file = 'result.csv'
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Si le fichier n'existe pas, ajoutez l'en-tête
        if not file_exists:
            writer.writerow(
                ['Player_Bot', 'Profondeur', 'Temps_recursion', 'Nb de Feuilles', 'Nb d évaluations', 'Time budget',
                 'turn'])

    def alpha_beta(board: Board, alpha, beta, depth):
        # Pour les stats
        nonlocal counter_leaf

        if depth == 0 or board.is_game_over:
            counter_leaf += 1

            return board.evaluate_v2(), None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        for move in board.get_movements():
            board.make_move(move)
            evaluation, _ = alpha_beta(board, alpha, beta, depth - 1)
            board.undo_move(move)

            if is_maximizing:
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = move
                alpha = max(alpha, evaluation)
            elif not is_maximizing:
                if evaluation < best_evaluation:
                    best_evaluation = evaluation
                    best_move = move
                beta = min(beta, evaluation)
            if beta < alpha:
                break

        return best_evaluation, best_move

    start = time.time()
    depth = 3
    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move: Move = alpha_beta(board, float('-inf'), float('inf'), depth)[1]

    # Pour les stats
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['AlphaBetaBot', str(depth), str(time.time() - start), str(counter_leaf),
                         str(counter_leaf), str(time_budget), str(turn)])
    counter_leaf = 0


    return best_move.get_return_move()




register_chess_bot('AlphaBetaBot', chess_bot)