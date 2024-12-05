
def evaluate(board, color):
    king = 16.0
    queen = 8.0
    knight = 4.0
    rook = 4.0
    bishop = 4.0
    pawn = 1.0

    result = 0.0

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x, y] != '':
                piece = board[x, y]
                color_piece = piece[-1]
                type_piece = piece[-2]

                coef = 0.0

                if color_piece != color:
                    coef = -1.0
                else :
                    coef = 1.0


                match type_piece:
                    case 'k':
                        result += king * coef
                    case 'q':
                        result += queen * coef
                    case 'b':
                        result += bishop * coef
                    case 'n' :
                        result += knight * coef
                    case 'r':
                        result += rook * coef
                    case 'p':
                        result += pawn * coef



    return result
