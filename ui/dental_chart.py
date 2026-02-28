import sqlite3
import os, sys
import json
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTabWidget, QFrame, QInputDialog, QMessageBox, QFileDialog, QToolTip,
    QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPixmap
from ..database import get_db_path, get_image_dir, db_manager

class ToothButton(QPushButton):
    def __init__(self, tooth_type, unit_id, label, x, y, image_path=None, parent=None):
        super().__init__(parent)
        self.tooth_type = tooth_type
        self.unit_id = unit_id
        self.display_label = label
        self.issue_text = ""
        self.image_path = image_path
        
        self.setFixedSize(50, 50)
        self.move(int(x), int(y))
        self.setCheckable(True)
        self.setText(label)
        self.update_style()

    def update_style(self):
        color = "white"
        border_color = "transparent"
        text_color = "black"
        
        if self.isChecked():
            if self.issue_text:
                color = "#ffd54f" # Flagged
                border_color = "#ffb300"
            else:
                color = "#4a90e2" # Selected
                border_color = "#357abd"
                text_color = "white"
        elif self.issue_text:
            color = "#fff9c4" # Flagged but not selected
            border_color = "#fff176"
            
        style = f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 25px;
                font-weight: bold;
                font-size: 10px;
                text-align: center;
                outline: none;
            }}
            QPushButton:hover {{ background-color: #f8f9fa; color: black; }}
        """
        
        if self.image_path and os.path.exists(os.path.join(get_image_dir(), self.image_path)):
            pixmap = QPixmap(os.path.join(get_image_dir(), self.image_path))
            # Fixed button size, scale image to fit
            scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setIcon(QIcon(scaled_pixmap))
            self.setIconSize(self.size())
        
        self.setStyleSheet(style)
        self.setToolTip(f"Tooth {self.display_label}\nFlag: {self.issue_text if self.issue_text else 'None'}")

class DentalChart(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tooth_buttons = {} # key: (type, unit_id)
        self.init_ui()

    def init_ui(self):
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Controls
        self.controls = QHBoxLayout()
        self.flag_btn = QPushButton("Flag Selected")
        self.flag_btn.setStyleSheet("background-color: #ffd54f; color: black; font-weight: bold; padding: 10px 20px; border-radius: 12px; border: none;")
        self.flag_btn.clicked.connect(self.on_flag_clicked)
        
        self.clear_btn = QPushButton("Clear Flags")
        self.clear_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px 20px; border-radius: 12px; border: none;")
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        
        self.edit_btn = QPushButton("Edit Tooth Details")
        self.edit_btn.setStyleSheet("background-color: #bdc3c7; color: white; font-weight: bold; padding: 10px 20px; border-radius: 12px; border: none;")
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        
        self.controls.addWidget(self.flag_btn)
        self.controls.addWidget(self.clear_btn)
        self.controls.addStretch()
        self.controls.addWidget(self.edit_btn)
        self._main_layout.addLayout(self.controls)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_chart_area("adult"), "Adult")
        self.tabs.addTab(self.create_chart_area("child"), "Child")
        self.tabs.addTab(self.create_chart_area("ortho"), "Orthodontics")
        
        self._main_layout.addWidget(self.tabs)
        self.setLayout(self._main_layout)

    def create_chart_area(self, tooth_type):
        container = QFrame()
        container.setFixedSize(750, 500)
        container.setStyleSheet("background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 18px;")
        
        # Set tab widget styling to be white
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e0e0e0; background: white; border-radius: 12px; }
            QTabBar::tab { background: #f1f1f1; color: #333; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QTabBar::tab:selected { background: white; color: #4a90e2; font-weight: bold; }
        """)
        
        try:
            conn = db_manager.conn
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT unit_id, display_label, x_pos, y_pos, image_path FROM teeth_metadata WHERE tooth_type=?", (tooth_type,))
                rows = cur.fetchall()
            
            for uid, label, x, y, img in rows:
                btn = ToothButton(tooth_type, uid, label, x, y, img, container)
                btn.clicked.connect(self.on_btn_clicked)
                self.tooth_buttons[(tooth_type, uid)] = btn
                # Do not call update_style() here, let the caller or set_data handle it
                # to avoid issues during rapid UI changes. Actually, it's safer to call it
                # but the error reported suggests images might be causing issues when 
                # buttons are re-created or updated.
                btn.update_style()
        except Exception as e:
            print(f"Error loading teeth for {tooth_type}: {e}")
            
        return container

    def on_btn_clicked(self):
        self.sender().update_style()
        self.selection_changed.emit()

    def on_flag_clicked(self):
        active_type = self.get_active_type()
        selected = [b for b in self.tooth_buttons.values() if b.tooth_type == active_type and b.isChecked()]
        
        if not selected:
            QMessageBox.information(self, "Selection", "Select teeth first.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Flag Issue")
        dialog.setMinimumSize(400, 350)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("<b>Enter issue description:</b>"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("e.g., Cavity, Root Canal needed, etc.")
        text_edit.setPlainText(selected[0].issue_text if len(selected) == 1 else "")
        layout.addWidget(text_edit)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Flag")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 12px 20px; border-radius: 12px; font-size: 11pt; border: none;")
        save_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; padding: 12px 20px; border-radius: 12px; font-size: 11pt; border: none;")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            issue = text_edit.toPlainText().strip()
            for b in selected:
                b.issue_text = issue
                b.update_style()
            self.selection_changed.emit()

    def on_clear_clicked(self):
        active_type = self.get_active_type()
        selected = [b for b in self.tooth_buttons.values() if b.tooth_type == active_type and b.isChecked()]
        
        if not selected:
            QMessageBox.information(self, "Selection", "Select teeth first.")
            return
            
        for b in selected:
            b.issue_text = ""
            b.update_style()
        self.selection_changed.emit()

    def on_edit_clicked(self):
        active_type = self.get_active_type()
        selected = [b for b in self.tooth_buttons.values() if b.tooth_type == active_type and b.isChecked()]
        
        if len(selected) != 1:
            QMessageBox.warning(self, "Selection", "Select exactly one tooth to edit.")
            return
            
        btn = selected[0]
        
        # Edit Label
        new_label, ok = QInputDialog.getText(self, "Edit Tooth", "Tooth Number/Label:", text=btn.display_label)
        if ok and new_label:
            # Edit Image
            msg = QMessageBox()
            msg.setText(f"Editing Tooth {new_label}")
            msg.setInformativeText("Would you like to change the tooth image?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            ret = msg.exec()
            
            img_path = btn.image_path
            if ret == QMessageBox.StandardButton.Yes:
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Tooth Image", "", "Images (*.png *.jpg *.jpeg)")
                if file_path:
                    filename = f"{btn.tooth_type}_{btn.unit_id}_{os.path.basename(file_path)}"
                    dest = os.path.join(get_image_dir(), filename)
                    shutil.copy2(file_path, dest)
                    img_path = filename

            # Save to DB
            try:
                conn = db_manager.conn
                cur = conn.cursor()
                cur.execute("UPDATE teeth_metadata SET display_label=?, image_path=? WHERE tooth_type=? AND unit_id=?",
                           (new_label, img_path, btn.tooth_type, btn.unit_id))
                conn.commit()
                
                btn.display_label = new_label
                btn.setText(new_label)
                btn.image_path = img_path
                btn.update_style()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def clear_selection(self):
        for b in self.tooth_buttons.values():
            if b.isChecked():
                b.setChecked(False)
                b.update_style()
        self.selection_changed.emit()

    def clear_all_flags(self):
        for b in self.tooth_buttons.values():
            if b.issue_text:
                b.issue_text = ""
                b.update_style()
        self.selection_changed.emit()

    def get_active_type(self):
        idx = self.tabs.currentIndex()
        return ["adult", "child", "ortho"][idx]

    def get_data(self):
        # We need to return data for all types for saving
        # Use custom labels instead of unit_id
        adult = {b.display_label: b.issue_text for b in self.tooth_buttons.values() if b.tooth_type == 'adult' and b.isChecked()}
        child = {b.display_label: b.issue_text for b in self.tooth_buttons.values() if b.tooth_type == 'child' and b.isChecked()}
        ortho = {b.display_label: b.issue_text for b in self.tooth_buttons.values() if b.tooth_type == 'ortho' and b.isChecked()}
        
        # Merge teeth (adult/child) vs ortho as per previous logic
        teeth = {**adult, **child}
        return teeth, ortho

    def set_data(self, teeth_data, ortho_data):
        # In View mode, we show charts for all types that have data
        # Check adult vs child vs ortho specifically
        has_adult = any(b.tooth_type == 'adult' and str(b.display_label) in teeth_data for b in self.tooth_buttons.values())
        has_child = any(b.tooth_type == 'child' and str(b.display_label) in teeth_data for b in self.tooth_buttons.values())
        has_ortho = any(b.tooth_type == 'ortho' and str(b.display_label) in ortho_data for b in self.tooth_buttons.values())
        
        # Determine visibility for each tab based on recorded flags
        self.tabs.setTabVisible(0, True)
        self.tabs.setTabVisible(1, True)
        self.tabs.setTabVisible(2, True)
        
        self.setVisible(True)
        
        for b in self.tooth_buttons.values():
            # Disconnect to prevent signals during bulk update if any
            try: b.clicked.disconnect(self.on_btn_clicked)
            except: pass
            
            b.setChecked(False)
            b.issue_text = ""
            
            val = None
            if b.tooth_type == 'ortho':
                val = ortho_data.get(str(b.display_label))
            else:
                val = teeth_data.get(str(b.display_label))
            
            if val is not None:
                b.setChecked(True)
                b.issue_text = val
            b.update_style()
            
            # Reconnect
            b.clicked.connect(self.on_btn_clicked)
        
        # Auto-tab to the first one with data
        if has_adult: self.tabs.setCurrentIndex(0)
        elif has_child: self.tabs.setCurrentIndex(1)
        elif has_ortho: self.tabs.setCurrentIndex(2)
