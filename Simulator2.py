from PyQt6 import QtWidgets, QtGui
from PyQt6 import uic

from Bots.ChessBotList import *
from ChessRules import *
from ParallelPlayer import *

import numpy as np
import csv
import os


set_nbr_turn_to_play = 700
set_max_time_budget = 1.0

set_players_AI = {
            'w': CHESS_BOT_LIST['RandomBot'],  # Bot for 'w'
            'b': CHESS_BOT_LIST['MinMaxBot']  # Bot for 'b'
        }
set_csv_file = "game_results2.csv"

# Wrap up for QApplication
class ChessApp(QtWidgets.QApplication):

    def __init__(self):
        super().__init__([])

    def start(self):
        arena = ChessArena()
        arena.show()
        arena.start()  # Configure le plateau
        arena.launch_game()  # Lance la partie immédiatement
        self.exec()

# Main window to handle the chess board
CHESS_PIECES = ["k", "q", "n", "b", "r", "p"]
CHESS_COLOR = {
    "w": [QtGui.QColor(255, 255, 255), QtGui.QColor(0, 0, 0)],
    "b": [QtGui.QColor(0, 0, 0), QtGui.QColor(255, 255, 255)],
    "r": [QtGui.QColor(200, 0, 0), QtGui.QColor(50, 255, 255)],
    "y": [QtGui.QColor(200, 200, 0), QtGui.QColor(50, 50, 255)],
}
COLOR_NAMES = {"w": "White", "b": "Black", "r": "Red", "y": "Yellow"}
CHESS_PIECES_NAMES = {
    "k": "King",
    "q": "Queen",
    "n": "Knight",
    "b": "Bishop",
    "r": "Rook",
    "p": "Pawn",
}



