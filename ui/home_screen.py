from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from .styles import BUTTON_STYLE, LABEL_TITLE_STYLE

class HomeScreen(QWidget):
    enter_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container for centering
        container = QFrame()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Dental Clinic Management")
        title.setStyleSheet(LABEL_TITLE_STYLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        enter_btn = QPushButton("Enter System")
        enter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        enter_btn.setStyleSheet(BUTTON_STYLE)
        enter_btn.setMinimumWidth(200)
        enter_btn.clicked.connect(self.enter_clicked.emit)

        container_layout.addWidget(title)
        container_layout.addWidget(enter_btn)
        
        layout.addWidget(container)
        self.setLayout(layout)
