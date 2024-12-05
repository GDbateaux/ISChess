def get_movements(board, color):
    res = []
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x,y] != '' and board[x,y][-1] == color:
                piece_moves = movement_piece(board, x, y)
                for move in piece_moves:
                    res.append([(x,y), move])
    return res

def movement_piece(board, x, y):
    if board[x,y] == '':
        return []
    current_color = board[x,y][-1]

    def get_movement_pawn():
        res = []
        if x + 1 >= board.shape[0]:
            return res
        
        new_x = x + 1
        for i in range(3):
            new_y = y + i - 1
            if 0 <= new_y < board.shape[1]:
                if i == 1:
                    if board[new_x, new_y] == '':
                        res.append((new_x, new_y))
                else:
                    if board[new_x, new_y] != '' and board[new_x, new_y][-1] != current_color:
                        res.append((new_x, new_y))
        return res

    def get_movement_rook():
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
        return get_movement_rook() + get_movement_bishop()
    
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
            return get_movement_pawn()
        case 'r':
            return get_movement_rook()
        case 'n':
            return get_movement_knight()
        case 'b':
            return get_movement_bishop()
        case 'q':
            return get_movement_queen()
        case 'k':
            return get_movement_king()
        case _:
            print('no valid piece')
            return []
