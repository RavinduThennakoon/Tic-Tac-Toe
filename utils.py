# utils.py

def get_empty_cells(board):
    empty_cells = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == ' ':
                empty_cells.append((row, col))
    return empty_cells

def check_winner(board, player):
    size = len(board)

    # Check rows and columns
    for i in range(size):
        if all(cell == player for cell in board[i]):
            return True
        if all(board[j][i] == player for j in range(size)):
            return True

    # Check diagonals
    if all(board[i][i] == player for i in range(size)):
        return True
    if all(board[i][size - i - 1] == player for i in range(size)):
        return True

    return False
