# performance_analyzer.py
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import pandas as pd
import time
import random
from ai_minimax import get_best_move_minimax
from ai_alpha_beta import get_best_move_alpha_beta
from utils import check_winner, get_empty_cells

class PerformanceAnalyzer:
    def __init__(self, db_path="tic_tac_toe.db"):
        """Initialize the performance analyzer with the database path"""
        self.db_path = db_path
        
    def _get_connection(self):
        """Get a database connection"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
            
    def run_algorithm_comparison(self, num_games=10):
        """
        Run a comparison between Minimax and Alpha-Beta for a specified number of games
        Records timing data for each move in each game
        """
        print(f"Running {num_games} game rounds to compare algorithms...")
        
        # Track move times for both algorithms
        minimax_times = []
        alphabeta_times = []
        
        for game_round in range(1, num_games + 1):
            print(f"Game round {game_round}/{num_games}")
            
            # Create a new game board
            board = [[" " for _ in range(5)] for _ in range(5)]
            
            # Make some random moves to create different board states
            num_initial_moves = random.randint(3, 8)
            players = ["X", "O"]
            
            for _ in range(num_initial_moves):
                empty_cells = get_empty_cells(board)
                if not empty_cells:
                    break
                    
                row, col = random.choice(empty_cells)
                player = players[_ % 2]
                board[row][col] = player
            
            # Test both algorithms on the same board state
            # Measure Minimax time
            start_time = time.time()
            minimax_move = get_best_move_minimax(board, "O")
            minimax_time = time.time() - start_time
            minimax_times.append(minimax_time)
            
            # Measure Alpha-Beta time
            start_time = time.time()
            alphabeta_move = get_best_move_alpha_beta(board, "O")
            alphabeta_time = time.time() - start_time
            alphabeta_times.append(alphabeta_time)
            
            print(f"  Minimax time: {minimax_time:.6f}s, Alpha-Beta time: {alphabeta_time:.6f}s")
            
            # Verify that both algorithms return the same move
            if minimax_move != alphabeta_move:
                print(f"  Warning: Different moves selected! Minimax: {minimax_move}, Alpha-Beta: {alphabeta_move}")
        
        # Store the results in a pandas DataFrame
        results = pd.DataFrame({
            'Game Round': range(1, num_games + 1),
            'Minimax Time (s)': minimax_times,
            'Alpha-Beta Time (s)': alphabeta_times
        })
        
        return results
            
    def get_algorithm_comparison_from_db(self):
        """
        Retrieve algorithm comparison data from the database
        Returns a pandas DataFrame with the comparison data
        """
        conn = self._get_connection()
        if not conn:
            return None
            
        try:
            query = """
            SELECT 
                g.game_id,
                p.player_name,
                am.algorithm,
                am.move_number,
                am.move_time
            FROM games g
            JOIN players p ON g.player_id = p.player_id
            JOIN ai_moves am ON g.game_id = am.game_id
            ORDER BY g.game_id, am.move_number
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving algorithm data: {e}")
            if conn:
                conn.close()
            return None
    
    def generate_time_comparison_chart(self, data=None, save_path=None):
        """
        Generate a chart comparing the time performance of both algorithms
        
        Parameters:
        - data: DataFrame with algorithm comparison data (optional)
        - save_path: Path to save the chart image (optional)
        
        Returns:
        - Path to saved chart if save_path is provided, otherwise None
        """
        if data is None:
            # Run a new comparison if no data is provided
            data = self.run_algorithm_comparison()
            
        if data is None or data.empty:
            print("No data available for chart generation")
            return None
            
        plt.figure(figsize=(12, 6))
        
        # Plot time comparison
        plt.subplot(1, 2, 1)
        plt.plot(data['Game Round'], data['Minimax Time (s)'], 'b-o', label='Minimax')
        plt.plot(data['Game Round'], data['Alpha-Beta Time (s)'], 'r-o', label='Alpha-Beta')
        plt.title('Algorithm Performance Comparison')
        plt.xlabel('Game Round')
        plt.ylabel('Time (seconds)')
        plt.legend()
        plt.grid(True)
        
        # Plot time difference
        plt.subplot(1, 2, 2)
        data['Time Difference (s)'] = data['Minimax Time (s)'] - data['Alpha-Beta Time (s)']
        plt.bar(data['Game Round'], data['Time Difference (s)'], color='green')
        plt.title('Time Difference (Minimax - Alpha-Beta)')
        plt.xlabel('Game Round')
        plt.ylabel('Time Difference (seconds)')
        plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
            return save_path
        else:
            plt.show()
            return None
            
    def generate_statistics_report(self, data=None):
        """
        Generate a statistical report on algorithm performance
        
        Parameters:
        - data: DataFrame with algorithm comparison data (optional)
        
        Returns:
        - String containing the statistical report
        """
        if data is None:
            # Run a new comparison if no data is provided
            data = self.run_algorithm_comparison()
            
        if data is None or data.empty:
            return "No data available for statistical analysis"
            
        # Calculate statistics
        minimax_stats = {
            'Mean': data['Minimax Time (s)'].mean(),
            'Median': data['Minimax Time (s)'].median(),
            'Std Dev': data['Minimax Time (s)'].std(),
            'Min': data['Minimax Time (s)'].min(),
            'Max': data['Minimax Time (s)'].max()
        }
        
        alphabeta_stats = {
            'Mean': data['Alpha-Beta Time (s)'].mean(),
            'Median': data['Alpha-Beta Time (s)'].median(),
            'Std Dev': data['Alpha-Beta Time (s)'].std(),
            'Min': data['Alpha-Beta Time (s)'].min(),
            'Max': data['Alpha-Beta Time (s)'].max()
        }
        
        # Format the report
        report = "Algorithm Performance Statistics\n"
        report += "==============================\n\n"
        
        report += "Minimax Algorithm:\n"
        report += f"  Mean Time: {minimax_stats['Mean']:.6f} seconds\n"
        report += f"  Median Time: {minimax_stats['Median']:.6f} seconds\n"
        report += f"  Standard Deviation: {minimax_stats['Std Dev']:.6f} seconds\n"
        report += f"  Min Time: {minimax_stats['Min']:.6f} seconds\n"
        report += f"  Max Time: {minimax_stats['Max']:.6f} seconds\n\n"
        
        report += "Alpha-Beta Algorithm:\n"
        report += f"  Mean Time: {alphabeta_stats['Mean']:.6f} seconds\n"
        report += f"  Median Time: {alphabeta_stats['Median']:.6f} seconds\n"
        report += f"  Standard Deviation: {alphabeta_stats['Std Dev']:.6f} seconds\n"
        report += f"  Min Time: {alphabeta_stats['Min']:.6f} seconds\n"
        report += f"  Max Time: {alphabeta_stats['Max']:.6f} seconds\n\n"
        
        # Calculate improvement percentage
        if minimax_stats['Mean'] > 0:
            improvement = (minimax_stats['Mean'] - alphabeta_stats['Mean']) / minimax_stats['Mean'] * 100
            report += f"Alpha-Beta improves performance by {improvement:.2f}% on average\n"
        
        return report

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    results = analyzer.run_algorithm_comparison(10)
    analyzer.generate_time_comparison_chart(results, "algorithm_comparison.png")
    report = analyzer.generate_statistics_report(results)
    print(report)
    
    # Save the report to a file
    with open("algorithm_statistics.txt", "w") as f:
        f.write(report)