from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
import time
import csv
import os

num_leaf_visited = 0
turn = 0


def chess_bot(player_sequence, board, time_budget, **kwargs):
    global num_leaf_visited
    global turn
    turn += 1
    num_leaf_visited = 0
    # Pour les stats
    counter_leaf = 0

    csv_file = 'result.csv'
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Si le fichier n'existe pas, ajoutez l'en-tête
        if not file_exists:
            writer.writerow(
                ['Player_Bot', 'Profondeur', 'Temps_recursion', 'Nb de Feuilles', 'Nb d évaluations', 'Time budget',
                 'turn'])

    print(player_sequence)
    time_limit = time.time() + time_budget * 0.95


    color = player_sequence[1]
    board: Board = Board(board, color)

    def min_max(board: Board, depth):
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
            evaluation, _ = min_max(board, depth - 1)
            board.undo_move(move)

            if is_maximizing and evaluation > best_evaluation:
                best_evaluation = evaluation
                best_move = move
            elif not is_maximizing and evaluation < best_evaluation:
                best_evaluation = evaluation
                best_move = move

        return best_evaluation, best_move

    start = time.time()
    depth = 3
    best_move: Move = min_max(board, depth)[1]

    # Pour les stats
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['MinMaxBot', str(depth), str(time.time() - start), str(counter_leaf),
                         str(counter_leaf), str(time_budget), str(turn)])
    counter_leaf = 0

    return best_move.get_return_move()





register_chess_bot('MinMaxBot', chess_bot)
