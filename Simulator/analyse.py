import csv

csv_file = 'game_results.csv'


def analyze_game_results(csv_file):
        # Dictionnaires pour suivre les statistiques
        bots = {}
        total_games = 0
        total_real_turns = 0

        try:
            with open(csv_file, mode='r', newline='') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    total_games += 1
                    white_bot = row['White']
                    black_bot = row['Black']
                    winner = row['Winner']
                    real_turns = int(row['Real Turns'])  # Correct column name if necessary

                    # Initialisation des dictionnaires pour les bots s'ils ne sont pas encore présents
                    if white_bot not in bots:
                        bots[white_bot] = {'white_wins': 0, 'black_wins': 0, 'draws': 0, 'games': 0}
                    if black_bot not in bots:
                        bots[black_bot] = {'white_wins': 0, 'black_wins': 0, 'draws': 0, 'games': 0}

                    # Mise à jour des statistiques pour chaque jeu
                    if winner == "White":
                        bots[white_bot]['white_wins'] += 1
                    elif winner == "Black":
                        bots[black_bot]['black_wins'] += 1
                    else:
                        bots[white_bot]['draws'] += 1
                        bots[black_bot]['draws'] += 1

                    # Mise à jour du nombre total de jeux et des tours réels
                    bots[white_bot]['games'] += 1
                    bots[black_bot]['games'] += 1
                    total_real_turns += real_turns

        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
        print(bots)
        # Affichage des résultats
        print("Bot Match Analysis Results:")
        print("------------------------------")
        print(f"Total games played: {total_games}")
        print(f"Average Real Turns: {total_real_turns / total_games:.2f}")
        print()

        for bot_name, stats in bots.items():
            total_bot_games = stats['games']
            white_wins_percentage = (stats['white_wins'] / total_bot_games) * 100
            black_wins_percentage = (stats['black_wins'] / total_bot_games) * 100
            draws_percentage = (stats['draws'] / total_bot_games) * 100

            print(f"Bot: {bot_name}")
            print(f"  - White wins: {stats['white_wins']} ({white_wins_percentage:.2f}%)")
            print(f"  - Black wins: {stats['black_wins']} ({black_wins_percentage:.2f}%)")
            print(f"  - Draws: {stats['draws']} ({draws_percentage:.2f}%)")
            print()


# Appel de la méthode
analyze_game_results(csv_file)