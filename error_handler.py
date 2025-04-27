# error_handler.py

import logging
import sys
import traceback
from PyQt5.QtWidgets import QMessageBox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tictactoe_errors.log"),
        logging.StreamHandler()
    ]
)

class ErrorHandler:
    """
    Central error handling class for the Tic-Tac-Toe application.
    Provides methods for logging, displaying, and handling various types of errors.
    """
    
    @staticmethod
    def log_error(error, module_name=None):
        """Log an error with optional module information"""
        if module_name:
            logging.error(f"Error in {module_name}: {error}")
        else:
            logging.error(f"Error: {error}")
        
        # Log traceback for debugging
        logging.debug(traceback.format_exc())
    
    @staticmethod
    def show_error_dialog(parent, title, message, details=None):
        """Display an error dialog to the user"""
        error_box = QMessageBox(parent)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        
        if details:
            error_box.setDetailedText(details)
            
        error_box.exec_()
    
    @staticmethod
    def handle_exception(parent, error, module_name=None):
        """Handle an exception by logging it and showing a dialog"""
        ErrorHandler.log_error(error, module_name)
        
        message = str(error)
        details = traceback.format_exc()
        
        # Show a user-friendly message
        title = "Error"
        if module_name:
            title = f"Error in {module_name}"
            
        ErrorHandler.show_error_dialog(parent, title, message, details)
    
    @staticmethod
    def validate_move(row, col, board_size=5):
        """
        Validate a move input.
        Raises ValueError with descriptive message if invalid.
        """
        # Check if move is numeric
        if not (isinstance(row, int) and isinstance(col, int)):
            raise ValueError("Row and column must be numbers")
        
        # Check if move is within board bounds
        if not (0 <= row < board_size and 0 <= col < board_size):
            raise ValueError(f"Move must be within the {board_size}x{board_size} board (0-{board_size-1})")
        
        return True
    
    @staticmethod
    def validate_player_name(name):
        """
        Validate a player name.
        Raises ValueError with descriptive message if invalid.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Player name cannot be empty")
            
        if len(name) > 50:
            raise ValueError("Player name is too long (maximum 50 characters)")
            
        return True
    
    @staticmethod
    def validate_algorithm_choice(choice):
        """
        Validate algorithm choice.
        Raises ValueError with descriptive message if invalid.
        """
        valid_choices = ['Minimax', 'Alpha-Beta', '1', '2']
        if choice not in valid_choices:
            raise ValueError("Algorithm choice must be 'Minimax', 'Alpha-Beta', '1', or '2'")
            
        return True
    
    @staticmethod
    def safe_db_operation(func):
        """
        Decorator for safely executing database operations.
        Handles SQLite exceptions and connection issues.
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(e, "Database")
                raise Exception(f"Database operation failed: {str(e)}")
        return wrapper

# Enhanced exception handling for GUI applications

def install_global_exception_handler():
    """
    Install a global exception handler to catch unhandled exceptions.
    This ensures that the application doesn't crash silently.
    """
    def global_exception_handler(exctype, value, traceback_obj):
        """Global function to catch unhandled exceptions"""
        logging.critical("Unhandled exception", exc_info=(exctype, value, traceback_obj))
        
        # Log to file
        with open("crash_report.log", "a") as f:
            f.write(f"\n--- Unhandled Exception ---\n")
            f.write(f"Time: {logging.Formatter('%(asctime)s').format(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
            f.write(f"Type: {exctype.__name__}\n")
            f.write(f"Value: {value}\n")
            import traceback
            traceback.print_tb(traceback_obj, file=f)
            f.write("\n")
        
        # Show error dialog
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("An unexpected error occurred")
            msg.setInformativeText(str(value))
            msg.setWindowTitle("Application Error")
            msg.setDetailedText("".join(traceback.format_tb(traceback_obj)))
            msg.exec_()
    
    # Install exception handler
    sys.excepthook = global_exception_handler