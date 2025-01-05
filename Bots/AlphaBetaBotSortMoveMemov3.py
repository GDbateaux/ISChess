from Bots.ChessBotList import register_chess_bot
from Bots.utils import Board, Move, order_moves2
import time

import csv
import os
import random

turn = 0

def chess_bot(player_sequence, board, time_budget, **kwargs):

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
                 'turn', 'Fail'])



    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move: Move = Move((0, 0), (0, 0))

    memoization = {}

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        # Pour les stats
        nonlocal counter_leaf
        nonlocal counter_evaluate

        board_key = board.get_board_state_v2()

        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        if depth == 0 or board.is_game_over:
            counter_leaf += 1

            if board_key in memoization:
                return memoization[board_key][0], None

            else:
                counter_evaluate += 1

                evaluation = board.evaluate_v2()
                memoization[board_key] = (evaluation, None, depth)
                return evaluation, None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        if board_key in memoization and memoization[board_key][2] >= depth:
            best_evaluation, best_move, _ = memoization[board_key]
        else:
            hashmove = None
            if board_key in memoization:
                _, hashmove, _ = memoization[board_key]
            moves = order_moves2(board.get_movements(), board, hashmove)

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
            memoization[board_key] = (best_evaluation, best_move, depth)

        return best_evaluation, best_move

    #depth = board.test_depth()
    message_fail = "Coup Random"

    list_random = board.get_movements().copy()
    size = len(list_random)
    test = random.randint(0, size - 1)
    best_move = list_random[test]
    resultS = ['AlphaBetaBotSortMoveMemov3', str(depth), str(0), str(0), str(0), str(time_budget), str(turn), str(True)]

    while (time_limit > time.time()):
        counter_leaf = 0  # Réinitialisation avant chaque itération
        counter_evaluate = 0
        depth += 1
        try:
            start = time.time()
            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]
            #print(f'{depth}: {leaf}')
            #with open('test2.csv', mode='a', newline='') as file:
             #   writer = csv.writer(file)
              #  writer.writerow([str(depth), str(leaf)])

            resultS = ['AlphaBetaBotSortMoveMemov3', str(depth), str(time.time() - start), str(counter_leaf),
                       str(counter_evaluate),
                       str(time_budget), str(turn), str(False)]
            message_fail = ""


        except TimeoutError:
            depth -= 1
            break

    print(message_fail)
    # Pour les stats
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(resultS)
    #counter_leaf = 0
    #counter_evaluate = 0


    #print("depth max :" + str(depth))
    #print(leaf)
    return best_move.get_return_move()

register_chess_bot('AlphaBetaBotSortMoveMemov3', chess_bot)
