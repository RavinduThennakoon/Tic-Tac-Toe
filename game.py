# enhanced_game.py - Improved version of game.py with better error handling

import time
import sys
from ai_minimax import get_best_move_minimax
from ai_alpha_beta import get_best_move_alpha_beta
from utils import check_winner, get_empty_cells
from database import save_result, save_move_time


def print_board(board):
    try:
        for row in board:
            print(" | ".join(row))
            print("-" * 19)
    except Exception as e:
        print(f"Error displaying board: {str(e)}")


def validate_input(value, min_val, max_val, input_type=""):
    """Validate numeric input is within range"""
    try:
        value = int(value)
        if min_val <= value <= max_val:
            return True, value
        else:
            print(f"{input_type} must be between {min_val} and {max_val}.")
            return False, None
    except ValueError:
        print(f"Invalid {input_type}. Please enter a number.")
        return False, None


def start_game():
    try:
        
        name = input("Enter your Name: ")
        if not name.strip():
            name = "Anonymous"
            print("Using 'Anonymous' as player name.")
        
        algo_choice = input("Choose AI Algorithm: 1. Minimax 2. Alpha-Beta: ")
        
        if algo_choice == '1':
            ai_function = get_best_move_minimax
            algo_name = "Minimax"
        elif algo_choice == '2':
            ai_function = get_best_move_alpha_beta
            algo_name = "Alpha-Beta"
        else:
            print("Invalid choice. Defaulting to Alpha-Beta.")
            ai_function = get_best_move_alpha_beta
            algo_name = "Alpha-Beta"
        
        board = [[" " for _ in range(5)] for _ in range(5)]
        player_turn = True
        
        while True:
            try:
                print_board(board)
                
                if check_winner(board, "X"):
                    print(f"Congratulations {name}! You win!")
                    save_result(name, "Win")
                    break
                elif check_winner(board, "O"):
                    print("AI wins!")
                    save_result(name, "Loss")
                    break
                elif not get_empty_cells(board):
                    print("It's a draw!")
                    save_result(name, "Draw")
                    break
                
                if player_turn:
                    move = input("Enter your move as row,col (0-4): ")
                    
                    try:
                        parts = move.split(',')
                        if len(parts) != 2:
                            print("Input must be in format 'row,col'. Try again.")
                            continue
                            
                        valid_row, row = validate_input(parts[0], 0, 4, "Row")
                        valid_col, col = validate_input(parts[1], 0, 4, "Column")
                        
                        if not (valid_row and valid_col):
                            continue
                            
                        if board[row][col] != " ":
                            print("Cell is already taken. Try again.")
                            
                            continue
                            
                        board[row][col] = "X"
                        player_turn = False
                    except Exception as e:
                        print(f"Error processing your move: {str(e)}. Try again.")
                        continue
                else:
                    print("AI is thinking...")
                    start_time = time.time()
                    
                    try:
                        ai_move = ai_function(board, "O")
                        move_time = time.time() - start_time
                        
                        if ai_move:
                            board[ai_move[0]][ai_move[1]] = "O"
                            print(f"AI placed O at position {ai_move[0]},{ai_move[1]}")
                            print(f"AI took {move_time:.4f} seconds to decide")
                            try:
                                save_move_time(name, algo_name, move_time)
                            except Exception as db_error:
                                print(f"Warning: Could not save move time to database: {str(db_error)}")
                        else:
                            print("No valid moves for AI. This shouldn't happen in Tic-Tac-Toe!")
                        player_turn = True
                    except Exception as ai_error:
                        print(f"AI encountered an error: {str(ai_error)}. Skipping AI's turn.")
                        player_turn = True
            
            except KeyboardInterrupt:
                print("\nGame interrupted. Exiting...")
                return
            except Exception as e:
                print(f"Unexpected error: {str(e)}. Continuing...")
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("Game terminated due to error.")


if __name__ == "__main__":
    start_game()