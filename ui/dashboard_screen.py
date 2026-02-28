import sqlite3, sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QTabWidget, QLineEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import get_db_path, db_manager
from .styles import LABEL_TITLE_STYLE, LABEL_SUBTITLE_STYLE, BUTTON_STYLE, CARD_STYLE, TABLE_STYLE, INPUT_STYLE

class DashboardScreen(QWidget):
    patient_selected = pyqtSignal(int)
    add_patient_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f7fa;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title = QLabel("Saint Jude Dental Clinic")
        title.setStyleSheet(LABEL_TITLE_STYLE + "border: none; background: transparent;")
        
        add_btn = QPushButton("+ New Patient")
        add_btn.setStyleSheet(BUTTON_STYLE)
        add_btn.setFixedWidth(180)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_patient_clicked.emit)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(BUTTON_STYLE + "background-color: #bdc3c7;")
        refresh_btn.setFixedWidth(120)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e0e0e0; border-radius: 12px; background: white; }
            QTabBar::tab { background: #f5f7fa; padding: 12px 24px; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 4px; color: #7f8c8d; font-weight: bold; font-size: 12pt; }
            QTabBar::tab:selected { background: white; border: 1px solid #e0e0e0; border-bottom-color: white; color: #4a90e2; }
        """)
        
        self.tabs.addTab(self.create_home_tab(), "Home")
        self.tabs.addTab(self.create_patient_list_tab(), "Patient List")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        
        self.refresh_data()

    def create_home_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        left_card = QFrame()
        left_card.setStyleSheet(CARD_STYLE)
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        title_appt = QLabel("Today's Appointments")
        title_appt.setStyleSheet(LABEL_SUBTITLE_STYLE + "border: none; background: transparent;")
        left_layout.addWidget(title_appt)
        
        self.today_patients_table = QTableWidget()
        self.today_patients_table.setColumnCount(2)
        self.today_patients_table.setHorizontalHeaderLabels(["Name", "Time"])
        self.today_patients_table.setStyleSheet(TABLE_STYLE)
        self.today_patients_table.setShowGrid(False)
        self.today_patients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.today_patients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.today_patients_table.cellDoubleClicked.connect(self.on_today_patient_clicked)
        h = self.today_patients_table.horizontalHeader()
        if h: h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v = self.today_patients_table.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(45)
        left_layout.addWidget(self.today_patients_table)
        
        right_card = QFrame()
        right_card.setStyleSheet(CARD_STYLE)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        title_act = QLabel("Recent Activity Log (Today)")
        title_act.setStyleSheet(LABEL_SUBTITLE_STYLE + "border: none; background: transparent;")
        right_layout.addWidget(title_act)
        
        self.today_activity_table = QTableWidget()
        self.today_activity_table.setColumnCount(2)
        self.today_activity_table.setHorizontalHeaderLabels(["Time", "Action"])
        self.today_activity_table.setStyleSheet(TABLE_STYLE)
        self.today_activity_table.setShowGrid(False)
        self.today_activity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        h = self.today_activity_table.horizontalHeader()
        if h: h.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v = self.today_activity_table.verticalHeader()
        if v:
            v.setVisible(False)
            v.setDefaultSectionSize(40)
        right_layout.addWidget(self.today_activity_table)
        
        layout.addWidget(left_card, 60)
        layout.addWidget(right_card, 40)
        return tab

    def create_patient_list_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Unified Search Bar
        search_card = QFrame()
        search_card.setObjectName("search_container")
        search_card.setStyleSheet("""
            #search_container {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
            }
            QLineEdit {
                border: none;
                background: transparent;
                padding: 10px;
                color: black;
            }
        """)
        
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_layout.setSpacing(10)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #7f8c8d; font-weight: bold; background: transparent; border: none;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patients...")
        self.search_input.textChanged.connect(self.filter_patients)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14pt; background: transparent; border: none;")
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_icon)
        
        layout.addWidget(search_card)
        
        table_card = QFrame()
        table_card.setStyleSheet(CARD_STYLE)
        table_layout = QVBoxLayout(table_card)
        
        self.all_patients_table = QTableWidget()
        self.all_patients_table.setColumnCount(3)
        self.all_patients_table.setHorizontalHeaderLabels(["Name", "Phone", "Birthdate"])
        self.all_patients_table.setStyleSheet(TABLE_STYLE)
        self.all_patients_table.setShowGrid(False)
        self.all_patients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.all_patients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.all_patients_table.cellDoubleClicked.connect(self.on_all_patient_clicked)
        v = self.all_patients_table.verticalHeader()
        if v: v.setVisible(False)
        
        # Add a hidden column for the DB ID (not visible but accessible)
        self.all_patients_table.setColumnCount(4)
        self.all_patients_table.setColumnHidden(3, True) 
        
        header = self.all_patients_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(self.all_patients_table)
        
        layout.addWidget(table_card)
        return tab

    def refresh_data(self):
        import time
        t_refresh_start = time.perf_counter()
        try:
            conn = db_manager.conn
            with conn:
                cursor = conn.cursor()

                # Appointments
                cursor.execute("""
                    SELECT DISTINCT p.id, p.name, v.visit_time 
                    FROM visits v
                    JOIN patients p ON v.patient_id = p.id
                    WHERE date(v.visit_date) = date('now')
                    ORDER BY v.visit_time DESC
                """)
                today_patients = cursor.fetchall()
                self.today_patients_table.setRowCount(0)
                for i, row in enumerate(today_patients):
                    self.today_patients_table.insertRow(i)
                    # We only show Name and Time.
                    name_item = QTableWidgetItem(str(row[1]))
                    name_item.setData(Qt.ItemDataRole.UserRole, row[0]) # Store DB ID
                    time_val = QTableWidgetItem(str(row[2]))
                    
                    self.today_patients_table.setItem(i, 0, name_item)
                    self.today_patients_table.setItem(i, 1, time_val)

                # Activity Log
                cursor.execute("""
                    SELECT strftime('%H:%M', timestamp), action || (CASE WHEN patient_id IS NOT NULL THEN ' (ID: ' || patient_id || ')' ELSE '' END)
                    FROM activity_logs
                    WHERE date(timestamp) = date('now')
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)
                logs = cursor.fetchall()
                self.today_activity_table.setRowCount(0)
                for i, row in enumerate(logs):
                    self.today_activity_table.insertRow(i)
                    for j, val in enumerate(row):
                        item = QTableWidgetItem(str(val) if val is not None else "")
                        self.today_activity_table.setItem(i, j, item)

                # Patients list
                cursor.execute("SELECT id, name, phone, birthdate FROM patients ORDER BY name ASC")
                patients = cursor.fetchall()
                self.all_patients_table.setRowCount(0)
                for i, row in enumerate(patients):
                    self.all_patients_table.insertRow(i)
                    # Column 0: Name
                    self.all_patients_table.setItem(i, 0, QTableWidgetItem(str(row[1])))
                    # Column 1: Phone
                    self.all_patients_table.setItem(i, 1, QTableWidgetItem(str(row[2])))
                    # Column 2: Birthdate
                    self.all_patients_table.setItem(i, 2, QTableWidgetItem(str(row[3])))
                    # Column 3: DB ID (Hidden)
                    self.all_patients_table.setItem(i, 3, QTableWidgetItem(str(row[0])))

        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
        
        t_refresh_end = time.perf_counter()
        print(f"DEBUG_PERF: Total Dashboard refresh_data took {t_refresh_end - t_refresh_start:.4f}s")

    def filter_patients(self, text):
        search_col = 0 # Name (was 1, now 0 because # column removed)
            
        for i in range(self.all_patients_table.rowCount()):
            item = self.all_patients_table.item(i, search_col)
            if item:
                self.all_patients_table.setRowHidden(i, text.lower() not in item.text().lower())

    def on_today_patient_clicked(self, row, col):
        item = self.today_patients_table.item(row, 0)
        if item: 
            db_id = item.data(Qt.ItemDataRole.UserRole)
            if db_id: self.patient_selected.emit(int(db_id))

    def on_all_patient_clicked(self, row, col):
        item = self.all_patients_table.item(row, 3) # DB ID is now at index 3
        if item: self.patient_selected.emit(int(item.text()))
