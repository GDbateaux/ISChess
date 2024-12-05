from Bots.ChessBotList import register_chess_bot
from .utils import get_movements

import random

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    moves = get_movements(board, color)
    rdm = random.randint(0, len(moves)-1)

    return moves[rdm][0], moves[rdm][1]

register_chess_bot('RandomBot', chess_bot)
