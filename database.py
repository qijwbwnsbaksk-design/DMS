import sqlite3
import os
import sys
import json
import time
from datetime import datetime

DB_NAME = "dental_clinic.db"

class DatabaseManager:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    @property
    def conn(self):
        if self._conn is None:
            db_path = get_db_path()
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            # Enable Foreign Keys immediately
            self._conn.execute("PRAGMA foreign_keys = ON;")
            # 2. Configure SQLite Once at Startup
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")
            self._conn.execute("PRAGMA temp_store=MEMORY;")
            self._conn.execute("PRAGMA cache_size=-10000;")
            
            # Verify journal_mode returns WAL
            cursor = self._conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            print(f"SQLite journal_mode: {mode}")
            if mode.lower() != 'wal':
                print("WARNING: journal_mode is not WAL")
        return self._conn

db_manager = DatabaseManager()

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    return os.path.join(get_app_dir(), DB_NAME)

def get_image_dir():
    img_dir = os.path.join(get_app_dir(), "tooth_images")
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def init_db():
    conn = db_manager.conn
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # 1. Base table creation
    cursor.execute("CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clinic_settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS teeth_metadata (tooth_type TEXT, unit_id TEXT, PRIMARY KEY (tooth_type, unit_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS activity_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, patient_id INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE SET NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS description_options (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)")

    # 2. Robust migration logic
    def migrate_table(table_name, required_columns):
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                print(f"Migrating {table_name}: adding {col_name}")
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"Migration error on {table_name}.{col_name}: {e}")

    # Patients
    migrate_table('patients', [
        ('address', 'TEXT'),
        ('phone', 'TEXT'),
        ('birthdate', 'TEXT'),
        ('occupation_status', 'TEXT'),
        ('complaint', 'TEXT'),
        ('medical_history', 'TEXT'),
        ('created_at', "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ])
    
    # Visits
    migrate_table('visits', [
        ('visit_date', 'DATE'),
        ('visit_time', 'TIME'),
        ('description', 'TEXT'),
        ('ortho_data', 'TEXT'),
        ('ortho_brand', 'TEXT'),
        ('teeth_data', 'TEXT'),
        ('general_notes', 'TEXT'),
        ('created_at', "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ])
    
    # Payments
    migrate_table('payments', [
        ('visit_id', 'INTEGER'),
        ('payment_date', 'DATE'),
        ('amount', 'REAL'),
        ('discount', 'REAL DEFAULT 0.0'),
        ('amount_paid', 'REAL'),
        ('balance', 'REAL'),
        ('payment_type', "TEXT DEFAULT 'New Payment'"),
        ('received_by', 'TEXT'),
        ('parent_id', 'INTEGER'),
        ('created_at', "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ])

    # Teeth Metadata
    migrate_table('teeth_metadata', [
        ('display_label', 'TEXT'),
        ('x_pos', 'REAL'),
        ('y_pos', 'REAL'),
        ('image_path', 'TEXT')
    ])

    # Seed initial teeth positions if empty
    cursor.execute("SELECT COUNT(*) FROM teeth_metadata")
    if cursor.fetchone()[0] == 0:
        seed_teeth_metadata(cursor)

    # Seed default clinic settings
    cursor.execute("SELECT COUNT(*) FROM clinic_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO clinic_settings (key, value) VALUES (?, ?)", ('receipt_header', 'Dental Clinic Name\nAddress Line 1\nPhone: 123-456-789'))
        cursor.execute("INSERT INTO clinic_settings (key, value) VALUES (?, ?)", ('receipt_footer', 'Thank you for your trust!\nPlease come again.'))

    conn.commit()
    get_image_dir()
    cleanup_logs()

def seed_teeth_metadata(cursor):
    def get_arc_coords(n, y_base, arc_height, width=600, center_x=350):
        coords = []
        for i in range(n):
            normalized_x = (i - (n-1)/2) / ((n-1)/2)
            x = center_x + (width/2) * normalized_x
            y = y_base - arc_height * (1 - normalized_x**2)
            coords.append((x, y))
        return coords

    # Adult
    upper_adult = get_arc_coords(16, 150, 80)
    for i, (x, y) in enumerate(upper_adult):
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('adult', str(i+1), str(i+1), x, y))
    lower_adult = get_arc_coords(16, 350, -80)
    for i, (x, y) in enumerate(lower_adult):
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('adult', str(32-i), str(32-i), x, y))

    # Child
    upper_child = get_arc_coords(10, 150, 60)
    labels_upper = "ABCDEFGHIJ"
    for i, (x, y) in enumerate(upper_child):
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('child', labels_upper[i], labels_upper[i], x, y))
    lower_child = get_arc_coords(10, 350, -60)
    labels_lower = "TSRQPONMLK"
    for i, (x, y) in enumerate(lower_child):
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('child', labels_lower[i], labels_lower[i], x, y))

    # Ortho
    for i, (x, y) in enumerate(upper_adult):
        uid = f"U{i+1}"
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('ortho', uid, uid, x, y))
    for i, (x, y) in enumerate(lower_adult):
        uid = f"L{16-i}"
        cursor.execute("INSERT OR IGNORE INTO teeth_metadata (tooth_type, unit_id, display_label, x_pos, y_pos) VALUES (?,?,?,?,?)",
                       ('ortho', uid, uid, x, y))

def cleanup_logs():
    try:
        conn = db_manager.conn
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activity_logs WHERE timestamp < datetime('now', '-7 days')")
        conn.commit()
    except: pass

def log_activity(action, patient_id=None):
    try:
        conn = db_manager.conn
        cursor = conn.cursor()
        
        start_exec = time.time()
        cursor.execute("INSERT INTO activity_logs (action, patient_id) VALUES (?, ?)", (action, patient_id))
        end_exec = time.time()
        
        start_commit = time.time()
        conn.commit()
        end_commit = time.time()
        
        print(f"DB Activity Log: Execute={end_exec-start_exec:.4f}s, Commit={end_commit-start_commit:.4f}s")
    except Exception as e:
        print(f"Log activity error: {e}")

def save_visit(patient_id, v_date, v_time, description, ortho_data, ortho_brand, teeth_data, general_notes):
    try:
        conn = db_manager.conn
        cursor = conn.cursor()
        
        start_exec = time.time()
        cursor.execute("INSERT INTO visits (patient_id, visit_date, visit_time, description, ortho_data, ortho_brand, teeth_data, general_notes) VALUES (?,?,?,?,?,?,?,?)",
                       (patient_id, v_date, v_time, description, json.dumps(ortho_data), ortho_brand, json.dumps(teeth_data), general_notes))
        end_exec = time.time()
        
        start_commit = time.time()
        conn.commit()
        end_commit = time.time()
        
        print(f"DB Save Visit: Execute={end_exec-start_exec:.4f}s, Commit={end_commit-start_commit:.4f}s")
        return cursor.lastrowid
    except Exception as e:
        print(f"Save visit error: {e}")
        return None

if __name__ == "__main__":
    init_db()
