# gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QMessageBox
)
import time  # For potential delays or timing
from ai_minimax import get_best_move_minimax
from ai_alpha_beta import get_best_move_alpha_beta
from utils import check_winner, get_empty_cells
from database import save_result, save_move_time



class TicTacToeUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(100, 100, 600, 600)
        self.board = [[" "]*5 for _ in range(5)]
        self.buttons = [[None]*5 for _ in range(5)]
        self.player_name = ""
        self.current_turn = "Player"
        self.init_ui()
        self.setStyleSheet("""
    QWidget {
        background-color: #0e6187;
    }
    QPushButton {
        background-color: black;
        color: white;
        font-weight: bold;
        font-size: 16px;
        border: 2px solid #107caf;
    }
    QLineEdit, QComboBox {
        background-color: #0e6187;
        color: white;
        font-weight:bold;
        border: 1px solid black;
    }
    QLabel {
        color: white;
        font-weight:bold;
    }
""")
       
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Player name input
        name_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Algorithm choice
        algo_layout = QHBoxLayout()
        self.algo_choice = QComboBox()
        self.algo_choice.addItems(["Minimax", "Alpha-Beta"])
        self.algo_choice.setStyleSheet("color:white")
        algo_layout.addWidget(QLabel("AI Algorithm:"))
        algo_layout.addWidget(self.algo_choice)
        main_layout.addLayout(algo_layout)


#====================================================================================
        # Start button
        self.start_btn = QPushButton("Start Game")
        self.start_btn.clicked.connect(self.start_game)
        main_layout.addWidget(self.start_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Reset Game")
        self.refresh_btn.clicked.connect(self.refresh_game)
        main_layout.addWidget(self.refresh_btn)


        self.game_started = False  
        # Game board (grid)
        self.grid = QGridLayout()
        for row in range(5):
            for col in range(5):
                btn = QPushButton(" ")
                btn.setFixedSize(80, 80)
                btn.clicked.connect(lambda _, r=row, c=col:  self.button_clicked(r, c))
                self.buttons[row][col] = btn
                self.grid.addWidget(btn, row, col)
        main_layout.addLayout(self.grid)

        # Status
        self.status_label = QLabel("Press 'Start Game' to begin.")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
#================================================================================================================
    def button_clicked(self, row, col):
     if not self.game_started :
        QMessageBox.information(self, "Start Game", "Please click the Start button to begin the game!")
        return
     
     self.player_name = self.name_input.text().strip()  # Get the latest name
     if not self.player_name:
        QMessageBox.warning(self, "Name Required", "Please enter your name before making a move!")
        return
     self.make_move(row, col)
#==================================================================================================================

    def start_game(self):
        self.game_started = True
        self.player_name = self.name_input.text().strip()

        if not self.player_name:
            QMessageBox.warning(
                self,
                "Name Required",
                "Please enter your Name before starting the game",
                QMessageBox.Ok
            )
            return

        self.board = [[" "]*5 for _ in range(5)]
        for row in range(5):
            for col in range(5):
                self.buttons[row][col].setText(" ")
                self.buttons[row][col].setEnabled(True)
        self.player_name = self.name_input.text()
        self.current_turn = "Player"
        self.status_label.setText("Game Started! Your move.")
#=======================================================================================
    def refresh_game(self):
        self.player_name = self.name_input.text().strip()
 

        self.name_input.clear() 

        self.board = [[" "]*5 for _ in range(5)]
        for row in range(5):
            for col in range(5):
             self.buttons[row][col].setText(" ")
             self.buttons[row][col].setEnabled(True)
        self.buttons[row][col].setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        self.current_turn = "Player"
        self.game_started = True
        self.status_label.setText("Game resetted!")

#==============================================================================================================
    def make_move(self, row, col):
        if self.board[row][col] != " " or self.current_turn != "Player":
            return
        self.board[row][col] = "X"
        self.buttons[row][col].setText("X")
        self.buttons[row][col].setStyleSheet("color: red; font-weight: bold; font-size: 40px;")
        self.buttons[row][col].setEnabled(False)
        self.current_turn = "AI"
        self.status_label.setText("AI is thinking...")
        self.update()

          # Check if the player won
        if check_winner(self.board, "X"):
            self.game_over("You win!")
            save_result(self.player_name, "Win")
            QMessageBox.information(self, "Game Over", "You win!")
            return
        elif not get_empty_cells(self.board):
            self.game_over("It's a draw!")
            save_result(self.player_name, "Draw")
            QMessageBox.information(self, "Game Over", "Draw!")
            return

        # AI's turn
        selected_algo = self.algo_choice.currentText()
        start_time = time.time()
        if selected_algo == "Minimax":
            ai_move = get_best_move_minimax(self.board, "O")
            algo_name = "Minimax"
        elif selected_algo == "Alpha-Beta":
            ai_move = get_best_move_alpha_beta(self.board, "O")
            algo_name = "Alpha-Beta"
        else:
            ai_move = None
            algo_name = "None"  # Should not happen

        move_time = time.time() - start_time

        if ai_move:
            ai_row, ai_col = ai_move
            self.board[ai_row][ai_col] = "O"
            self.buttons[ai_row][ai_col].setText("O")
            self.buttons[ai_row][ai_col].setStyleSheet("color: yellow; font-weight: bold; font-size: 40px;")
            self.buttons[ai_row][ai_col].setEnabled(False)
            save_move_time(self.player_name, algo_name, move_time)

            # Check if AI won
            if check_winner(self.board, "O"):
                self.game_over("AI wins!")
                save_result(self.player_name, "Loss")
                QMessageBox.information(self, "Game Over", "You Loss")
                return
            elif not get_empty_cells(self.board):
                self.game_over("It's a draw!")
                save_result(self.player_name, "Draw the Match")
                return

            self.current_turn = "Player"
            self.status_label.setText("Your turn.")
        else:
            self.status_label.setText("AI couldn't make a move (Error).")

    def game_over(self, message):
        self.status_label.setText(message)
        for row in range(5):
            for col in range(5):
                self.buttons[row][col].setEnabled(False)

        # TODO: Hook AI move here in next step

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeUI()
    window.show()
    sys.exit(app.exec_())
