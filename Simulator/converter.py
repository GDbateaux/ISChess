def convert_from_fen(position: str) -> str:
    color = position.split(' ')[1]
    res = '0' + color + '01b2\n'
    pos = position.split(' ')[0].strip()
    board = pos.split('/')

    formatted_rows = []

    for row in board:
        row_res = []
        idx = 0
        for char in row:
            if char.isnumeric():
                for _ in range(int(char)):
                    row_res.append('--')
                    idx += 1
            elif char.isupper():
                row_res.append(char.lower() + 'w')
                idx += 1
            else:
                row_res.append(char + 'b')
                idx += 1
        formatted_rows.append(','.join(row_res))

    formatted_rows.reverse()

    res += '\n'.join(formatted_rows) + '\n'
    return res[0:-1]