class ChessArena(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.playersList = None
        uic.loadUi("Data/UI.ui", self)

        # Render for chess board
        self.chess_scene = QtWidgets.QGraphicsScene()
        self.chess_scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("white")))
        self.chessboardView.setScene(self.chess_scene)

        self.loadBoardButton.clicked.connect(self.select_and_load_board)

        self.load_assets()
        self.current_player = None

        # Add variables to track game statistics
        self.start_time = None  # Used to track the start time of the game
        self.game_start_real_time = QtCore.QTime.currentTime()

    def add_system_message(self, message):
        msg_widget = QtWidgets.QLabel(message)
        msg_widget.setWordWrap(True)
        print("[SYS]", message)
        self.systemMessagesLayout.addWidget(msg_widget)
        self.systemMessagesBox = QtWidgets.QScrollArea()
        self.systemMessagesBox.verticalScrollBar().setSliderPosition(
            self.systemMessagesBox.verticalScrollBar().maximum()
        )

    # Start the bot simulation
    def launch_game(self):
        self.add_system_message("# Starting new Game #")
        self.start_time = QtCore.QTime.currentTime()  # Start time when game begins
        # Assign bots directly
        self.players_AI = set_players_AI

        for cid, (color, bot) in enumerate(self.players_AI.items()):
            self.add_system_message(f"AI #{cid} ({COLOR_NAMES[color]}) = {bot.__name__}")


        self.nbr_turn_to_play = set_nbr_turn_to_play
        self.max_time_budget = set_max_time_budget

        self.play_next_turn()

    def play_next_turn(self):
        if self.current_player is not None:
            print("Cannot launch new turn while already processing")
            return

        if self.nbr_turn_to_play == 0:
            print("No more play to do")
            self.end_game(None)
            return

        next_player_color = self.player_order[0:3]

        rotated_view_board = np.rot90(self.board, int(next_player_color[2]))
        self.current_player = ParallelTurn(
            self.players_AI[next_player_color[1]],
            self.player_order,
            rotated_view_board,
            self.max_time_budget,
        )
        self.current_player.setTerminationEnabled(True)
        self.current_player.start()

        QtCore.QTimer.singleShot(
            int(self.max_time_budget * 1000 * 1.05), self.end_turn
        )

    def end_turn(self):
        all_other_defeated = False

        if self.current_player.isRunning():
            self.current_player.terminate()
            self.add_system_message(
                COLOR_NAMES[self.current_player.color] + " did not end their turn"
            )
        else:
            player_color = self.current_player.color
            next_play = self.current_player.next_move

            if not move_is_valid(self.player_order, next_play, self.current_player.board):
                self.add_system_message(
                    COLOR_NAMES[player_color]
                    + " invalid move from "
                    + str(next_play[0])
                    + " to "
                    + str(next_play[1])
                )
                return

            self.add_system_message(
                COLOR_NAMES[player_color]
                + " moved "
                + CHESS_PIECES_NAMES[
                    self.current_player.board[next_play[0][0], next_play[0][1]][0]
                ]
                + " from "
                + str(next_play[0])
                + " to "
                + str(next_play[1])
            )

            if self.current_player.board[next_play[1][0], next_play[1][1]] != '':
                self.add_system_message(
                    COLOR_NAMES[player_color]
                    + " captured "
                    + COLOR_NAMES[
                        self.current_player.board[next_play[1][0], next_play[1][1]][1]
                    ]
                    + " "
                    + CHESS_PIECES_NAMES[
                        self.current_player.board[next_play[1][0], next_play[1][1]][0]
                    ]
                )

            self.current_player.board[next_play[1][0], next_play[1][1]] = self.current_player.board[
                next_play[0][0], next_play[0][1]
            ]
            self.current_player.board[next_play[0][0], next_play[0][1]] = ''

            if (
                    self.current_player.board[next_play[1][0], next_play[1][1]][0] == 'p'
                    and next_play[1][0] == self.current_player.board.shape[0] - 1
            ):
                self.current_player.board[next_play[1][0], next_play[1][1]] = (
                        "q"
                        + self.current_player.board[next_play[1][0], next_play[1][1]][1]
                )

            all_other_defeated = True
            for row in self.board:
                for elem in row:
                    if len(elem) > 0 and elem[0] == 'k':
                        if int(self.player_order[self.player_order.find(elem[1]) - 1]) != int(
                                self.current_player.team
                        ):
                            all_other_defeated = False

        self.current_player = None
        self.setup_board()

        self.player_order = self.player_order[3:] + self.player_order[0:3]
        self.nbr_turn_to_play -= 1

        if all_other_defeated:
            self.end_game(player_color)
        else:
            self.play_next_turn()

    def end_game(self, winner):
        if winner is None:
            self.add_system_message("# Match ended in a draw")
        else:
            self.add_system_message("# " + str(COLOR_NAMES[winner]) + " won the match")

        # Save game results to CSV
        self.save_game_result(winner)

        self.close()  # Ferme l'interface
        QtWidgets.QApplication.quit()  # Quitte l'application

    def save_game_result(self, winner):
        # Prepare data for CSV
        player1_name = [bot for bot in CHESS_BOT_LIST if CHESS_BOT_LIST[bot] == self.players_AI['w']][0]
        player2_name = [bot for bot in CHESS_BOT_LIST if CHESS_BOT_LIST[bot] == self.players_AI['b']][0]
        winner_name = COLOR_NAMES[winner] if winner else "Draw"
        number_of_turns = set_nbr_turn_to_play  # Total turns played
        time_per_turn = set_max_time_budget # Each turn time limit
        real_turns = self.nbr_turn_to_play  # Total turns played

        # CSV file path
        csv_file = set_csv_file

        # Check if file exists, if not, create it and add headers
        file_exists = os.path.exists(csv_file)
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # Write the header only once
                writer.writerow(['White', 'Black', 'Winner', 'Total Turns', 'Time per Turn (s)', 'Real Turns'])

            # Write game data
            writer.writerow([player1_name, player2_name, winner_name, number_of_turns, time_per_turn, real_turns])

    def select_and_load_board(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select board", "C:\\Users\\Louis\\Desktop\\ISChess\\Data\\maps", "Board File (*.brd)"
        )

        if not path[0]:
            return

        self.board = self.load_board(path[0])
        if self.board is None:
            return

        self.setup_board()

    def load_board(self, path):
        try:
            with open(path, "r") as f:
                data = f.read()
                lines = data.split("\n")
                self.player_order = lines[0]
                elems = [l.replace("--", "").split(",") for l in lines[1:]]

                while len(elems) > 0 and len(elems[-1]) == 0:
                    del elems[-1]

                for l in elems:
                    if len(l) != len(elems[0]):
                        return None

                return np.array(elems, dtype='O')
        except Exception as e:
            print(e)
            return None

    def load_assets(self):
        self.white_square = QtGui.QPixmap("Data/assets/light_square.png")
        self.black_square = QtGui.QPixmap("Data/assets/dark_square.png")

        self.pieces_imgs = {}
        for p in CHESS_PIECES:
            image = QtGui.QImage("Data/assets/" + p + ".png")
            self.pieces_imgs[p] = image

    def setup_board(self):
        for i in reversed(self.chess_scene.items()):
            self.chess_scene.removeItem((i))

        self.piece_items = np.array([[None] * self.board.shape[1]] * self.board.shape[0], dtype=object)
        self.colored_piece_pixmaps = {}

        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):
                square_color = self.white_square if (x + y) % 2 == 0 else self.black_square
                square_item = self.chess_scene.addPixmap(square_color)
                square_item.setPos(
                    QtCore.QPointF(square_color.size().width() * y, square_color.size().height() * x)
                )

                if self.board[x, y] != '' and self.board[x, y] != 'XX':
                    player_piece = self.board[x, y][0]
                    player_color = self.board[x, y][1]

                    if player_color not in self.colored_piece_pixmaps:
                        self.colored_piece_pixmaps[player_color] = {}

                    if player_piece not in self.colored_piece_pixmaps[player_color]:
                        piece_img = self.pieces_imgs[player_piece]
                        copy = piece_img.copy()

                        def mix(Q1, Q2, f, a):
                            return QtGui.QColor(
                                int(Q1.red() * f + Q2.red() * (1 - f)),
                                int(Q1.green() * f + Q2.green() * (1 - f)),
                                int(Q1.blue() * f + Q2.blue() * (1 - f)),
                                a,
                            )

                        for px in range(copy.size().width()):
                            for py in range(copy.size().height()):
                                copy.setPixelColor(
                                    px,
                                    py,
                                    mix(
                                        CHESS_COLOR[player_color][0],
                                        CHESS_COLOR[player_color][1],
                                        copy.pixelColor(px, py).red() / 255.0,
                                        copy.pixelColor(px, py).alpha(),
                                    ),
                                )

                        self.colored_piece_pixmaps[player_color][player_piece] = QtGui.QPixmap().fromImage(copy)

                    self.piece_items[x, y] = self.chess_scene.addPixmap(
                        self.colored_piece_pixmaps[player_color][player_piece]
                    )
                    self.piece_items[x, y].setPos(
                        QtCore.QPointF(
                            square_color.size().width() * y, square_color.size().height() * x
                        )
                    )

        self.chessboardView.fitInView(self.chess_scene.sceneRect())

    def start(self):
        self.board = self.load_board("Data/maps/default.brd")
        self.setup_board()
        self.chess_scene.update()

# Main execution
if __name__ == "__main__":

    # Nombre de parties à jouer
    total_games = 2000
    app = ChessApp()  # Create only one QApplication instance

    for game_number in range(total_games):
        print(f"Starting game {game_number + 1} of {total_games}")
        app.start()  # Start each game sequentially

    print("Finished all games.")


    def analyze_game_results(csv_file=set_csv_file):
        # Dictionnaires pour suivre les statistiques
        bots = {}
        total_games = 0
        white_wins = {}
        black_wins = {}
        draws = 0
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
                        bots[black_bot]['black_wins'] += 1
                    elif winner == "Black":
                        bots[black_bot]['black_wins'] += 1
                        bots[white_bot]['white_wins'] += 1
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
    analyze_game_results(set_csv_file)
