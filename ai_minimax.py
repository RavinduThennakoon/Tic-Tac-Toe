# ai_minimax.py
from utils import get_empty_cells, check_winner
MAX_DEPTH =3

def get_best_move_minimax(board, player):
    def minimax(board, depth, is_maximizing):
        opponent = "X" if player == "O" else "O"

        if check_winner(board, player):
            return 1
        elif check_winner(board, opponent):
            return -1
        elif not get_empty_cells(board) or depth >= MAX_DEPTH:
            return 0

        if is_maximizing:
            best = -float("inf")
            for row, col in get_empty_cells(board):
                board[row][col] = player
                val = minimax(board, depth + 1, False)
                board[row][col] = " "
                best = max(best, val)
            return best
        else:
            best = float("inf")
            for row, col in get_empty_cells(board):
                board[row][col] = opponent
                val = minimax(board, depth + 1, True)
                board[row][col] = " "
                best = min(best, val)
            return best

    best_score = -float("inf")
    best_move = None
    for row, col in get_empty_cells(board):
        board[row][col] = player
        score = minimax(board, 0, False)
        board[row][col] = " "
        if score > best_score:
            best_score = score
            best_move = (row, col)

    return best_move
