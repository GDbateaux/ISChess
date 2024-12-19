import csv

from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
from .Evaluate import evaluate_v2

import time
import csv
import os


def chess_bot(player_sequence, board, time_budget, **kwargs):
    # Pour les stats
    counter_leaf = 0

    csv_file = 'stat_result3.csv'
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Si le fichier n'existe pas, ajoutez l'en-tête
        if not file_exists:
            writer.writerow(['Player_Bot', 'Profondeur', 'Temps_recursion', 'Nb de Feuilles', 'Nb d évaluations'])

    print(player_sequence)
    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move:Move = Move((0,0), (0,0))

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        # Pour les stats
        nonlocal counter_leaf

        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        if depth == 0 or board.is_game_over:
            counter_leaf += 1

            return evaluate_v2(board), None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        for move in board.get_movements():
            board.make_move(move)
            evaluation, _ = alpha_beta(board, alpha, beta, depth - 1, time_limit)
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

    while(time_limit > time.time()):
        depth += 1
        try:
            start = time.time()

            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]

            # Pour les stats
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['AlphaBetaBotTime', str(depth), str(time.time() - start), str(counter_leaf),
                                 str(counter_leaf)])
            counter_leaf = 0

        except TimeoutError:
            depth -= 1
            break
        
    print(depth)
    return best_move.get_return_move()

register_chess_bot('AlphaBetaBotTime', chess_bot)
