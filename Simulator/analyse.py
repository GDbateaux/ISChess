import csv

csv_file = 'game_results_StatEvalV3_vs_StatEvalV4.csv'

def analyze_game_results(csv_file):
    # Dictionnaires pour suivre les statistiques
    bots = {}
    total_games = 0

    try:
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                total_games += 1
                white_bot = row['White']
                black_bot = row['Black']
                winner = row['Winner']

                # Initialisation des dictionnaires pour les bots s'ils ne sont pas encore présents
                if white_bot not in bots:
                    bots[white_bot] = {'wins': 0, 'losses': 0, 'win_with_pieces': 0, 'draws': 0}
                if black_bot not in bots:
                    bots[black_bot] = {'wins': 0, 'losses': 0, 'win_with_pieces': 0, 'draws': 0}

                # Gestion des résultats
                if winner == "White":
                    bots[white_bot]['wins'] += 1
                    bots[black_bot]['losses'] += 1
                elif winner == "Black":
                    bots[black_bot]['wins'] += 1
                    bots[white_bot]['losses'] += 1
                else:  # Draw
                    white_pawns = int(row['White Pawns'])
                    black_pawns = int(row['Black Pawns'])

                    if white_pawns > black_pawns:
                        bots[white_bot]['wins'] += 1
                        bots[black_bot]['losses'] += 1
                        bots[white_bot]['win_with_pieces'] += 1
                    elif black_pawns > white_pawns:
                        bots[black_bot]['wins'] += 1
                        bots[white_bot]['losses'] += 1
                        bots[black_bot]['win_with_pieces'] += 1
                    else:
                        bots[white_bot]['draws'] += 1
                        bots[black_bot]['draws'] += 1

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Affichage des statistiques finales
    print("Bot Match Analysis Results:")
    print("------------------------------")
    print(f"Total games played: {total_games}")
    print()

    for bot_name, stats in bots.items():
        print(f"Bot: {bot_name}")
        print(f"  - Wins: {stats['wins']}")
        print(f"  - Losses: {stats['losses']}")
        print(f"  - Wins with pieces: {stats['win_with_pieces']}")
        print(f"  - Draws: {stats['draws']}")
        print()

# Appel de la méthode
analyze_game_results(csv_file)
