from Bots.ChessBotList import register_chess_bot

def chess_bot(player_sequence, board, time_budget, **kwargs):

    color = player_sequence[1]
    for x in range(board.shape[0]-1):
        for y in range(board.shape[1]):
            if board[x,y][-1] == color:
                movement_piece(board, (x, y))

    return (0,0), (0,0)

def movement_piece(board, piece_position):
      res = [(1,0), (2,0)]
      piece_type = board[piece_position[0], piece_position[1]]


#   Example how to register the function
register_chess_bot("FirstBot", chess_bot)
