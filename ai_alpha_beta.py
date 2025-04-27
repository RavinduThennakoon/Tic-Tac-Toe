# ai_alpha_beta.py
from utils import get_empty_cells, check_winner
MAX_DEPTH = 3

def get_best_move_alpha_beta(board, player):
    def alphabeta(board, depth, alpha, beta, maximizing):
        opponent = "X" if player == "O" else "O"

        if check_winner(board, player):
            return 1
        elif check_winner(board, opponent):
            return -1
        elif not get_empty_cells(board) or depth >= MAX_DEPTH:
            return 0

        if maximizing:
            max_eval = -float("inf")
            for row, col in get_empty_cells(board):
                board[row][col] = player
                eval = alphabeta(board, depth + 1, alpha, beta, False)
                board[row][col] = " "
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for row, col in get_empty_cells(board):
                board[row][col] = opponent
                eval = alphabeta(board, depth + 1, alpha, beta, True)
                board[row][col] = " "
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    best_score = -float("inf")
    best_move = None
    for row, col in get_empty_cells(board):
        board[row][col] = player
        score = alphabeta(board, 0, -float("inf"), float("inf"), False)
        board[row][col] = " "
        if score > best_score:
            best_score = score
            best_move = (row, col)

    return best_move
