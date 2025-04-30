import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from ai_minimax import get_best_move_minimax
from ai_alpha_beta import get_best_move_alpha_beta
from utils import check_winner, get_empty_cells
import random

class AlgorithmBenchmark:
   
    def __init__(self):
        """Initialize the benchmark class"""
        self.results = {
            'board_fill': [],          # Percentage of board filled
            'minimax_time': [],        # Time taken by Minimax algorithm
            'alphabeta_time': [],      # Time taken by Alpha-Beta algorithm
            'nodes_minimax': [],       # Nodes evaluated by Minimax
            'nodes_alphabeta': [],     # Nodes evaluated by Alpha-Beta
            'move_quality_match': []   # Whether both algorithms chose the same move
        }
        
        # For tracking node counts
        self.minimax_nodes = 0
        self.alphabeta_nodes = 0
    
    def _reset_node_counters(self):
        """Reset node counters for a new benchmark run"""
        self.minimax_nodes = 0
        self.alphabeta_nodes = 0
    
    def _create_board_with_fill_percentage(self, fill_percentage):
        
        board = [[" " for _ in range(5)] for _ in range(5)]
        total_cells = 25
        cells_to_fill = int(total_cells * fill_percentage / 100)
        
        # Get all possible positions
        all_positions = [(i, j) for i in range(5) for j in range(5)]
        random.shuffle(all_positions)
        
        # Fill board with alternating X and O
        symbols = ["X", "O"]
        for i in range(cells_to_fill):
            row, col = all_positions[i]
            board[row][col] = symbols(["X","O"])#[i % 2]
        
        return board
    
    def _count_nodes_minimax(self, board, player):
        """Modified minimax that counts nodes explored"""
        def minimax_counter(board, depth, is_maximizing):
            nonlocal node_count
            node_count += 1
            
            opponent = "X" if player == "O" else "O"

            if check_winner(board, player):
                return 1
            elif check_winner(board, opponent):
                return -1
            elif not get_empty_cells(board) or depth >= 3:  # MAX_DEPTH = 3
                return 0

            if is_maximizing:
                best = -float("inf")
                for row, col in get_empty_cells(board):
                    board[row][col] = player
                    val = minimax_counter(board, depth + 1, False)
                    board[row][col] = " "
                    best = max(best, val)
                return best
            else:
                best = float("inf")
                for row, col in get_empty_cells(board):
                    board[row][col] = opponent
                    val = minimax_counter(board, depth + 1, True)
                    board[row][col] = " "
                    best = min(best, val)
                return best

        node_count = 0
        best_score = -float("inf")
        best_move = None
        for row, col in get_empty_cells(board):
            board[row][col] = player
            score = minimax_counter(board, 0, False)
            board[row][col] = " "
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        return best_move, node_count
    
    def _count_nodes_alphabeta(self, board, player):
        """Modified alpha-beta that counts nodes explored"""
        def alphabeta_counter(board, depth, alpha, beta, maximizing):
            nonlocal node_count
            node_count += 1
            
            opponent = "X" if player == "O" else "O"

            if check_winner(board, player):
                return 1
            elif check_winner(board, opponent):
                return -1
            elif not get_empty_cells(board) or depth >= 3:  # MAX_DEPTH = 3
                return 0

            if maximizing:
                max_eval = -float("inf")
                for row, col in get_empty_cells(board):
                    board[row][col] = player
                    eval = alphabeta_counter(board, depth + 1, alpha, beta, False)
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
                    eval = alphabeta_counter(board, depth + 1, alpha, beta, True)
                    board[row][col] = " "
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval

        node_count = 0
        best_score = -float("inf")
        best_move = None
        for row, col in get_empty_cells(board):
            board[row][col] = player
            score = alphabeta_counter(board, 0, -float("inf"), float("inf"), False)
            board[row][col] = " "
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        return best_move, node_count
    
    def run_benchmark(self, iterations=10):
       
        # Test different board fill percentages
        fill_percentages = [20, 40, 60, 80]
        
        for fill in fill_percentages:
            print(f"Testing with {fill}% board fill...")
            
            for i in range(iterations):
                board = self._create_board_with_fill_percentage(fill)
                
                # Skip boards where the game is already over
                if check_winner(board, "X") or check_winner(board, "O") or not get_empty_cells(board):
                    continue
                
                # Measure Minimax performance
                start_time = time.time()
                minimax_move, minimax_nodes = self._count_nodes_minimax(board, "O")
                minimax_time = time.time() - start_time
                
                # Measure Alpha-Beta performance
                start_time = time.time()
                alphabeta_move, alphabeta_nodes = self._count_nodes_alphabeta(board, "O")
                alphabeta_time = time.time() - start_time
                
                # Record results
                self.results['board_fill'].append(fill)
                self.results['minimax_time'].append(minimax_time)
                self.results['alphabeta_time'].append(alphabeta_time)
                self.results['nodes_minimax'].append(minimax_nodes)
                self.results['nodes_alphabeta'].append(alphabeta_nodes)
                self.results['move_quality_match'].append(minimax_move == alphabeta_move)
                
                print(f"  Iteration {i+1}/{iterations}: Minimax: {minimax_time:.6f}s ({minimax_nodes} nodes), "
                      f"Alpha-Beta: {alphabeta_time:.6f}s ({alphabeta_nodes} nodes)")
        
        # Convert results to DataFrame
        return pd.DataFrame(self.results)
    
    def plot_results(self, results=None, save_path=None):
      
        if results is None:
            results = pd.DataFrame(self.results)
        
        # Group by board fill percentage
        grouped = results.groupby('board_fill')
        
        # Calculate means for each fill percentage
        mean_results = grouped.mean()
        
        # Create figure with 2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Algorithm Performance Comparison', fontsize=16)
        
        # Plot 1: Execution Time Comparison
        axes[0, 0].plot(mean_results.index, mean_results['minimax_time'], 'b-o', label='Minimax')
        axes[0, 0].plot(mean_results.index, mean_results['alphabeta_time'], 'r-o', label='Alpha-Beta')
        axes[0, 0].set_title('Execution Time vs. Board Fill')
        axes[0, 0].set_xlabel('Board Fill (%)')
        axes[0, 0].set_ylabel('Time (seconds)')
        axes[0, 0].grid(True)
        axes[0, 0].legend()
        
        # Plot 2: Nodes Evaluated Comparison
        axes[0, 1].plot(mean_results.index, mean_results['nodes_minimax'], 'b-o', label='Minimax')
        axes[0, 1].plot(mean_results.index, mean_results['nodes_alphabeta'], 'r-o', label='Alpha-Beta')
        axes[0, 1].set_title('Nodes Evaluated vs. Board Fill')
        axes[0, 1].set_xlabel('Board Fill (%)')
        axes[0, 1].set_ylabel('Number of Nodes')
        axes[0, 1].grid(True)
        axes[0, 1].legend()
        
        # Plot 3: Relative Improvement
        improvement_time = (mean_results['minimax_time'] - mean_results['alphabeta_time']) / mean_results['minimax_time'] * 100
        improvement_nodes = (mean_results['nodes_minimax'] - mean_results['nodes_alphabeta']) / mean_results['nodes_minimax'] * 100
        
        axes[1, 0].bar(mean_results.index, improvement_time, color='green')
        axes[1, 0].set_title('Alpha-Beta Time Improvement (%)')
        axes[1, 0].set_xlabel('Board Fill (%)')
        axes[1, 0].set_ylabel('Improvement (%)')
        axes[1, 0].grid(True)
        
        # Plot 4: Nodes Saved by Alpha-Beta
        axes[1, 1].bar(mean_results.index, improvement_nodes, color='purple')
        axes[1, 1].set_title('Alpha-Beta Nodes Saved (%)')
        axes[1, 1].set_xlabel('Board Fill (%)')
        axes[1, 1].set_ylabel('Nodes Saved (%)')
        axes[1, 1].grid(True)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        if save_path:
            plt.savefig(save_path)
            print(f"Benchmark plot saved to {save_path}")
        else:
            plt.show()
        
        # Print summary statistics
        print("\nPerformance Summary:")
        print(f"Average Minimax Time: {mean_results['minimax_time'].mean():.6f} seconds")
        print(f"Average Alpha-Beta Time: {mean_results['alphabeta_time'].mean():.6f} seconds")
        print(f"Average Time Improvement: {improvement_time.mean():.2f}%")
        print(f"Average Nodes Saved: {improvement_nodes.mean():.2f}%")
        
        return fig

if __name__ == "__main__":
    # Run benchmark
    benchmark = AlgorithmBenchmark()
    results = benchmark.run_benchmark(iterations=10)
    
    # Save results to CSV
    results.to_csv("benchmark_results.csv", index=False)
    print("Benchmark results saved to benchmark_results.csv")
    
    # Plot and save results
    benchmark.plot_results(results, "algorithm_benchmark.png")