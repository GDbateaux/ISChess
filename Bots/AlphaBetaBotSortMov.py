from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move, orderMoves

import time
import csv
import os
import random

turn = 0

num_leaf_visited = 0

def chess_bot(player_sequence, board, time_budget, **kwargs):
    global num_leaf_visited
    num_leaf_visited = 0

    # Pour les stats
    global turn
    turn += 1
    counter_leaf = 0
    counter_evaluate = 0
    csv_file = 'result.csv'
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Si le fichier n'existe pas, ajoutez l'en-tête
        if not file_exists:
            writer.writerow(
                ['Player_Bot', 'Profondeur', 'Temps_recursion', 'Nb de Feuilles', 'Nb d évaluations', 'Time budget',
                 'turn','Fail'])


    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move:Move = Move((0,0), (0,0))

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        # Pour les stats
        nonlocal counter_leaf
        nonlocal counter_evaluate

        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        if depth == 0 or board.is_game_over:
            counter_leaf += 1
            global num_leaf_visited
            counter_evaluate += 1
            num_leaf_visited += 1
            return board.evaluate_v2(), None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None
        moves = orderMoves(board.get_movements(), board, is_maximizing)

        for move in moves:
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

    depth = 5
    message_fail = "Coup Random"

    list_random = board.get_movements().copy()
    size = len(list_random)
    test = random.randint(0, size - 1)
    best_move = list_random[test]
    resultS = ['AlphaBetaBotSortMov', str(depth), str(0), str(0), str(0), str(time_budget), str(turn), str(True)]

    while (time_limit > time.time()):
        #    depth += 1
        try:
            start = time.time()
            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]
            resultS = ['AlphaBetaBotSortMov', str(depth), str(time.time() - start), str(counter_leaf),
                       str(counter_evaluate),
                       str(time_budget), str(turn), str(False)]
            message_fail = ""
            break
        except TimeoutError:
            depth -= 1
            break

    print(message_fail)
    # Pour les stats
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(resultS)
    counter_leaf = 0
    counter_evaluate = 0

    return best_move.get_return_move()



register_chess_bot('AlphaBetaBotSortMov', chess_bot)
