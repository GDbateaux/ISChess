import random
import time

from Bots.ChessBotList import register_chess_bot
from Bots.utils import Board, Move
from Bots.Evaluate import evaluate_v2


def chess_bot(player_sequence, board, time_budget, **kwargs):
    start = time.time()
    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move: Move = min_max(board, 3,start, time_budget-0.05)[1]
    return best_move.get_return_move()


def min_max(board: Board, depth, start_time, time_limit):
    is_maximizing = board.board_color_top == board.color_to_play
    best_evaluation = float('-inf') if is_maximizing else float('inf')
    best_move = None

    list_random = board.get_movements().copy()
    size = len(list_random)
    counter = size / 2

    if time.time() - start_time > time_limit:
        print("Coup Random")
        test = random.randint(0, size - 1)
        move = list_random[test]
        return best_evaluation, move


    if depth == 0 or board.is_game_over:
        return evaluate_v2(board), None


    for move in board.get_movements():
        board.make_move(move)
        evaluation, _ = min_max(board, depth - 1, start_time, time_limit)
        board.undo_move(move)

        if is_maximizing and evaluation > best_evaluation:
            best_evaluation = evaluation
            best_move = move
        elif not is_maximizing and evaluation < best_evaluation:
            best_evaluation = evaluation
            best_move = move

    return best_evaluation, best_move


register_chess_bot('MinMaxBot', chess_bot)