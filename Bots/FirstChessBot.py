from Bots.ChessBotList import register_chess_bot

def chess_bot(player_sequence, board, time_budget, **kwargs):
    print(board)
    color = player_sequence[1]
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != '' and board[x,y][-1] == color:
                print(movement_piece(board, x, y))                

    return (0,0), (0,0)

register_chess_bot('FirstBot', chess_bot)

def movement_piece(board, x, y):
    if board[x,y] == '':
        return
    current_color = board[x,y][-1]

    def get_movement_pawn():
        res = []
        moves = [
             (1, 0)
        ]
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                next_new_mov = board[nx, ny]
                if next_new_mov == '' or next_new_mov[-1] != current_color:
                    res.append((nx, ny))
        return res

    def get_movement_rock():
            res = []
        directions = [(-1,0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            i = 1
            while True:
                new_x = x + dx * i
                new_y = y + dy * i

                if 0 <= new_x < board.shape[0] and 0 <= new_y < board.shape[1]:
                    next_new_mov = board[new_x, new_y]
                    if next_new_mov == '':
                        res.append((new_x, new_y))
                    elif next_new_mov[-1] != current_color:
                        res.append((new_x, new_y))
                        break
                    else:
                        break
                else:
                    break
                i += 1
        return res
        

    def get_movement_knight():
        res = []
        moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (1, -2), (-1, 2), (1, 2)
        ]
        
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                next_new_mov = board[nx, ny]
                if next_new_mov == '' or next_new_mov[-1] != current_color:
                    res.append((nx, ny))
        return res
    
    def get_movement_bishop():
        res = []
        directions = [(-1,-1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            i = 1
            while True:
                new_x = x + dx * i
                new_y = y + dy * i

                if 0 <= new_x < board.shape[0] and 0 <= new_y < board.shape[1]:
                    next_new_mov = board[new_x, new_y]
                    if next_new_mov == '':
                        res.append((new_x, new_y))
                    elif next_new_mov[-1] != current_color:
                        res.append((new_x, new_y))
                        break
                    else:
                        break
                else:
                    break
                i += 1
        return res
    
    def get_movement_queen():
        return get_movement_rock() + get_movement_bishop()
    
    def get_movement_king():
        res = []
        moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),         (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1]:
                next_new_mov = board[nx, ny]
                if next_new_mov == '' or next_new_mov[-1] != current_color:
                    res.append((nx, ny))
        return res
    
    match board[x][y][0]:
        case 'p':
            print('pawn')
            return get_movement_pawn()
        case 'r':
            print('rock')
            return get_movement_rock()
        case 'n':
            print('knight')
            return get_movement_knight()
        case 'b':
            print('bishop')
            return get_movement_bishop()
        case 'q':
            print('queen')
            return get_movement_queen()
        case 'k':
            print('king')
            return get_movement_king()
        case _:
            print('no valid piece')
