from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move


def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move:Move = alpha_beta(board, float('-inf'), float('inf'), 4)[1]
    return best_move.get_return_move()

def alpha_beta(board: Board, alpha, beta, depth):
    if depth == 0 or board.is_game_over:
        return board.evaluate_v2(), None

    is_maximizing = board.board_color_top == board.color_to_play
    best_evaluation = float('-inf') if is_maximizing else float('inf')
    best_move = None

    for move in board.get_movements():
        board.make_move(move)
        evaluation, _ = alpha_beta(board, alpha, beta, depth-1)
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

register_chess_bot('AlphaBetaBot', chess_bot)
