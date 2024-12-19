from Bots.ChessBotList import register_chess_bot
from Bots.utils import Board, Move
from Bots.Evaluate import evaluate_v2
import time
import csv
import os



def chess_bot(player_sequence, board, time_budget, **kwargs):
    #Pour les stats
    counter_leaf = 0
    csv_file = 'stat_result.csv'
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Si le fichier n'existe pas, ajoutez l'en-tête
        if not file_exists:
            writer.writerow(['Player_Bot', 'Profondeur', 'Temps_recursion', 'Nb de Feuilles'])

    time_limit = time.time() + time_budget * 0.95
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0
    best_move: Move = Move((0, 0), (0, 0))

    memoization = {}

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        # Pour les stats
        nonlocal counter_leaf

        board_key = board.get_board_state()

        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        if depth == 0 or board.is_game_over:
            if board_key in memoization:
                #print("Use save evaluate")
                return memoization[board_key], None
            else:
                counter_leaf += 1
                evaluation = evaluate_v2(board)
                # Pour les stats

                #print("Save evaluate")
                memoization[board_key] = evaluation
                return evaluation, None

        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        board_key_with_depth = (board_key, depth, board.color_to_play)

        if board_key_with_depth in memoization:
            best_evaluation, best_move = memoization[board_key_with_depth]
        else:
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

            start = time.time()

            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]

            # Pour les stats
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['AlphaBetaBotTimeMemo', str(depth), str(time.time() - start), str(counter_leaf)])
            counter_leaf = 0

        except TimeoutError:
            depth -= 1
            break


    print("depth max :"+str(depth))




    return best_move.get_return_move()

register_chess_bot('AlphaBetaBotTimeMemo', chess_bot)
