from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
import time
import random


def chess_bot(player_sequence, board, time_budget, **kwargs):
    start = time.time()
    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move: Move = alpha_beta_Random(board, float('-inf'), float('inf'), 4, start, time_budget-0.05)[1]
    return best_move.get_return_move()

def alpha_beta_Random(board: Board, alpha, beta, depth, start_time, time_limit):

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



register_chess_bot('AlphaBetaRandom', chess_bot)
