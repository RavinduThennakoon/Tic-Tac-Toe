# test_game.py

import unittest
import copy
from utils import check_winner, get_empty_cells
from ai_minimax import get_best_move_minimax
from ai_alpha_beta import get_best_move_alpha_beta


class TestGameLogic(unittest.TestCase):
    
    def test_check_winner_horizontal(self):
        board = [["X", "X", "X", "X", "X"],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "]]
        self.assertTrue(check_winner(board, "X"))
        
    def test_check_winner_vertical(self):
        board = [[" ", " ", "O", " ", " "],
                 [" ", " ", "O", " ", " "],
                 [" ", " ", "O", " ", " "],
                 [" ", " ", "O", " ", " "],
                 [" ", " ", "O", " ", " "]]
        self.assertTrue(check_winner(board, "O"))
        
    def test_check_winner_diagonal1(self):
        board = [["X", " ", " ", " ", " "],
                 [" ", "X", " ", " ", " "],
                 [" ", " ", "X", " ", " "],
                 [" ", " ", " ", "X", " "],
                 [" ", " ", " ", " ", "X"]]
        self.assertTrue(check_winner(board, "X"))
        
    def test_check_winner_diagonal2(self):
        board = [[" ", " ", " ", " ", "O"],
                 [" ", " ", " ", "O", " "],
                 [" ", " ", "O", " ", " "],
                 [" ", "O", " ", " ", " "],
                 ["O", " ", " ", " ", " "]]
        self.assertTrue(check_winner(board, "O"))
        
    def test_no_winner(self):
        board = [["X", "O", "X", "O", "X"],
                 ["O", "X", "O", "X", "O"],
                 ["X", "O", "X", "O", "X"],
                 ["O", "X", "O", "X", "O"],
                 ["X", "O", "X", "O", " "]]
        self.assertFalse(check_winner(board, "X"))
        self.assertFalse(check_winner(board, "O"))
        
    def test_get_empty_cells(self):
        board = [["X", "O", " "],
                 [" ", "X", "O"],
                 ["O", " ", "X"]]
        empty_cells = get_empty_cells(board)
        self.assertEqual(len(empty_cells), 3)
        self.assertIn((0, 2), empty_cells)
        self.assertIn((1, 0), empty_cells)
        self.assertIn((2, 1), empty_cells)
        
    def test_minimax_finds_winning_move(self):
        # Test that minimax finds a winning move
        board = [[" ", " ", " ", " ", " "],
                 [" ", "X", "X", "X", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "]]
        # X needs one more to win in the second row
        move = get_best_move_minimax(board, "X")
        self.assertTrue(move == (1, 0) or move == (1, 4))
        
    def test_alpha_beta_finds_winning_move(self):
        # Test that alpha-beta pruning finds a winning move
        board = [[" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "],
                 ["O", "O", "O", "O", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "]]
        # O needs one more to win in the third row
        move = get_best_move_alpha_beta(board, "O")
        self.assertEqual(move, (2, 4))
        
    def test_algorithm_blocks_opponent(self):
        # Test that both algorithms block an opponent's winning move
        board = [[" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "],
                 ["X", "X", "X", "X", " "],
                 [" ", " ", " ", " ", " "],
                 [" ", " ", " ", " ", " "]]
        # O should block X's winning move
        move_minimax = get_best_move_minimax(board, "O")
        move_alpha_beta = get_best_move_alpha_beta(board, "O")
        # Both should block at position (2, 4)
        self.assertEqual(move_minimax, (2, 4))
        self.assertEqual(move_alpha_beta, (2, 4))
    
    def test_draw_condition(self):
        # Test a nearly-full board with no winners
        board = [["X", "O", "X", "O", "X"],
                 ["O", "X", "O", "X", "O"],
                 ["X", "O", "X", "O", "X"],
                 ["O", "X", "O", "X", "O"],
                 ["X", "O", "X", "O", " "]]
        # Last empty cell
        self.assertEqual(len(get_empty_cells(board)), 1)
        self.assertEqual(get_empty_cells(board)[0], (4, 4))


if __name__ == "__main__":
    unittest.main()