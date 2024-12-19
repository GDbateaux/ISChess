from Bots.ChessBotList import register_chess_bot
from .utils import Board

import time

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    board: Board = Board(board, color)
    for i in range(7):
        start_time = time.time()
        num_pos = get_num_board_positions(board, i)
        print(f'depth: {i} number positions: {num_pos} time: {time.time() - start_time}')
    return board.get_movements()[0].get_return_move()

def get_num_board_positions(board: Board, depth):
    if depth == 0 or board.is_game_over:
        return 1
    num_pos = 0
    for move in board.get_movements():
        board.make_move(move)
        num_pos += get_num_board_positions(board, depth-1)
        board.undo_move(move)

    return num_pos

register_chess_bot('BoardNumPositions', chess_bot)
