from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
from .Evaluate import evaluate_v2


def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move:Move = min_max(board, 3)[1]
    return best_move.get_return_move()


def min_max(board: Board, depth):
    if depth == 0:
        return evaluate_v2(board), None

    is_maximizing = board.board_color_top == board.color_to_play
    best_evaluation = float('-inf') if is_maximizing else float('inf')
    best_move = None

    for move in board.get_movements():
        board.make_move(move)
        evaluation, _ = min_max(board, depth-1)
        board.undo_move(move)

        if is_maximizing and evaluation > best_evaluation:
            best_evaluation = evaluation
            best_move = move
        elif not is_maximizing and evaluation < best_evaluation:
            best_evaluation = evaluation
            best_move = move
    
    return best_evaluation, best_move

register_chess_bot('MinMax', chess_bot)
