from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move
from .Evaluate import evaluate_v2
import hashlib
import time

# Cache de mémorisation global
memo_cache = {}

def chess_bot(player_sequence, board, time_budget, **kwargs):
    start_time = time.time()

    color = player_sequence[1]
    board: Board = Board(board, color)
    best_move = board.get_movements()[1]

    while time.time() - start_time < time_budget:
        remaining_time = time_budget - (time.time() - start_time)
        if remaining_time < 0.01:
            print("Trop de temps")
            break
        try:
            best_move = alpha_beta_Memo(board, float('-inf'), float('inf'), 4)[1]
            print(best_move)
        except TimeoutError:  # En cas de gestion d'exception liée au temps, si elle existe
            print("except TimeOut")

            break
    print(best_move)

    return best_move.get_return_move()

def hash_board(board: Board, depth: int) -> str:
    """
    Fonction de hachage pour générer une clé unique basée sur l'état du plateau et la profondeur.
    """
    # Représentation sous forme de chaîne de l'état du plateau (vous pouvez ajuster cela en fonction de votre structure de Board)
    board_state = ''.join([str(piece) for piece in board.board])  # Convertir l'état du plateau en chaîne
    color_to_play = board.color_to_play  # Couleur à jouer

    # Créer une chaîne qui représente l'état complet (y compris la profondeur)
    board_str = f"{board_state}|{color_to_play}|{depth}"

    # Générer un hash de cette chaîne en utilisant SHA256
    return hashlib.sha256(board_str.encode('utf-8')).hexdigest()

def alpha_beta_Memo(board: Board, alpha, beta, depth):
    # Utilisation du cache pour éviter de recalculer des positions déjà évaluées
    cache_key = hash_board(board, depth)  # Générer une clé unique basée sur le hash
    if cache_key in memo_cache:
        return memo_cache[cache_key]

    if depth == 0:
        evaluation = evaluate_v2(board)
        memo_cache[cache_key] = (evaluation, None)
        return evaluation, None

    is_maximizing = board.board_color_top == board.color_to_play
    best_evaluation = float('-inf') if is_maximizing else float('inf')
    best_move = None

    for move in board.get_movements():
        board.make_move(move)
        evaluation, _ = alpha_beta_Memo(board, alpha, beta, depth - 1)
        board.undo_move(move)

        if is_maximizing:
            if evaluation > best_evaluation:
                best_evaluation = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
        else:
            if evaluation < best_evaluation:
                best_evaluation = evaluation
                best_move = move
            beta = min(beta, evaluation)

        if beta < alpha:
            break

    # Sauvegarde du résultat dans le cache
    memo_cache[cache_key] = (best_evaluation, best_move)
    return best_evaluation, best_move

register_chess_bot('AlphaBetaMemoBot', chess_bot)
