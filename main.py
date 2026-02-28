import sys
import os

# Add the project root to sys.path
# Fix: Ensure absolute path to root is used
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from PyQt6.QtWidgets import QApplication
from dental_app.ui.main_window import MainWindow
from dental_app.database import init_db

def main():
    # Initialize Database and Persistent Connection
    from dental_app.database import db_manager
    _ = db_manager.conn
    init_db()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Consistent look across platforms
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
