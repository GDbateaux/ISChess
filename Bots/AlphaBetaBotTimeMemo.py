from Bots.ChessBotList import register_chess_bot
from Bots.utils import Board, Move
from Bots.Evaluate import evaluate_v2
from typing import List
import time


def chess_bot(player_sequence, board, time_budget, **kwargs):
    start = time.time()
    print(player_sequence)
    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move: Move = Move((0, 0), (0, 0))

    memoization = {}

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        board_key = board.get_board_state()
        board_key_with_evaluate = (board_key, board.color_to_play)

        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        if depth == 0 or board.is_game_over:
            if board_key_with_evaluate in memoization:
                #print("Use save evaluate")
                return memoization[board_key_with_evaluate], None
            else:
                evaluation = evaluate_v2(board)
                #print("Save evaluate")
                memoization[board_key_with_evaluate] = evaluation
                return evaluation, None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        board_key_with_depth = (board_key, depth, board.color_to_play)

        if board_key_with_depth in memoization:
            #print(memoization[board_key_with_depth])
            evaluation, _ = memoization[board_key_with_depth]

        else :
            #print("Save sub-trees")


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

            memoization[board_key_with_depth] = (best_evaluation, best_move)

        return best_evaluation, best_move

    while (time_limit > time.time()):
        depth += 1
        try:
            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]
            print(time.time() - start)
        except TimeoutError:
            depth -= 1
            break

    print(depth)

    return best_move.get_return_move()


register_chess_bot('AlphaBetaBotTimeMemo', chess_bot)
