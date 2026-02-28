import sys
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from .styles import MAIN_WINDOW_STYLE, BUTTON_STYLE
from .home_screen import HomeScreen
from .dashboard_screen import DashboardScreen
from .patient_screen import PatientScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dental Clinic Management System")
        self.resize(1024, 768)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Remove any default margins or backgrounds that might cause black bars
        # self.central_widget.setContentsMargins(0, 0, 0, 0)
        
        self.init_screens()
    
    def init_screens(self):
        # 0: Home
        self.home_screen = HomeScreen()
        self.home_screen.enter_clicked.connect(self.show_dashboard)
        self.central_widget.addWidget(self.home_screen)
        
        # 1: Dashboard
        self.dashboard_screen = DashboardScreen()
        self.dashboard_screen.add_patient_clicked.connect(self.show_new_patient)
        self.dashboard_screen.patient_selected.connect(self.show_existing_patient)
        self.central_widget.addWidget(self.dashboard_screen)
        
        # 2: Patient Screen Container (Dynamic)
        self.patient_container = QWidget()
        self.patient_layout = QVBoxLayout(self.patient_container)
        self.patient_layout.setContentsMargins(0,0,0,0)
        
        # Back Button for Patient Screen
        back_btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.setFixedWidth(200)
        back_btn.clicked.connect(self.show_dashboard)
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.addStretch()
        
        self.patient_layout.addLayout(back_btn_layout)
        
        # Placeholder for actual patient screen
        self.current_patient_screen = None
        
        self.central_widget.addWidget(self.patient_container)

    def show_dashboard(self):
        # Navigation should be instant
        self.central_widget.setCurrentIndex(1)
        # Ensure dashboard background is clean
        self.dashboard_screen.setStyleSheet("background-color: #f5f7fa;")
        # Refresh data in the background or after transition
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self.dashboard_screen.refresh_data)

    def show_new_patient(self):
        self.load_patient_screen(None)
    
    def show_existing_patient(self, patient_id):
        self.load_patient_screen(patient_id)

    def load_patient_screen(self, patient_id):
        # Remove old screen if exists
        if self.current_patient_screen:
            self.patient_layout.removeWidget(self.current_patient_screen)
            self.current_patient_screen.deleteLater()
        
        self.current_patient_screen = PatientScreen(patient_id)
        self.patient_layout.addWidget(self.current_patient_screen)
        self.central_widget.setCurrentIndex(2)
