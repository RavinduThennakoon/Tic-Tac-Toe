import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# Database connection with error handling
def get_db_connection():
    try:
        conn = sqlite3.connect("tic_tac_toe.db")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise


def initialize_database():
    """Initialize database with proper schema and validation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create players Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        #Crate results Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            result TEXT CHECK(result IN ('Win', 'Loss', 'Draw')),
            game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
        ''')
        #Create ai_algorithms Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_algorithms (
            algorithm_id INTEGER PRIMARY KEY,
            algorithm_name TEXT NOT NULL UNIQUE
        )
        ''')
        #Create ai_timings Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_timings (
            timing_id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            algorithm_id INTEGER NOT NULL,
            move_time REAL NOT NULL,
            move_number INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (algorithm_id) REFERENCES ai_algorithms(algorithm_id)
        )
        ''')
        
        # Insert default algorithms
        cursor.execute("INSERT OR IGNORE INTO ai_algorithms (algorithm_id, algorithm_name) VALUES (1, 'Minimax')")
        cursor.execute("INSERT OR IGNORE INTO ai_algorithms (algorithm_id, algorithm_name) VALUES (2, 'Alpha-Beta')")
        
        conn.commit()
        print("Database initialized successfully")
        return conn
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise

#==========================================================Game History===========================================================
def get_game_history():
    """Retrieve complete game history from database"""
    conn = None  # Initialize here to avoid UnboundLocalError
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.result_id as game_id,
                p.player_name,
                r.result,
                r.game_date,
                COUNT(at.timing_id) as moves_count
            FROM results r
            JOIN players p ON r.player_id = p.player_id
            LEFT JOIN ai_timings at ON r.result_id = at.game_id
            GROUP BY r.result_id, p.player_name, r.result, r.game_date
            ORDER BY r.game_date ASC
            LIMIT 50;
        """)
        
        history_data = cursor.fetchall()
        return history_data

    except sqlite3.Error as e:
        print(f"Error fetching game history: {e}")
        return []
        
    finally:
        if conn:
            conn.close()

#=======================================================================================================================

def get_or_create_player(player_name):
    """Get or create player ID from name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if player exists
        cursor.execute("SELECT player_id FROM players WHERE player_name = ?", (player_name,))
        player = cursor.fetchone()
        
        if player:
            return player[0]
        else:
            # Create new player
            cursor.execute("INSERT INTO players (player_name) VALUES (?)", (player_name,))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Player creation error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_algorithm_id(algorithm_name):
    """Get algorithm ID from name"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT algorithm_id FROM ai_algorithms WHERE algorithm_name = ?", (algorithm_name,))
        algorithm = cursor.fetchone()
        
        if algorithm:
            return algorithm[0]
        else:
            # Fallback to default
            return 1  # Default to Minimax
    except sqlite3.Error as e:
        print(f"Algorithm lookup error: {e}")
        return 1  # Default to Minimax
    finally:
        if conn:
            conn.close()


def get_new_game_id():
    """Generate a new game ID based on timestamp"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(game_id) FROM ai_timings")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            return 1
        else:
            return max_id + 1
    except sqlite3.Error as e:
        print(f"Game ID generation error: {e}")
        return int(datetime.now().timestamp())  # Fallback
    finally:
        if conn:
            conn.close()


# Current game information
current_game_id = None
current_player_id = None
current_algorithm_id = None
current_move_number = 0


def start_new_game(player_name, algorithm_name):
    """Initialize a new game session"""
    global current_game_id, current_player_id, current_algorithm_id, current_move_number
    
    current_player_id = get_or_create_player(player_name)
    current_algorithm_id = get_algorithm_id(algorithm_name)
    current_game_id = get_new_game_id()
    current_move_number = 0
    
    return current_game_id


def save_result(player_name, result):
    """Save game result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        player_id = get_or_create_player(player_name)
        
        cursor.execute(
            "INSERT INTO results (player_id, result) VALUES (?, ?)",
            (player_id, result)
        )
        
        conn.commit()
        print(f"Result saved to database: {player_name} - {result}")
    except sqlite3.Error as e:
        print(f"Error saving result: {e}")
    finally:
        if conn:
            conn.close()


def save_move_time(player_name, algorithm, time_taken):
    """Save AI move time to database"""
    global current_game_id, current_player_id, current_algorithm_id, current_move_number
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure we have valid IDs
        if current_player_id is None:
            current_player_id = get_or_create_player(player_name)
        
        if current_algorithm_id is None:
            current_algorithm_id = get_algorithm_id(algorithm)
            
        if current_game_id is None:
            current_game_id = get_new_game_id()
            
        current_move_number += 1
        
        cursor.execute(
            """INSERT INTO ai_timings 
               (player_id, algorithm_id, move_time, move_number, game_id) 
               VALUES (?, ?, ?, ?, ?)""",
            (current_player_id, current_algorithm_id, time_taken, current_move_number, current_game_id)
        )
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving move time: {e}")
    finally:
        if conn:
            conn.close()

#===================================================================================================================================
def generate_performance_chart(num_games=10):
    """Generate a chart comparing algorithm performance over games"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get average move times for each algorithm across games
        cursor.execute("""
            SELECT a.algorithm_name, AVG(t.move_time) as avg_time, t.game_id
            FROM ai_timings t
            JOIN ai_algorithms a ON t.algorithm_id = a.algorithm_id
            GROUP BY t.game_id, a.algorithm_id
            ORDER BY t.game_id
            LIMIT ?
        """, (num_games * 2,))  # 2 algorithms
        
        results = cursor.fetchall()
        
        if not results:
            print("No performance data available")
            return None
        
        # Organize data for plotting
        algorithms = {}
        for algo_name, avg_time, game_id in results:
            if algo_name not in algorithms:
                algorithms[algo_name] = []
            algorithms[algo_name].append((game_id, avg_time))
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        for algo_name, data in algorithms.items():
            game_ids = [d[0] for d in data]
            avg_times = [d[1] for d in data]
            plt.plot(game_ids, avg_times, marker='o', label=algo_name)
        
        plt.title('Algorithm Performance Comparison')
        plt.xlabel('Game ID')
        plt.ylabel('Average Move Time (seconds)')
        plt.legend()
        plt.grid(True)
        
        # Save the chart
        output_file = f"algorithm_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_file)
        print(f"Performance chart saved to {output_file}")
        plt.close()
        
        return output_file
    except sqlite3.Error as e:
        print(f"Error generating performance chart: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in chart generation: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Initialize the database when the module is imported
try:
    initialize_database()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

