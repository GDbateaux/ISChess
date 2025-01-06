from Bots.ChessBotList import register_chess_bot
from Bots.SS_utils import Board, Move, order_moves
import time


def chess_bot(player_sequence, board, time_budget, **kwargs):
    """
    Implémente un bot d'échecs utilisant l'algorithme Alpha-Beta avec tri des mouvements
    et mémorisation (memoization) pour améliorer les performances.
    """
    time_limit = time.time() + time_budget * 0.95 # Temps alloué légèrement inférieur à la limite pour éviter un dépassement.
    color = player_sequence[1]
    board: Board = Board(board, color)
    depth = 0 # Profondeur actuelle de recherche.
    best_move: Move = board.get_movements()[0]

    memoization = {} # Dictionnaire pour stocker les évaluations des positions déjà visitées.

    def alpha_beta(board: Board, alpha, beta, depth, time_limit):
        """
        Implémente l'algorithme Alpha-Beta pour la recherche dans l'arbre des mouvements.

        Args:
            board (Board): État actuel du plateau.
            alpha (float): Limite inférieure pour le joueur maximisant.
            beta (float): Limite supérieure pour le joueur minimisant.
            depth (int): Profondeur de recherche actuelle.
            time_limit (float): Temps limite avant d'interrompre la recherche.

        Returns:
            tuple: Meilleure évaluation trouvée et le mouvement correspondant.
        """
        board_key = board.get_board_state()

        # Vérification du dépassement du temps alloué.
        if time.time() >= time_limit:
            raise TimeoutError("Time limit exceeded")

        # Condition d'arrêt : profondeur maximale atteinte ou partie terminée.
        if depth == 0 or board.is_game_over:
            if board_key in memoization:
                return memoization[board_key][0], None
            else:
                evaluation = board.evaluate()
                memoization[board_key] = (evaluation, None, depth)
                return evaluation, None

        # Déterminer si le bot maximise ou minimise l'évaluation.
        is_maximizing = board.board_color_top == board.color_to_play
        best_evaluation = float('-inf') if is_maximizing else float('inf')
        best_move = None

        # Vérification si une évaluation mémorisée peut être utilisée.
        if board_key in memoization and memoization[board_key][2] >= depth:
            best_evaluation, best_move, _ = memoization[board_key]
        else:
            # Récupération du mouvement prioritaire (hashmove) si disponible.
            hashmove = None
            if board_key in memoization:
                _, hashmove, _ = memoization[board_key]
            moves = order_moves(board.get_movements(), board, hashmove)

            for move in moves:
                board.make_move(move)
                evaluation, _ = alpha_beta(board, alpha, beta, depth - 1, time_limit)
                board.undo_move(move)

                # Mise à jour des valeurs d'évaluation et des limites alpha/beta.
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

    # Boucle d'approfondissement progressif jusqu'à expiration du temps.
    while (time_limit > time.time()):
        depth += 1
        try:
            best_move = alpha_beta(board, float('-inf'), float('inf'), depth, time_limit)[1]
        except TimeoutError:
            break
        
    # Retourne le mouvement optimal dans le format attendu.
    return best_move.get_return_move()

register_chess_bot('SS_AlphaBetaBotSortMoveMemov3', chess_bot)
