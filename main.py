import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QSplitter, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from game import start_game
from gui import TicTacToeUI
from performance_analyzer import PerformanceAnalyzer


class MainMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color:#1d5772;")

        # Create the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        #=======================================================================================
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setFixedSize(self.size())
        self.setStyleSheet("background-color:#004e72")
        #================================================================================

        # Create pages
        self.create_main_menu_page()
        self.create_game_page()
        self.create_stats_page()
        #self.create_about_page()

        # Show the main menu initially
        self.stacked_widget.setCurrentIndex(0)

        # Set up the performance analyzer
        self.analyzer = PerformanceAnalyzer()

    def create_main_menu_page(self):
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)

        # Title
        title_label = QLabel("5x5 Tic-Tac-Toe Game")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        menu_layout.addWidget(title_label)
        title_label.setStyleSheet("color: white;")

        # Description
        desc_label = QLabel("Human vs Computer")
        desc_label.setStyleSheet("color: white;font-weight: bold")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 12))
        menu_layout.addWidget(desc_label)

        # Add some spacing
        menu_layout.addSpacing(40)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)

        btn_style = """
            QPushButton {
                background-color: black;
                color: #b2bcc1;
                border: none;
                padding: 15px 32px;
                text-align: center;
                font-size: 20px;
                font-weight:bold;
                margin: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0090ca;
                color: black;
            }
        """

        # Start Game button
        start_btn = QPushButton("Start Game")
        start_btn.setStyleSheet(btn_style)
        start_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        buttons_layout.addWidget(start_btn)

        # Statistics button
        stats_btn = QPushButton("View Algorithm Statistics")
        stats_btn.setStyleSheet(btn_style)
        stats_btn.clicked.connect(self.show_statistics)
        buttons_layout.addWidget(stats_btn)

        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet(btn_style.replace("background-color: #4CAF50", "background-color: #f44336"))
        exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(exit_btn)

        menu_layout.addWidget(buttons_widget)
        menu_layout.addStretch()

        self.stacked_widget.addWidget(menu_widget)

    def create_game_page(self):
        self.game_widget = TicTacToeUI()
        back_btn = QPushButton("Back to Main Menu")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.game_widget.layout().addWidget(back_btn)
        self.stacked_widget.addWidget(self.game_widget)

    def create_stats_page(self):
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        title_label = QLabel("Game History And Charts")
        title_label.setStyleSheet("color: white;font-weight:bold")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        stats_layout.addWidget(title_label)

        tab_widget = QTabWidget()
        stats_layout.addWidget(tab_widget)

        # Algorithm Comparison Tab
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)

        compare_btn = QPushButton("Run New 10-Game Comparison")
        compare_btn.setStyleSheet("color:white;font-weight:bold;background-color:b7bfc5")
        compare_btn.clicked.connect(self.run_new_comparison)
        comparison_layout.addWidget(compare_btn)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        comparison_layout.addWidget(self.stats_text)

        tab_widget.addTab(comparison_tab, "Algorithm Comparison")
#=====================================================Game History==========================================================
        # Game History Tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Game ID", "Player", "Result", "Date", "Moves"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
       

        self.history_table.setStyleSheet("""
        QTableWidget::item {
         background-color: #d8d8d1;
                            }
        QHeaderView::section {
        background-color: black;
        color: white;
}
""")

        history_layout.addWidget(self.history_table)

        refresh_btn = QPushButton("Refresh History")
        refresh_btn.setStyleSheet("color: black;font-weight:bold;")
        refresh_btn.clicked.connect(self.load_game_history)
        history_layout.addWidget(refresh_btn)

        tab_widget.addTab(history_tab, "Game History")
        tab_widget.setStyleSheet("background-color: #79aaca;font-weight: bold")

        back_btn = QPushButton("Back to Main Menu")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        back_btn.setStyleSheet("color: white;font-weight:bold")
        stats_layout.addWidget(back_btn)

        self.stacked_widget.addWidget(stats_widget)
   
    def show_statistics(self):
        self.stacked_widget.setCurrentIndex(2)
        self.load_game_history()

    def load_game_history(self):
        """Load game history from database into the table"""
        try:
            from database import get_game_history
            games_data = get_game_history()
            self.history_table.setRowCount(len(games_data))
            for row, (game_id, player_name, result, game_date, moves_count) in enumerate(games_data):
                self.history_table.setItem(row, 0, QTableWidgetItem(str(game_id)))
                self.history_table.setItem(row, 1, QTableWidgetItem(player_name))
                self.history_table.setItem(row, 2, QTableWidgetItem(result))
                self.history_table.setItem(row, 3, QTableWidgetItem(str(game_date)))
                self.history_table.setItem(row, 4, QTableWidgetItem(str(moves_count)))
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Could not load game history: {e}")
#==============================================================================================================
    def run_new_comparison(self):
        """Run a new algorithm comparison"""
        start_msg = QMessageBox(self)
        start_msg.setIcon(QMessageBox.Information)
        start_msg.setWindowTitle("Comparison Started")
        start_msg.setText("Running 10 game rounds to compare algorithms.\nThis may take a few moments...")
        start_msg.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 14px;
        }
        QMessageBox {
            background-color: #1d5772;;
        }
        QPushButton {
            background-color: white;
            color: black;
            font-weight: bold;
        }
    """)
        start_msg.exec_()
     
        sender = self.sender()
        sender.setEnabled(False)

        try:
            results = self.analyzer.run_algorithm_comparison(10)
            report = self.analyzer.generate_statistics_report(results)
            self.stats_text.setText(report)

            chart_path = "algorithm_comparison.png"
            self.analyzer.generate_time_comparison_chart(results, chart_path)

            # Create a new window to show the chart
            chart_window = QWidget()
            chart_window.setWindowTitle("Algorithm Comparison Chart")
            chart_window.resize(800, 600)

            layout = QVBoxLayout()
            label = QLabel()
            pixmap = QPixmap(chart_path)
            label.setPixmap(pixmap)
            label.setScaledContents(True)  # Scale the image to fit the window

            layout.addWidget(label)
            chart_window.setLayout(layout)

            # Show the new window
            chart_window.show()

            # Keep a reference to prevent the window from closing
            self.chart_window = chart_window
#===============================================================================================
            start_msg = QMessageBox(self)
            start_msg.setIcon(QMessageBox.Information)
            start_msg.setWindowTitle("Comparison Complete")
            start_msg.setText("Comparison complete! Chart displayed in a new window.")
            start_msg.setStyleSheet("""
                QLabel {
                color: white;
                 font-size: 14px;
        }
        QMessageBox {
            background-color: #1d5772;;
        }
        QPushButton {
            background-color: white;
            color: black;
            font-weight: bold;
        }
    """)
            start_msg.exec_()
#=====================================================================================================
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred during comparison: {e}")
        finally:
            sender.setEnabled(True)
#==============================================================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenuWindow()
    window.show()
    sys.exit(app.exec_())
