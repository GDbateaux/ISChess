def convert_from_fen(position: str) -> str:
    """
    Convertit une position en notation FEN vers un format personnalisé et inverse le tableau.
    
    :param position: Chaîne représentant une position FEN complète (inclut le trait aux blancs ou aux noirs).
    :return: Une chaîne représentant le format personnalisé inversé.
    """
    color = position.split(' ')[1]
    res = '0' + color + '01b2\n'  # Ajout de l'entête avec le trait (blanc ou noir)
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
            else:  # Pièces noires
                row_res.append(char + 'b')
                idx += 1
        formatted_rows.append(','.join(row_res))

    formatted_rows.reverse()

    res += '\n'.join(formatted_rows) + '\n'
    return res[0:-1]
