import csv
import os

from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
import time
import random

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

    start = time.time()
    color = player_sequence[1]
    board: Board = Board(board, color)


    def alpha_beta_Random(board: Board, alpha, beta, depth, start_time, time_limit):

        # Pour les stats
        nonlocal counter_leaf
        nonlocal counter_depth

        counter_depth = depth

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        list_random = board.get_movements().copy()
        size = len(list_random)
        counter = size / 2

        if time.time() - start_time > time_limit:
            print("Coup Random")
            counter_depth -= 1
            test = random.randint(0, size - 1)
            move = list_random[test]
            return best_evaluation, move

        if depth == 0 or board.is_game_over:
            counter_leaf += 1

            return board.evaluate_v2(), None

        while counter > 0:
            size2 = len(list_random)
            test = random.randint(0, size2 - 1)
            move = list_random[test]
            list_random.remove(move)

            board.make_move(move)
            evaluation, _ = alpha_beta_Random(board, alpha, beta, depth - 1, start_time, time_limit)
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

            counter -= 1

        return best_evaluation, best_move





    best_move: Move = alpha_beta_Random(board, float('-inf'), float('inf'), 4, start, time_budget - 0.05)[1]

    # Pour les stats
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['AlphaBetaBotRandom', str(counter_depth), str(time.time() - start), str(counter_leaf), str(counter_leaf), str(time_budget), str(turn)])
    counter_leaf = 0


    return best_move.get_return_move()





register_chess_bot('AlphaBetaRandom', chess_bot)