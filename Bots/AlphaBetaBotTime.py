from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
from .Evaluate import evaluate_v2

import time


def chess_bot(player_sequence, board, time_budget, **kwargs):
    print(player_sequence)
    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move:Move = Move((0,0), (0,0))

    while(time_limit > time.time()):
        depth += 1
        try:
            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]
        except TimeoutError:
            depth -= 1
            break
        
    print(depth)
    return best_move.get_return_move()

def alpha_beta(board: Board, alpha, beta, depth, time_limit):
    if time.time() >= time_limit:
        raise TimeoutError("Time limit exceeded")
    
    if depth == 0 or board.is_game_over:
        return evaluate_v2(board), None

    is_maximizing = board.board_color_top == board.color_to_play
    best_evaluation = float('-inf') if is_maximizing else float('inf')
    best_move = None

    for move in board.get_movements():
        board.make_move(move)
        evaluation, _ = alpha_beta(board, alpha, beta, depth-1, time_limit)
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

register_chess_bot('AlphaBetaBotTime', chess_bot)
