import sqlite3, os, json, sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QFormLayout, QTabWidget, QDateEdit, 
    QTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QInputDialog, QDialog, QComboBox, QFrame, QListWidget, QAbstractItemView, QApplication, QScrollArea,
    QSlider, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QDate, QTime
from ..database import get_db_path, get_app_dir, log_activity, db_manager
from .dental_chart import DentalChart
from .styles import BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE, MAIN_WINDOW_STYLE, CARD_STYLE, LABEL_SUBTITLE_STYLE

class DescriptionManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Description Options")
        self.resize(350, 450)
        self.init_ui()
        self.load_options()

    def init_ui(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        l = QVBoxLayout()
        l.setContentsMargins(15, 15, 15, 15)
        l.setSpacing(15)
        
        container = QFrame()
        container.setStyleSheet(CARD_STYLE)
        cl = QVBoxLayout(container)
        
        self.list = QListWidget()
        self.list.setStyleSheet(TABLE_STYLE)
        cl.addWidget(QLabel("<b>Description Options:</b>"))
        cl.addWidget(self.list)
        
        bl = QHBoxLayout()
        add = QPushButton("Add"); add.setStyleSheet(BUTTON_STYLE); add.clicked.connect(self.add_opt)
        edit = QPushButton("Rename"); edit.setStyleSheet(BUTTON_STYLE + "background-color: #bdc3c7;"); edit.clicked.connect(self.rename_opt)
        rem = QPushButton("Delete"); rem.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 12px; padding: 10px; font-weight: bold; border: none;"); rem.clicked.connect(self.rem_opt)
        bl.addWidget(add); bl.addWidget(edit); bl.addWidget(rem)
        cl.addLayout(bl)
        
        close = QPushButton("Close"); close.setStyleSheet(BUTTON_STYLE + "background-color: #7f8c8d;"); close.clicked.connect(self.accept)
        cl.addWidget(close)
        
        l.addWidget(container)
        self.setLayout(l)

    def load_options(self):
        try:
            self.list.clear()
            conn = db_manager.conn; cur = conn.cursor()
            cur.execute("SELECT name FROM description_options ORDER BY name")
            for r in cur.fetchall(): self.list.addItem(r[0])
        except Exception as e:
            print(f"Error loading options: {e}")

    def add_opt(self):
        name, ok = QInputDialog.getText(self, "Add", "Option Name:")
        if ok and name.strip():
            try: 
                conn = db_manager.conn; cur = conn.cursor()
                cur.execute("INSERT INTO description_options (name) VALUES (?)", (name.strip(),))
                conn.commit()
                log_activity(f"Added procedure option: {name.strip()}")
                self.load_options()
            except Exception as e:
                print(f"Error adding option: {e}")
                QMessageBox.warning(self, "Error", "Duplicate option or database error.")

    def rename_opt(self):
        item = self.list.currentItem()
        if not item: return
        new, ok = QInputDialog.getText(self, "Rename", f"Rename '{item.text()}':", text=item.text())
        if ok and new.strip():
            try:
                conn = db_manager.conn; cur = conn.cursor()
                cur.execute("UPDATE description_options SET name=? WHERE name=?", (new.strip(), item.text()))
                conn.commit()
                log_activity(f"Renamed procedure option: {item.text()} to {new.strip()}")
                self.load_options()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename option: {e}")

    def rem_opt(self):
        item = self.list.currentItem()
        if not item: return
        ret = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{item.text()}'?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            try:
                conn = db_manager.conn; cur = conn.cursor()
                cur.execute("DELETE FROM description_options WHERE name=?", (item.text(),))
                conn.commit()
                log_activity(f"Deleted procedure option: {item.text()}")
                self.load_options()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete option: {e}")

class PatientProfileDialog(QDialog):
    def __init__(self, patient_screen, parent=None):
        super().__init__(parent)
        self.ps = patient_screen
        self.setWindowTitle("Patient Profile")
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        l = QVBoxLayout()
        f = QFormLayout()
        self.name_in = QLineEdit(self.ps.name_input.text())
        self.addr_in = QLineEdit(self.ps.address_input.text())
        self.phone_in = QLineEdit(self.ps.phone_input.text())
        
        # Birthdate and Age Row
        birth_age_layout = QHBoxLayout()
        self.birth_in = QDateEdit(self.ps.birthdate_input.date())
        self.birth_in.setCalendarPopup(True)
        self.birth_in.setDisplayFormat("yyyy/MM/dd")
        cw = self.birth_in.calendarWidget()
        if cw: cw.setGridVisible(False)
        self.birth_in.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; background-color: white; color: black;")
        self.birth_in.dateChanged.connect(self.update_age_from_birthdate)
        
        self.age_in = QLineEdit()
        self.age_in.setPlaceholderText("Age")
        self.age_in.setFixedWidth(60)
        self.age_in.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; background-color: white; color: black;")
        self.update_age_from_birthdate(self.birth_in.date())
        
        birth_age_layout.addWidget(self.birth_in)
        birth_age_layout.addWidget(QLabel("Age:"))
        birth_age_layout.addWidget(self.age_in)
        
        self.occ_in = QLineEdit(self.ps.occupation_input.text())
        self.comp_in = QTextEdit(self.ps.complaint_input.toPlainText())
        self.med_in = QTextEdit(self.ps.med_history_input.toPlainText())
        for i in [self.name_in, self.addr_in, self.phone_in, self.occ_in, self.comp_in, self.med_in]:
            i.setStyleSheet(INPUT_STYLE); i.setReadOnly(True); i.setStyleSheet(i.styleSheet() + "color: black;")
        self.birth_in.setReadOnly(True); self.age_in.setReadOnly(True)
        
        f.addRow("Name:", self.name_in); f.addRow("Address:", self.addr_in); f.addRow("Phone:", self.phone_in)
        f.addRow("Birthdate:", birth_age_layout); f.addRow("Occupation:", self.occ_in)
        f.addRow("Complaint:", self.comp_in); f.addRow("Med History:", self.med_in)
        l.addLayout(f)
        bl = QHBoxLayout()
        self.edit_btn = QPushButton("Edit (Requires Password)"); self.edit_btn.clicked.connect(self.toggle_edit)
        self.del_btn = QPushButton("Delete Patient"); self.del_btn.setStyleSheet("background-color: #dc3545; color: white;"); self.del_btn.clicked.connect(self.delete_patient)
        self.save_btn = QPushButton("Save Changes"); self.save_btn.clicked.connect(self.save_changes); self.save_btn.hide()
        bl.addWidget(self.edit_btn); bl.addWidget(self.del_btn); bl.addWidget(self.save_btn)
        l.addLayout(bl)
        close = QPushButton("Close"); close.clicked.connect(self.accept)
        l.addWidget(close); self.setLayout(l)
        self.is_editing = False

    def update_age_from_birthdate(self, date):
        today = QDate.currentDate()
        age = today.year() - date.year()
        if today.month() < date.month() or (today.month() == date.month() and today.day() < date.day()):
            age -= 1
        self.age_in.setText(str(max(0, age)))

    def toggle_edit(self):
        if not self.is_editing:
            pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password:", QLineEdit.EchoMode.Password)
            if ok and self.ps.check_password(pwd): self.set_editing(True)
            elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")
        else: self.set_editing(False)

    def set_editing(self, e):
        self.is_editing = e
        for i in [self.name_in, self.addr_in, self.phone_in, self.occ_in, self.comp_in, self.med_in]: i.setReadOnly(not e)
        self.birth_in.setReadOnly(not e); self.age_in.setReadOnly(not e); self.save_btn.setVisible(e); self.del_btn.setVisible(not e)
        self.edit_btn.setText("Cancel" if e else "Edit (Requires Password)")

    def delete_patient(self):
        pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password:", QLineEdit.EchoMode.Password)
        if not ok or not self.ps.check_password(pwd):
            QMessageBox.warning(self, "Denied", "Wrong password or cancelled.")
            return

        ret = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this patient and all related records?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            try:
                conn = db_manager.conn
                cur = conn.cursor()
                cur.execute("DELETE FROM patients WHERE id=?", (self.ps.patient_id,))
                conn.commit()
                log_activity(f"Deleted patient", self.ps.patient_id)
                
                self.accept()
                main_win = self.window()
                if hasattr(main_win, 'show_dashboard'):
                    main_win.show_dashboard()
                else:
                    for widget in QApplication.topLevelWidgets():
                        if hasattr(widget, 'show_dashboard'):
                            widget.show_dashboard()
                            break
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete patient: {e}")

    def save_changes(self):
        try:
            conn = db_manager.conn; cur = conn.cursor()
            d = (self.name_in.text(), self.addr_in.text(), self.phone_in.text(), self.birth_in.date().toString("yyyy-MM-dd"), self.occ_in.text(), self.comp_in.toPlainText(), self.med_in.toPlainText(), self.ps.patient_id)
            cur.execute("UPDATE patients SET name=?, address=?, phone=?, birthdate=?, occupation_status=?, complaint=?, medical_history=? WHERE id=?", d)
            conn.commit()
            log_activity(f"Edited profile for patient", self.ps.patient_id)
            self.ps.load_patient_data(); self.accept()
        except Exception as e: QMessageBox.critical(self, "Error", f"Could not save: {e}")

class VisitDetailDialog(QDialog):
    def __init__(self, visit_id, patient_screen, parent=None):
        super().__init__(parent)
        self.visit_id = visit_id; self.ps = patient_screen; self.is_editing = False
        self.setWindowTitle("Visit Details"); self.resize(800, 600)
        self.init_ui(); self.load_data()

    def init_ui(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        l = QVBoxLayout()
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(15)

        # Header Card for Patient Type
        header_card = QFrame()
        header_card.setStyleSheet(CARD_STYLE + "background-color: white;")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        hl_top = QHBoxLayout()
        self.type_display = QLabel("Adult")
        self.type_display.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2c3e50; background: transparent;")
        hl_top.addWidget(QLabel("<b>Patient Type:</b>"))
        hl_top.addWidget(self.type_display)
        hl_top.addStretch()
        
        self.link_receipt_btn = QPushButton("Link to Receipt")
        self.link_receipt_btn.setStyleSheet(BUTTON_STYLE + "background-color: #f39c12; font-size: 10pt; padding: 5px 15px;")
        self.link_receipt_btn.clicked.connect(self.open_link_receipt_dialog)
        hl_top.addWidget(self.link_receipt_btn)
        
        header_layout.addLayout(hl_top)
        l.addWidget(header_card)

        # Content Card
        content_card = QFrame()
        content_card.setStyleSheet(CARD_STYLE + "background-color: white;")
        content_layout = QHBoxLayout(content_card)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)

        # Left Column: Details Form
        form_widget = QWidget()
        f = QFormLayout(form_widget)
        f.setSpacing(10)
        label_style = "color: #555555; font-size: 10pt; font-weight: bold; border: none; background: transparent;"
        
        self.date_input = QDateEdit()
        self.date_input.setReadOnly(True); self.date_input.setCalendarPopup(True); self.date_input.setDisplayFormat("yyyy/MM/dd")
        self.date_input.setStyleSheet(INPUT_STYLE)
        
        self.time_input = QTimeEdit(); self.time_input.setReadOnly(True); self.time_input.setStyleSheet(INPUT_STYLE)
        self.proc_display = QTextEdit(); self.proc_display.setReadOnly(True); self.proc_display.setFixedHeight(60); self.proc_display.setStyleSheet(INPUT_STYLE)
        self.notes_input = QTextEdit(); self.notes_input.setReadOnly(True); self.notes_input.setFixedHeight(80); self.notes_input.setStyleSheet(INPUT_STYLE)
        self.ortho_brand = QLineEdit(); self.ortho_brand.setReadOnly(True); self.ortho_brand.setStyleSheet(INPUT_STYLE)
        
        l_date = QLabel("Date:"); l_date.setStyleSheet(label_style)
        l_time = QLabel("Time:"); l_time.setStyleSheet(label_style)
        l_proc = QLabel("Procedures:"); l_proc.setStyleSheet(label_style)
        l_notes = QLabel("General Notes:"); l_notes.setStyleSheet(label_style)
        l_brand = QLabel("Brand:"); l_brand.setStyleSheet(label_style)
        self.brand_label = l_brand

        f.addRow(l_date, self.date_input)
        f.addRow(l_time, self.time_input)
        f.addRow(l_proc, self.proc_display)
        
        content_layout.addWidget(form_widget, 45)

        # Right Column: Teeth Details and General Notes with Scroll
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("border: none; background: transparent;")
        
        right_container = QWidget()
        right_column = QVBoxLayout(right_container)
        right_column.setSpacing(15)
        
        self.summary_lbl = QLabel()
        self.summary_lbl.setStyleSheet("color: black; border: none; background: #f8f9fa; border-radius: 12px; padding: 15px; font-size: 11pt; line-height: 1.5;")
        self.summary_lbl.setWordWrap(True)
        self.summary_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Swapping positions: General Notes first, then Teeth Details
        right_column.addWidget(l_notes)
        right_column.addWidget(self.notes_input)
        right_column.addWidget(l_brand)
        right_column.addWidget(self.ortho_brand)
        
        right_column.addWidget(QLabel("<b>Teeth Details:</b>"))
        right_column.addWidget(self.summary_lbl)
        
        # Wrapping chart in a container to ensure white background
        self.chart_container = QFrame()
        self.chart_container.setStyleSheet("background-color: white; border-radius: 18px;")
        chart_cl = QVBoxLayout(self.chart_container)
        chart_cl.setContentsMargins(0,0,0,0)
        
        self.chart = DentalChart()
        self.chart.setEnabled(False)
        self.chart.hide()
        chart_cl.addWidget(self.chart)
        
        right_column.addWidget(self.chart_container)
        right_column.addStretch()
        
        right_scroll.setWidget(right_container)
        content_layout.addWidget(right_scroll, 55)
        l.addWidget(content_card)

        # Footer: Buttons
        bl = QHBoxLayout()
        self.del_btn = QPushButton("Delete Visit")
        self.del_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 12px; padding: 10px; font-weight: bold;")
        self.del_btn.clicked.connect(self.delete_visit_internal)
        
        self.edit_btn = QPushButton("Edit (Requires Password)"); self.edit_btn.setStyleSheet(BUTTON_STYLE); self.edit_btn.clicked.connect(self.toggle_edit)
        self.save_btn = QPushButton("Save Changes"); self.save_btn.setStyleSheet(BUTTON_STYLE + "background-color: #27ae60;"); self.save_btn.clicked.connect(self.save_changes); self.save_btn.hide()
        bl.addWidget(self.del_btn)
        bl.addStretch()
        bl.addWidget(self.edit_btn); bl.addWidget(self.save_btn)
        l.addLayout(bl)

        self.setLayout(l)

    def open_link_receipt_dialog(self):
        try:
            conn = db_manager.conn
            cur = conn.cursor()
            # Find the root payment (parent_id IS NULL) that has a balance
            cur.execute("SELECT id, payment_date, balance FROM payments WHERE patient_id=? AND parent_id IS NULL AND balance > 0 ORDER BY payment_date DESC", (self.ps.patient_id,))
            rows = cur.fetchall()
            if not rows:
                # If no balance payments, check all unlinked new payments
                cur.execute("SELECT id, payment_date, amount_paid FROM payments WHERE patient_id=? AND visit_id IS NULL AND parent_id IS NULL ORDER BY payment_date DESC", (self.ps.patient_id,))
                rows = cur.fetchall()
            
            if not rows:
                QMessageBox.information(self, "Link Receipt", "No unlinked or outstanding payments found for this patient.")
                return
            
            items = [f"ID: {r[0]} | Date: {r[1]} | Val: PHP {r[2]:,.2f}" for r in rows]
            item, ok = QInputDialog.getItem(self, "Link Receipt", "Select payment to link:", items, 0, False)
            if ok and item:
                pid = int(item.split(" | ")[0].split(": ")[1])
                cur.execute("UPDATE payments SET visit_id=? WHERE id=?", (self.visit_id, pid))
                conn.commit()
                log_activity(f"Linked visit {self.visit_id} to payment {pid}", self.ps.patient_id)
                QMessageBox.information(self, "Success", "Visit linked to payment successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to link receipt: {e}")

    def delete_visit_internal(self):
        pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password to Delete Visit:", QLineEdit.EchoMode.Password)
        if ok and self.ps.check_password(pwd):
            ret = QMessageBox.question(self, "Confirm", "Delete this visit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ret == QMessageBox.StandardButton.Yes:
                try:
                    conn = db_manager.conn; cur = conn.cursor()
                    cur.execute("DELETE FROM visits WHERE id=?", (self.visit_id,))
                    conn.commit()
                    log_activity(f"Deleted visit {self.visit_id}", self.ps.patient_id)
                    if hasattr(self.ps, 'load_patient_data'):
                        self.ps.load_patient_data()
                    self.accept()
                except Exception as e: QMessageBox.critical(self, "Error", str(e))
        elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")

    def update_ortho_visibility(self):
        is_ortho = self.chart.tabs.tabText(self.chart.tabs.currentIndex()) == "Orthodontics"
        self.ortho_brand.setVisible(is_ortho)

    def load_data(self):
        try:
            conn = db_manager.conn
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT visit_date, visit_time, description, ortho_data, ortho_brand, teeth_data, general_notes FROM visits WHERE id=?", (self.visit_id,))
                r = cur.fetchone()
                if r:
                    self.date_input.setDate(QDate.fromString(r[0], "yyyy-MM-dd"))
                    self.time_input.setTime(QTime.fromString(r[1], "HH:mm"))
                    
                    self.proc_display.setText(r[2] or "None")
                    self.proc_display.setPlainText(r[2] if r[2] else "No procedure selected")
                    self.ortho_brand.setText(r[4] or "")
                    self.notes_input.setPlainText(r[6] or "")
                    t_data = json.loads(r[5]) if r[5] else {}
                    o_data = json.loads(r[3]) if r[3] else {}
                    
                    patient_type = "Adult"
                    if bool(o_data): patient_type = "Orthodontics Patient"
                    else:
                        for k in t_data.keys():
                            try:
                                if int(k) > 32: patient_type = "Child"; break
                            except: patient_type = "Child"; break
                    
                    self.type_display.setText(patient_type)
                    is_ortho_type = "Orthodontics" in patient_type
                    self.ortho_brand.setVisible(is_ortho_type)
                    self.brand_label.setVisible(is_ortho_type)
                    
                    teeth_summary = []
                    if t_data or o_data:
                        for t_id, details in t_data.items():
                            flag = details.get('flag', '') if isinstance(details, dict) else details
                            flag_indicator = " 🚩" if flag else ""
                            teeth_summary.append(f"Tooth {t_id}{flag_indicator}" + (f" - {flag}" if flag else ""))
                        for t_id, details in o_data.items():
                            flag = details.get('flag', '') if isinstance(details, dict) else details
                            flag_indicator = " 🚩" if flag else ""
                            teeth_summary.append(f"Tooth {t_id}{flag_indicator}" + (f" - {flag}" if flag else ""))
                        self.summary_lbl.setText("<br>".join([f"• {s}" for s in teeth_summary]))
                    else: self.summary_lbl.setText("<i>No teeth selected</i>")
                    self.summary_lbl.show(); self.chart.hide()
        except Exception as e: QMessageBox.critical(self, "Error", f"Could not load visit: {e}")

    def toggle_edit(self):
        if not self.is_editing:
            pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password:", QLineEdit.EchoMode.Password)
            if ok and self.ps.check_password(pwd): self.set_editing(True)
            elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")
        else: self.set_editing(False)

    def set_editing(self, e):
        self.is_editing = e; self.date_input.setReadOnly(not e); self.time_input.setReadOnly(not e)
        self.proc_display.setReadOnly(not e); self.notes_input.setReadOnly(not e); self.ortho_brand.setReadOnly(not e)
        edit_style = INPUT_STYLE + "background-color: white; color: black;"
        self.date_input.setStyleSheet(edit_style if e else INPUT_STYLE)
        self.time_input.setStyleSheet(edit_style if e else INPUT_STYLE)
        self.proc_display.setStyleSheet(edit_style if e else INPUT_STYLE)
        self.notes_input.setStyleSheet(edit_style if e else INPUT_STYLE)
        self.ortho_brand.setStyleSheet(edit_style if e else INPUT_STYLE)
        if e:
            self.chart_container.show(); self.chart.show(); self.chart.setEnabled(True)
            self.chart.tabs.tabBar().show(); self.chart.flag_btn.show(); self.chart.clear_btn.show(); self.chart.edit_btn.show(); self.summary_lbl.hide()
            try:
                conn = db_manager.conn; cur = conn.cursor(); cur.execute("SELECT teeth_data, ortho_data FROM visits WHERE id=?", (self.visit_id,))
                row = cur.fetchone()
                if row: self.chart.set_data(json.loads(row[0] or '{}'), json.loads(row[1] or '{}'))
            except: pass
            ptype = self.type_display.text()
            if "Orthodontics" in ptype: self.chart.tabs.setCurrentIndex(2)
            elif "Child" in ptype: self.chart.tabs.setCurrentIndex(1)
            else: self.chart.tabs.setCurrentIndex(0)
            self.update_ortho_visibility(); self.chart.setMinimumHeight(600)
        else:
            self.chart.setEnabled(False); self.chart.hide(); self.chart_container.hide()
            self.chart.tabs.tabBar().hide(); self.chart.flag_btn.hide(); self.chart.clear_btn.hide(); self.chart.edit_btn.hide(); self.summary_lbl.show()
        self.save_btn.setVisible(e); self.edit_btn.setText("Cancel" if e else "Edit (Requires Password)")

    def save_changes(self):
        try:
            t, o = self.chart.get_data(); conn = db_manager.conn; cur = conn.cursor(); desc = self.proc_display.toPlainText()
            cur.execute("UPDATE visits SET visit_date=?, visit_time=?, description=?, ortho_data=?, ortho_brand=?, teeth_data=?, general_notes=? WHERE id=?",
                       (self.date_input.date().toString("yyyy-MM-dd"), self.time_input.time().toString("HH:mm"), desc, json.dumps(o), self.ortho_brand.text(), json.dumps(t), self.notes_input.toPlainText(), self.visit_id))
            conn.commit(); log_activity(f"Edited visit {self.visit_id}", self.ps.patient_id); self.load_data(); self.set_editing(False)
            if hasattr(self.ps, 'load_patient_data'): self.ps.load_patient_data()
            QMessageBox.information(self, "Success", "Visit details updated successfully.")
        except Exception as e: QMessageBox.critical(self, "Error", f"Could not update visit: {e}")

class ReceiptDialog(QDialog):
    def __init__(self, payment_id, patient_screen, parent=None):
        super().__init__(parent); self.payment_id = payment_id; self.ps = patient_screen; self.patient_id = None
        self.setWindowTitle("Payment Receipt"); self.resize(500, 700); self.init_ui(); self.load_data()

    def print_receipt(self):
        try:
            filename = f"receipt_{self.payment_id}.txt"
            with open(filename, "w") as f:
                f.write(f"Clinic Header: {self.header_edit.toPlainText()}\nDate: {self.date_lbl.text()}\nType: {self.type_lbl.text()}\nTotal: {self.amount_lbl.text()}\nPaid: {self.paid_lbl.text()}\nBalance: {self.bal_lbl.text()}\nProcedures: {self.receipt_summary.text()}\nFooter: {self.footer_edit.toPlainText()}\n")
            QMessageBox.information(self, "Print", f"Receipt saved to {filename}")
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to print: {e}")

    def init_ui(self):
        l = QVBoxLayout(); scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget(); scroll_layout = QVBoxLayout(scroll_content); scroll_layout.setContentsMargins(0, 0, 0, 0); scroll_layout.setSpacing(15)
        info_card = QFrame(); info_card.setStyleSheet(CARD_STYLE); icl = QVBoxLayout(info_card)
        self.receipt_summary = QLabel("Loading details..."); self.receipt_summary.setWordWrap(True); self.receipt_summary.setStyleSheet("font-size: 11pt; padding: 10px; color: black;")
        icl.addWidget(QLabel("<b>Clinic Information:</b>")); self.header_edit = QTextEdit(); self.header_edit.setFixedHeight(80); self.header_edit.setReadOnly(True); icl.addWidget(self.header_edit)
        edit_header = QPushButton("Edit Header (Admin)"); edit_header.setStyleSheet(BUTTON_STYLE + "font-size: 9pt; padding: 5px;"); edit_header.clicked.connect(lambda: self.edit_setting_internal('receipt_header', self.header_edit)); icl.addWidget(edit_header); scroll_layout.addWidget(info_card)
        f_card = QFrame(); f_card.setStyleSheet(CARD_STYLE); fcl = QFormLayout(f_card)
        self.date_lbl = QLabel("N/A"); self.type_lbl = QLabel("N/A"); self.p_type_lbl = QLabel("N/A"); self.amount_lbl = QLabel("PHP 0.00"); self.paid_lbl = QLabel("PHP 0.00"); self.bal_lbl = QLabel("PHP 0.00")
        fcl.addRow("Date:", self.date_lbl); fcl.addRow("Payment Type:", self.type_lbl); fcl.addRow("Patient Type:", self.p_type_lbl); fcl.addRow("Total Amount:", self.amount_lbl); fcl.addRow("Amount Paid (This Trans):", self.paid_lbl); fcl.addRow("Remaining Balance:", self.bal_lbl); scroll_layout.addWidget(f_card)
        summary_card = QFrame(); summary_card.setStyleSheet(CARD_STYLE); scl = QVBoxLayout(summary_card); scl.addWidget(self.receipt_summary); scroll_layout.addWidget(summary_card)
        footer_card = QFrame(); footer_card.setStyleSheet(CARD_STYLE); fcl_foot = QVBoxLayout(footer_card); fcl_foot.addWidget(QLabel("<b>Notes / Footer:</b>"))
        self.footer_edit = QTextEdit(); self.footer_edit.setFixedHeight(60); self.footer_edit.setReadOnly(True); fcl_foot.addWidget(self.footer_edit)
        edit_footer = QPushButton("Edit Footer (Admin)"); edit_footer.setStyleSheet(BUTTON_STYLE + "font-size: 9pt; padding: 5px;"); edit_footer.clicked.connect(lambda: self.edit_setting_internal('receipt_footer', self.footer_edit)); fcl_foot.addWidget(edit_footer); scroll_layout.addWidget(footer_card)
        scroll.setWidget(scroll_content); l.addWidget(scroll); bl = QHBoxLayout()
        self.print_btn = QPushButton("Print Receipt"); self.print_btn.clicked.connect(self.print_receipt); bl.addWidget(self.print_btn); close = QPushButton("Close"); close.setStyleSheet(BUTTON_STYLE); close.clicked.connect(self.accept); bl.addWidget(close); l.addLayout(bl); self.setLayout(l)

    def edit_setting_internal(self, key, widget):
        try:
            pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password:", QLineEdit.EchoMode.Password)
            if not ok or not self.ps.check_password(pwd): QMessageBox.warning(self, "Denied", "Wrong password."); return
            new_val, ok = QInputDialog.getMultiLineText(self, "Edit Setting", f"Update {key}:", widget.toPlainText())
            if ok:
                conn = db_manager.conn; cursor = conn.cursor(); cursor.execute("INSERT OR REPLACE INTO clinic_settings (key, value) VALUES (?, ?)", (key, new_val)); conn.commit(); widget.setPlainText(new_val); log_activity(f"Updated clinic setting: {key}")
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to update setting: {str(e)}")

    def load_data(self):
        try:
            conn = db_manager.conn; cursor = conn.cursor()
            # Fetch current payment
            cursor.execute("SELECT patient_id, payment_date, payment_type, amount, discount, amount_paid, balance, visit_id, received_by, parent_id FROM payments WHERE id=?", (self.payment_id,))
            p = cursor.fetchone()
            if not p: return
            # Determine Patient Type
            cursor.execute("SELECT teeth_data, ortho_data FROM visits WHERE patient_id=? ORDER BY visit_date DESC LIMIT 1", (self.patient_id,))
            v_type_row = cursor.fetchone()
            p_type_str = "Adult"
            if v_type_row:
                t_json, o_json = v_type_row
                t_data = json.loads(t_json) if t_json else {}
                o_data = json.loads(o_json) if o_json else {}
                if o_data: p_type_str = "Orthodontic"
                else:
                    for k in t_data.keys():
                        try:
                            if int(k) > 32: p_type_str = "Child"; break
                        except: p_type_str = "Child"; break

            self.patient_id, p_date, p_type, p_amt, p_discount, p_paid, p_bal, v_id, received_by, parent_id = p
            
            # Determine effective root payment ID for balance history
            root_id = parent_id if parent_id else self.payment_id
            
            # Calculate total paid for this transaction chain
            cursor.execute("SELECT payment_date, amount_paid FROM payments WHERE id=? OR parent_id=?", (root_id, root_id))
            all_payments = cursor.fetchall()
            total_history_paid = sum(r[1] for r in all_payments)
            
            # Fetch patient details for type
            cursor.execute("SELECT name FROM patients WHERE id=?", (self.patient_id,))
            patient_name = cursor.fetchone()[0]

            self.date_lbl.setText(p_date or "N/A")
            self.type_lbl.setText(p_type or "N/A")
            self.p_type_lbl.setText(p_type_str)
            self.amount_lbl.setText(f"PHP {p_amt:,.2f}")
            self.paid_lbl.setText(f"PHP {p_paid:,.2f}")
            self.bal_lbl.setText(f"PHP {p_bal:,.2f}")
            
            summary = ""
            summary += f"<b>Patient:</b> {patient_name}<br><br>"
            
            # Visit details if linked
            if v_id:
                cursor.execute("SELECT description, teeth_data, ortho_data, ortho_brand, general_notes FROM visits WHERE id=?", (v_id,))
                v = cursor.fetchone()
                if v:
                    proc, t_json, o_json, o_brand, notes = v; t_data = json.loads(t_json) if t_json else {}; o_data = json.loads(o_json) if o_json else {}
                    summary += f"<b>Procedure:</b> {proc if proc else 'None'}<br>"
                    if notes: summary += f"<b>Notes:</b> {notes}<br>"
                    if t_data or o_data:
                        summary += "<b>Teeth:</b> "
                        t_list = []
                        for t_num, details in t_data.items():
                            flag = details.get('flag', '') if isinstance(details, dict) else details
                            t_list.append(f"T{t_num}" + (f"({flag})" if flag else ""))
                        for t_num, details in o_data.items():
                            flag = details.get('flag', '') if isinstance(details, dict) else details
                            t_list.append(f"O{t_num}" + (f"({flag})" if flag else ""))
                        summary += ", ".join(t_list) + "<br>"
                    if o_brand: summary += f"<b>Ortho Brand:</b> {o_brand}<br>"
                summary += "<br>"

            # Payment History
            summary += f"<b>Payment History for this Transaction:</b><br>"
            summary += f"Total Paid to Date: <b>PHP {total_history_paid:,.2f}</b><br>"
            summary += "<table width='100%' border='0' cellspacing='0' cellpadding='2'>"
            summary += "<tr><td align='left'><b>Date</b></td><td align='right'><b>Amount Paid</b></td></tr>"
            for r_date, r_paid in sorted(all_payments, key=lambda x: x[0]):
                summary += f"<tr><td align='left'>{r_date}</td><td align='right'>PHP {r_paid:,.2f}</td></tr>"
            summary += "</table><br>"

            if received_by: summary += f"<b>Received By:</b> {received_by}<br>"
            
            self.receipt_summary.setText(summary)
            
            cursor.execute("SELECT value FROM clinic_settings WHERE key='receipt_header'"); h = cursor.fetchone(); self.header_edit.setPlainText(h[0] if h else "")
            cursor.execute("SELECT value FROM clinic_settings WHERE key='receipt_footer'"); f = cursor.fetchone(); self.footer_edit.setPlainText(f[0] if f else "")
        except Exception as e: QMessageBox.critical(self, "Receipt Error", f"Failed to load: {str(e)}"); self.reject()

class ReceivedByManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Received By Options"); self.resize(350, 450); self.selected_name = None; self.init_ui(); self.load_options()

    def init_ui(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE); l = QVBoxLayout(self); container = QFrame(); container.setStyleSheet(CARD_STYLE); cl = QVBoxLayout(container)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search names..."); self.search.textChanged.connect(self.filter_list)
        self.list = QListWidget(); self.list.setStyleSheet(TABLE_STYLE); self.list.itemDoubleClicked.connect(self.select_and_close)
        cl.addWidget(QLabel("<b>Received By Names:</b>")); cl.addWidget(self.search); cl.addWidget(self.list)
        bl = QHBoxLayout(); add = QPushButton("Add"); add.setStyleSheet(BUTTON_STYLE); add.clicked.connect(self.add_opt)
        edit = QPushButton("Rename"); edit.setStyleSheet(BUTTON_STYLE); edit.clicked.connect(self.rename_opt)
        rem = QPushButton("Delete"); rem.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 12px; padding: 10px;"); rem.clicked.connect(self.rem_opt)
        bl.addWidget(add); bl.addWidget(edit); bl.addWidget(rem); cl.addLayout(bl)
        sel_btn = QPushButton("Select Name"); sel_btn.setStyleSheet(BUTTON_STYLE); sel_btn.clicked.connect(self.select_and_close); cl.addWidget(sel_btn); l.addWidget(container)

    def load_options(self):
        self.list.clear()
        try:
            conn = db_manager.conn; cur = conn.cursor(); cur.execute("CREATE TABLE IF NOT EXISTS received_by_options (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)"); cur.execute("SELECT name FROM received_by_options ORDER BY name")
            for r in cur.fetchall(): self.list.addItem(r[0])
        except: pass

    def filter_list(self, text):
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item: item.setHidden(text.lower() not in item.text().lower())

    def add_opt(self):
        name, ok = QInputDialog.getText(self, "Add", "Name:")
        if ok and name.strip():
            try:
                conn = db_manager.conn; cur = conn.cursor(); cur.execute("INSERT INTO received_by_options (name) VALUES (?)", (name.strip(),)); conn.commit(); self.load_options()
            except: QMessageBox.warning(self, "Error", "Name already exists.")

    def rename_opt(self):
        item = self.list.currentItem()
        if not item: return
        new, ok = QInputDialog.getText(self, "Rename", "New Name:", text=item.text())
        if ok and new.strip():
            try:
                conn = db_manager.conn; cur = conn.cursor(); cur.execute("UPDATE received_by_options SET name=? WHERE name=?", (new.strip(), item.text())); conn.commit(); self.load_options()
            except: pass

    def rem_opt(self):
        item = self.list.currentItem()
        if not item: return
        if QMessageBox.question(self, "Delete", f"Delete {item.text()}?") == QMessageBox.StandardButton.Yes:
            try:
                conn = db_manager.conn; cur = conn.cursor(); cur.execute("DELETE FROM received_by_options WHERE name=?", (item.text(),)); conn.commit(); self.load_options()
            except: pass

    def select_and_close(self):
        item = self.list.currentItem()
        if item: self.selected_name = item.text(); self.accept()

class PatientScreen(QWidget):
    def __init__(self, patient_id=None):
        super().__init__(); self.patient_id = patient_id; self.is_editing = False
        self.name_input = QLineEdit(); self.address_input = QLineEdit(); self.phone_input = QLineEdit()
        self.occupation_input = QLineEdit(); self.complaint_input = QTextEdit(); self.med_history_input = QTextEdit()
        self.birthdate_input = QDateEdit(); self.birthdate_input.setCalendarPopup(True); self.birthdate_input.setDisplayFormat("yyyy/MM/dd")
        if self.birthdate_input.calendarWidget(): self.birthdate_input.calendarWidget().setGridVisible(False)
        self.age_input = QLineEdit(); self.age_input.setFixedWidth(60); self.birthdate_input.dateChanged.connect(self.update_age_from_birthdate)
        self.init_ui()
        if self.patient_id:
            try: self.load_patient_data()
            except Exception as e: QMessageBox.critical(self, "Error", f"Could not load patient: {e}")
        else: self.set_editing(True)

    def update_age_from_birthdate(self, date):
        today = QDate.currentDate(); age = today.year() - date.year()
        if today.month() < date.month() or (today.month() == date.month() and today.day() < date.day()): age -= 1
        self.age_input.setText(str(max(0, age)))

    def init_ui(self):
        layout = QVBoxLayout(); self.name_lbl = QLabel("Patient: Loading..."); self.name_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2c3e50; border: none; background: transparent;")
        hl = QHBoxLayout(); back_btn = QPushButton("← Back"); back_btn.setFixedWidth(100); back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(lambda: self.window().show_dashboard() if self.window() and hasattr(self.window(), 'show_dashboard') else None)
        hl.addWidget(back_btn); hl.addWidget(self.name_lbl); hl.addStretch()
        if self.patient_id:
            prof_btn = QPushButton("View Profile"); prof_btn.setStyleSheet(BUTTON_STYLE); prof_btn.clicked.connect(self.open_profile_dialog); hl.addWidget(prof_btn)
        layout.addLayout(hl); layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(20)
        self.tabs = QTabWidget(); self.tabs.setStyleSheet("""QTabWidget::pane { border: 1px solid #e0e0e0; border-radius: 12px; background: white; } QTabBar::tab { background: #f5f7fa; padding: 12px 24px; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 4px; color: #7f8c8d; font-weight: bold; font-size: 12pt; } QTabBar::tab:selected { background: white; border: 1px solid #e0e0e0; border-bottom-color: white; color: #4a90e2; }""")
        if not self.patient_id: self.tabs.addTab(self.create_profile_tab(), "Profile")
        self.tabs.addTab(self.create_visits_tab(), "Visits & Chart"); self.tabs.addTab(self.create_payments_tab(), "Payments"); layout.addWidget(self.tabs); self.setLayout(layout)

    def create_profile_tab(self):
        w = QWidget(); l = QVBoxLayout(); f = QFormLayout()
        for i in [self.name_input, self.address_input, self.phone_input, self.occupation_input, self.complaint_input, self.med_history_input, self.age_input]: i.setStyleSheet(INPUT_STYLE + "color: black;"); i.setReadOnly(False)
        birth_age_layout = QHBoxLayout(); self.birthdate_input.setCalendarPopup(True); self.birthdate_input.setStyleSheet(INPUT_STYLE + "color: black;"); self.update_age_from_birthdate(self.birthdate_input.date())
        birth_age_layout.addWidget(self.birthdate_input); birth_age_layout.addWidget(QLabel("Age:")); birth_age_layout.addWidget(self.age_input)
        f.addRow("Name:", self.name_input); f.addRow("Address:", self.address_input); f.addRow("Phone:", self.phone_input); f.addRow("Birthdate:", birth_age_layout); f.addRow("Occupation:", self.occupation_input); f.addRow("Complaint:", self.complaint_input); f.addRow("Med History:", self.med_history_input)
        l.addLayout(f); bl = QHBoxLayout(); self.edit_btn = QPushButton("Edit Profile"); self.edit_btn.clicked.connect(self.toggle_edit); self.edit_btn.hide(); self.save_btn = QPushButton("Save New Patient"); self.save_btn.clicked.connect(self.save_profile); self.save_btn.show(); bl.addWidget(self.edit_btn); bl.addWidget(self.save_btn); l.addLayout(bl); w.setLayout(l); return w

    def create_visits_tab(self):
        w = QWidget(); main_layout = QHBoxLayout(w); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(10)
        left_scroll = QScrollArea(); left_scroll.setWidgetResizable(True); left_scroll.setFrameShape(QFrame.Shape.NoFrame); left_scroll.setStyleSheet("background: transparent; border: none;")
        left_container = QWidget(); left_container.setStyleSheet("background-color: #f5f7fa; border: none;"); left_layout = QVBoxLayout(left_container); left_layout.setContentsMargins(10, 10, 10, 10); left_layout.setSpacing(15)
        vf = QFrame(); vf.setStyleSheet(CARD_STYLE + "border: none;"); vfl = QFormLayout(vf); vfl.setSpacing(10); label_style = "border: none; background: transparent; color: #333333; font-weight: bold;"
        l_date = QLabel("Date:"); l_date.setStyleSheet(label_style); self.v_date = QDateEdit(QDate.currentDate()); self.v_date.setCalendarPopup(True); self.v_date.setDisplayFormat("yyyy/MM/dd")
        if self.v_date.calendarWidget(): self.v_date.calendarWidget().setGridVisible(False)
        self.v_date.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; color: black;"); l_time = QLabel("Time:"); l_time.setStyleSheet(label_style); self.v_time = QTimeEdit(QTime.currentTime()); self.v_time.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; color: black;")
        l_proc = QLabel("Procedures:"); l_proc.setStyleSheet(label_style); proc_container = QWidget(); proc_layout = QVBoxLayout(proc_container); proc_layout.setContentsMargins(0, 0, 0, 0); proc_layout.setSpacing(2)
        self.proc_search = QLineEdit(); self.proc_search.setPlaceholderText("Search procedures..."); self.proc_search.setStyleSheet(INPUT_STYLE + "height: 25px; font-size: 9pt;"); self.proc_search.textChanged.connect(self.filter_procedures)
        self.desc_list = QListWidget(); self.desc_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection); self.desc_list.setFixedHeight(120); self.desc_list.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; color: black;")
        self.load_desc_options(); proc_layout.addWidget(self.proc_search); proc_layout.addWidget(self.desc_list)
        edit_desc = QPushButton("Edit Options (Admin)"); edit_desc.setStyleSheet("QPushButton { background-color: #34495e; color: white; border-radius: 12px; padding: 5px; font-size: 10pt; }"); edit_desc.clicked.connect(self.open_desc_manager); l_notes = QLabel("Notes:"); l_notes.setStyleSheet(label_style); self.v_notes = QTextEdit(); self.v_notes.setPlaceholderText("General notes for this visit..."); self.v_notes.setFixedHeight(80); self.v_notes.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; color: black;")
        self.v_ortho_brand_label = QLabel("Brand:"); self.v_ortho_brand_label.setStyleSheet(label_style); self.v_ortho_brand = QLineEdit(); self.v_ortho_brand.setPlaceholderText("Brand"); self.v_ortho_brand.setStyleSheet(INPUT_STYLE + "border: 1px solid #e0e0e0; color: black;"); self.v_ortho_brand.setVisible(False); self.v_ortho_brand_label.setVisible(False)
        self.sel_lbl = QLabel("Selected: None"); self.sel_lbl.setWordWrap(True); self.sel_lbl.setStyleSheet("color: #4a90e2; font-weight: bold; font-size: 10pt; border: none; background: transparent;")
        vfl.addRow(l_date, self.v_date); vfl.addRow(l_time, self.v_time); vfl.addRow(l_proc, proc_container); vfl.addRow("", edit_desc); vfl.addRow(l_notes, self.v_notes); vfl.addRow(self.v_ortho_brand_label, self.v_ortho_brand); vfl.addRow(self.sel_lbl)
        add_v = QPushButton("Add Visit Record"); add_v.setStyleSheet(BUTTON_STYLE); add_v.clicked.connect(self.add_visit); left_layout.addWidget(vf); left_layout.addWidget(add_v); self.v_table = QTableWidget(); self.v_table.setColumnCount(4); self.v_table.setHorizontalHeaderLabels(["Date", "Time", "Description", "Action"]); self.v_table.setStyleSheet(TABLE_STYLE); self.v_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.v_table.verticalHeader().setVisible(False); self.v_table.setFixedHeight(300); left_layout.addWidget(self.v_table); left_layout.addStretch(); left_scroll.setWidget(left_container); main_layout.addWidget(left_scroll, 2)
        self.tooth_chart_container = QFrame(); self.tooth_chart_container.setStyleSheet(CARD_STYLE); right_layout = QVBoxLayout(self.tooth_chart_container); self.chart = DentalChart(); self.chart.selection_changed.connect(self.on_chart_change); self.chart.tabs.currentChanged.connect(self.update_visit_ortho_visibility); right_layout.addWidget(self.chart); main_layout.addWidget(self.tooth_chart_container, 3); self.update_visit_ortho_visibility(); return w

    def update_visit_ortho_visibility(self):
        is_ortho = self.chart.tabs.tabText(self.chart.tabs.currentIndex()) == "Orthodontics"
        self.v_ortho_brand.setVisible(is_ortho); self.v_ortho_brand_label.setVisible(is_ortho)

    def create_payments_tab(self):
        w = QWidget(); l = QVBoxLayout(); fl = QHBoxLayout(); fl.setSpacing(10)
        self.p_type = QComboBox(); self.p_type.addItems(["New Payment", "Pay Balance", "Partial Payment"]); self.p_type.setStyleSheet(INPUT_STYLE); self.p_type.currentIndexChanged.connect(self.on_payment_type_changed)
        self.p_date = QDateEdit(QDate.currentDate()); self.p_date.setCalendarPopup(True); self.p_date.setDisplayFormat("yyyy/MM/dd")
        if self.p_date.calendarWidget(): self.p_date.calendarWidget().setGridVisible(False)
        self.p_date.setStyleSheet(INPUT_STYLE); self.p_amount_lbl = QLabel("Total:"); self.p_amount = QLineEdit(); self.p_amount.setPlaceholderText("Total Amount"); self.p_amount.setStyleSheet(INPUT_STYLE)
        self.p_discount_lbl = QLabel("Disc:"); self.p_discount = QLineEdit(); self.p_discount.setPlaceholderText("Discount"); self.p_discount.setStyleSheet(INPUT_STYLE); self.p_paid = QLineEdit(); self.p_paid.setPlaceholderText("Amount"); self.p_paid.setStyleSheet(INPUT_STYLE)
        from PyQt6.QtGui import QDoubleValidator
        v = QDoubleValidator(0.0, 9999999.0, 2); v.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.p_amount.setValidator(v); self.p_discount.setValidator(v); self.p_paid.setValidator(v); add_p = QPushButton("Add Payment"); add_p.setStyleSheet(BUTTON_STYLE); add_p.clicked.connect(self.add_payment)
        fl.addWidget(QLabel("Type:")); fl.addWidget(self.p_type); fl.addWidget(self.p_date); fl.addWidget(self.p_amount_lbl); fl.addWidget(self.p_amount); fl.addWidget(self.p_discount_lbl); fl.addWidget(self.p_discount); fl.addWidget(QLabel("Paid:")); fl.addWidget(self.p_paid); fl.addWidget(add_p)
        l.addLayout(fl); self.p_table = QTreeWidget(); self.p_table.setColumnCount(8); self.p_table.setHeaderLabels(["Date", "Type", "Total", "Discount", "Paid", "Balance", "Received By", "Action"]); self.p_table.setStyleSheet(TABLE_STYLE); self.p_table.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); l.addWidget(self.p_table); w.setLayout(l); return w

    def delete_visit(self, vid):
        pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password to Delete Visit:", QLineEdit.EchoMode.Password)
        if ok and self.check_password(pwd):
            if QMessageBox.question(self, "Confirm", "Delete this visit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                try:
                    conn = db_manager.conn; cur = conn.cursor(); cur.execute("DELETE FROM visits WHERE id=?", (vid,)); conn.commit(); log_activity(f"Deleted visit {vid}", self.patient_id); self.load_patient_data()
                except Exception as e: QMessageBox.critical(self, "Error", str(e))
        elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")

    def delete_payment(self, pid):
        pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password to Delete Payment:", QLineEdit.EchoMode.Password)
        if ok and self.check_password(pwd):
            if QMessageBox.question(self, "Confirm", "Delete this payment?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                try:
                    conn = db_manager.conn; cur = conn.cursor(); cur.execute("DELETE FROM payments WHERE id=?", (pid,)); conn.commit(); log_activity(f"Deleted payment {pid}", self.patient_id); self.load_patient_data()
                except Exception as e: QMessageBox.critical(self, "Error", str(e))
        elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")

    def open_received_by_manager(self, pid, current_name):
        dialog = ReceivedByManager(self)
        if dialog.exec():
            name = dialog.selected_name
            if name:
                try:
                    conn = db_manager.conn; cur = conn.cursor(); cur.execute("UPDATE payments SET received_by=? WHERE id=?", (name, pid)); conn.commit(); self.load_patient_data()
                except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def on_payment_type_changed(self):
        pt = self.p_type.currentText()
        is_new_or_partial = pt in ["New Payment", "Partial Payment"]
        self.p_amount.setVisible(is_new_or_partial); self.p_amount_lbl.setVisible(is_new_or_partial); self.p_discount.setVisible(is_new_or_partial); self.p_discount_lbl.setVisible(is_new_or_partial)

    def filter_procedures(self, text):
        for i in range(self.desc_list.count()):
            item = self.desc_list.item(i)
            if item: item.setHidden(text.lower() not in item.text().lower())

    def open_profile_dialog(self): 
        try: PatientProfileDialog(self, self).exec()
        except Exception as e: QMessageBox.critical(self, "Error", f"Could not open profile: {e}")

    def on_chart_change(self):
        t, o = self.chart.get_data(); names = [f"T{k}" for k in t.keys()] + [f"O{k}" for k in o.keys()]; self.sel_lbl.setText("Selected: " + (", ".join(names) if names else "None"))

    def load_desc_options(self):
        try:
            self.desc_list.clear(); conn = db_manager.conn; cur = conn.cursor(); cur.execute("SELECT name FROM description_options ORDER BY name")
            for r in cur.fetchall(): self.desc_list.addItem(r[0])
        except Exception as e: print(f"Error loading options: {e}")

    def open_desc_manager(self):
        pwd, ok = QInputDialog.getText(self, "Admin", "Admin Password:", QLineEdit.EchoMode.Password)
        if ok and self.check_password(pwd):
            if DescriptionManager(self).exec(): self.load_desc_options()
        elif ok: QMessageBox.warning(self, "Denied", "Wrong password.")

    def add_visit(self):
        if not self.patient_id: QMessageBox.warning(self, "Error", "Save patient profile first."); return
        sel = [i.text() for i in self.desc_list.selectedItems()]
        if not sel: QMessageBox.warning(self, "Error", "Select procedure."); return
        t, o = self.chart.get_data()
        try:
            from ..database import save_visit
            if save_visit(self.patient_id, self.v_date.date().toString("yyyy-MM-dd"), self.v_time.time().toString("HH:mm"), ", ".join(sel), o, self.v_ortho_brand.text(), t, self.v_notes.toPlainText()):
                log_activity(f"Added visit", self.patient_id); self.load_patient_data(); self.v_notes.clear(); self.v_ortho_brand.clear()
                if hasattr(self.chart, "clear_selection"): self.chart.clear_selection()
                if hasattr(self.chart, "clear_all_flags"): self.chart.clear_all_flags()
                self.desc_list.clearSelection(); self.sel_lbl.setText("Selected: None")
        except Exception as e: QMessageBox.critical(self, "Error", f"Could not add visit: {e}")

    def add_payment(self):
        if not self.patient_id: return
        try:
            conn = db_manager.conn
            with conn:
                cur = conn.cursor(); pt = self.p_type.currentText(); is_bal = pt == "Pay Balance"; selected_id = None
                if is_bal:
                    items = []
                    cur.execute("SELECT id, payment_date, balance, payment_type FROM payments WHERE patient_id=? AND balance > 0 AND parent_id IS NULL ORDER BY payment_date DESC", (self.patient_id,))
                    rows = cur.fetchall()
                    if not rows: QMessageBox.information(self, "Balance", "No outstanding unpaid transactions found."); return
                    for r in rows: items.append(f"ID: {r[0]} | Date: {r[1]} | {r[3]} | Bal: PHP {r[2]:,.2f}")
                    item, ok = QInputDialog.getItem(self, "Select Balance", "Select transaction to pay:", items, 0, False)
                    if not ok: return
                    selected_id = int(item.split(" | ")[0].split(": ")[1]); cur.execute("SELECT balance FROM payments WHERE id=?", (selected_id,))
                    total_bal = cur.fetchone()[0]; ps = self.p_paid.text().strip()
                    if not ps: QMessageBox.warning(self, "Error", "Enter amount to pay."); return
                    paid = float(ps)
                    if paid > total_bal: QMessageBox.warning(self, "Error", f"Max: PHP {total_bal:,.2f}"); return
                    new_bal = total_bal - paid; total = total_bal; discount = 0; cur.execute("UPDATE payments SET balance=? WHERE id=?", (new_bal, selected_id))
                else:
                    ps = self.p_paid.text().strip(); as_ = self.p_amount.text().strip(); ds = self.p_discount.text().strip() or "0"
                    if not ps or not as_: QMessageBox.warning(self, "Error", "Enter amount and paid values."); return
                    paid = float(ps); total = float(as_); discount = float(ds)
                    if paid > (total - discount): QMessageBox.warning(self, "Error", "Overpayment not allowed."); return
                    new_bal = total - discount - paid
                cur.execute("INSERT INTO payments (patient_id, payment_date, payment_type, amount, discount, amount_paid, balance, parent_id) VALUES (?,?,?,?,?,?,?,?)", (self.patient_id, self.p_date.date().toString("yyyy-MM-dd"), pt, total, discount, paid, new_bal, selected_id))
                conn.commit(); log_activity(f"Added payment", self.patient_id); self.load_patient_data(); self.p_amount.clear(); self.p_discount.clear(); self.p_paid.clear()
        except Exception as e: QMessageBox.warning(self, "Error", f"Invalid input: {e}")

    def load_patient_data(self):
        if not self.patient_id: return
        try:
            conn = db_manager.conn
            with conn:
                cur = conn.cursor(); cur.execute("SELECT name, address, phone, birthdate, occupation_status, complaint, medical_history FROM patients WHERE id=?", (self.patient_id,))
                p = cur.fetchone()
                if p:
                    self.name_lbl.setText(f"Patient: {p[0]}"); self.name_input.setText(p[0]); self.address_input.setText(p[1]); self.phone_input.setText(p[2])
                    if p[3]: self.birthdate_input.setDate(QDate.fromString(p[3], "yyyy-MM-dd"))
                    self.occupation_input.setText(p[4]); self.complaint_input.setText(p[5]); self.med_history_input.setText(p[6])
                cur.execute("SELECT id, visit_date, visit_time, description FROM visits WHERE patient_id=? ORDER BY visit_date DESC", (self.patient_id,))
                rows = cur.fetchall(); self.v_table.setRowCount(len(rows))
                for i, r in enumerate(rows):
                    for j in range(3): self.v_table.setItem(i, j, QTableWidgetItem(str(r[j+1])))
                    bc = QWidget(); bl = QHBoxLayout(bc); bl.setContentsMargins(0, 0, 0, 0); bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    btn = QPushButton("View"); btn.setStyleSheet(BUTTON_STYLE + "font-size: 9pt; padding: 2px;"); btn.setFixedWidth(80); btn.clicked.connect(lambda _, vid=r[0]: self.view_visit(vid))
                    bl.addWidget(btn); self.v_table.setCellWidget(i, 3, bc); self.v_table.setRowHeight(i, 45)
                self.p_table.clear(); self.p_table.setStyleSheet(TABLE_STYLE + "QTreeWidget { background-color: white; color: black; } QTreeWidget::item { color: black; border-bottom: 1px solid #e0e0e0; }"); cur.execute("SELECT id, payment_date, payment_type, amount, discount, amount_paid, balance, received_by FROM payments WHERE patient_id=? AND parent_id IS NULL ORDER BY payment_date DESC", (self.patient_id,))
                for pr in cur.fetchall():
                    pi = QTreeWidgetItem(self.p_table); pid = pr[0]; pi.setText(0, str(pr[1])); pi.setText(1, str(pr[2])); pi.setText(2, f"{pr[3]:,.2f}"); pi.setText(3, f"{pr[4]:,.2f}"); pi.setText(4, f"{pr[5]:,.2f}"); pi.setText(5, f"{pr[6]:,.2f}"); pi.setText(6, str(pr[7] or "N/A"))
                    bc = QWidget(); bl = QHBoxLayout(bc); bl.setContentsMargins(0, 0, 0, 0); rb = QPushButton("Receipt"); rb.setStyleSheet(BUTTON_STYLE + "font-size: 8pt; padding: 2px;"); rb.clicked.connect(lambda _, id=pid: self.view_receipt(id)); bl.addWidget(rb)
                    if not pr[7] or pr[7] == "N/A":
                        by = QPushButton("By"); by.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px; font-size: 8pt; padding: 2px;"); by.clicked.connect(lambda _, id=pid, n=pr[7]: self.open_received_by_manager(id, n)); bl.addWidget(by)
                    db = QPushButton("Del"); db.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 8px; font-size: 8pt; padding: 2px;"); db.clicked.connect(lambda _, id=pid: self.delete_payment(id)); bl.addWidget(db); self.p_table.setItemWidget(pi, 7, bc)
                    cur.execute("SELECT id, payment_date, payment_type, amount, discount, amount_paid, balance, received_by FROM payments WHERE parent_id=? ORDER BY payment_date DESC", (pid,))
                    for cr in cur.fetchall():
                        ci = QTreeWidgetItem(pi); cid = cr[0]; ci.setText(0, str(cr[1])); ci.setText(1, str(cr[2])); ci.setText(2, "-"); ci.setText(3, "-"); ci.setText(4, f"{cr[5]:,.2f}"); ci.setText(5, f"{cr[6]:,.2f}"); ci.setText(6, str(cr[7] or "N/A"))
                        cbc = QWidget(); cbl = QHBoxLayout(cbc); cbl.setContentsMargins(0, 0, 0, 0)
                        if not cr[7] or cr[7] == "N/A":
                            cby = QPushButton("By"); cby.setStyleSheet("background-color: #27ae60; color: white; border-radius: 8px; font-size: 8pt; padding: 2px;"); cby.clicked.connect(lambda _, id=cid, n=cr[7]: self.open_received_by_manager(id, n)); cbl.addWidget(cby)
                        cdb = QPushButton("Del"); cdb.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 8px; font-size: 8pt; padding: 2px;"); cdb.clicked.connect(lambda _, id=cid: self.delete_payment(id)); cbl.addWidget(cdb); self.p_table.setItemWidget(ci, 7, cbc)
                self.p_table.expandAll()
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def view_visit(self, vid):
        if VisitDetailDialog(vid, self, self).exec(): self.load_patient_data()

    def view_receipt(self, pid): ReceiptDialog(pid, self, self).exec()

    def check_password(self, pwd):
        import sys
        try:
            if getattr(sys, 'frozen', False): path = os.path.join(os.path.dirname(sys.executable), "password.txt")
            else:
                path = os.path.join(get_app_dir(), "password.txt")
                if not os.path.exists(path): path = os.path.join(get_app_dir(), "..", "password.txt")
            if not os.path.exists(path): return pwd == "admin123"
            with open(path, "r") as f: return pwd == f.read().strip()
        except: return pwd == "admin123"

    def set_editing(self, e): self.is_editing = e

    def toggle_edit(self):
        pwd, ok = QInputDialog.getText(self, "Auth", "Admin Password:", QLineEdit.EchoMode.Password)
        if ok and self.check_password(pwd):
            # For now, we just allow editing the name as a test
            self.name_input.setReadOnly(False)
            self.edit_btn.hide()
            self.save_btn.show()
        elif ok:
            QMessageBox.warning(self, "Denied", "Wrong password.")

    def save_profile(self):
        try:
            name = self.name_input.text().strip()
            if not name: QMessageBox.warning(self, "Validation", "Name required."); return
            conn = db_manager.conn
            with conn:
                cur = conn.cursor(); d = (name, self.address_input.text(), self.phone_input.text(), self.birthdate_input.date().toString("yyyy-MM-dd"), self.occupation_input.text(), self.complaint_input.toPlainText(), self.med_history_input.toPlainText())
                if self.patient_id: cur.execute("UPDATE patients SET name=?, address=?, phone=?, birthdate=?, occupation_status=?, complaint=?, medical_history=? WHERE id=?", d + (self.patient_id,))
                else: cur.execute("INSERT INTO patients (name, address, phone, birthdate, occupation_status, complaint, medical_history) VALUES (?,?,?,?,?,?,?)", d); self.patient_id = cur.lastrowid
                conn.commit()
            p = self.window()
            if p and hasattr(p, 'show_dashboard'): 
                p.central_widget.setCurrentIndex(1)
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, p.dashboard_screen.refresh_data)
            else: 
                self.load_patient_data()
                self.init_ui()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))
