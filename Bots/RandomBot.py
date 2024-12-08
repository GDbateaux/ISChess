from Bots.ChessBotList import register_chess_bot
from .utils import Board, Move

import random

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    board: Board = Board(board, color)
    moves: list[Move] = board.get_movements()
    rdm = random.randint(0, len(moves)-1)

    return moves[rdm].get_return_move()

register_chess_bot('RandomBot', chess_bot)
