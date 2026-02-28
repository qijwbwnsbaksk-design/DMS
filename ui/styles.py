# Qt Style Sheets for the application

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #f5f7fa;
        color: black;
        font-family: 'Segoe UI', sans-serif;
    }
    QLabel {
        color: #333333;
    }
    QMessageBox, QDialog, QInputDialog {
        background-color: white;
        color: black;
    }
    QMessageBox QLabel, QDialog QLabel, QInputDialog QLabel {
        color: black;
        border: none;
        background: transparent;
    }
    QInputDialog QLineEdit, QInputDialog QTextEdit {
        background-color: white;
        color: black;
        border: 1px solid #e0e0e0;
    }
    QInputDialog QPlainTextEdit {
        background-color: white;
        color: black;
        border: 1px solid #e0e0e0;
    }
    QMessageBox QPushButton, QDialog QPushButton, QInputDialog QPushButton {
        padding: 8px 20px;
        border-radius: 10px;
        background-color: #4a90e2;
        color: white;
        font-weight: bold;
    }
    QMessageBox QPushButton:hover, QDialog QPushButton:hover, QInputDialog QPushButton:hover {
        background-color: #357abd;
    }
    QLabel {
        border: none;
        background: transparent;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #4a90e2;
        color: white;
        border-radius: 15px;
        padding: 10px 20px;
        font-size: 11pt;
        font-weight: 600;
        border: none;
    }
    QPushButton:hover {
        background-color: #357abd;
    }
    QPushButton:pressed {
        background-color: #2a6094;
    }
    QPushButton[styleClass="action-btn"] {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 10pt;
    }
    QPushButton[styleClass="action-btn"]:hover {
        background-color: #bbdefb;
    }
"""

LABEL_TITLE_STYLE = """
    QLabel {
        font-size: 20pt;
        font-weight: bold;
        color: #2c3e50;
        border: none;
        background: transparent;
    }
"""

LABEL_SUBTITLE_STYLE = """
    QLabel {
        font-size: 16pt;
        font-weight: bold;
        color: #34495e;
        border: none;
        background: transparent;
    }
"""

INPUT_STYLE = """
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QComboBox, QListWidget, QCalendarWidget {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 8px 12px;
        font-size: 11pt;
    }
    QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus, QListWidget:focus {
        border: 1px solid #4a90e2;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        color: #333333;
        selection-background-color: #4a90e2;
        selection-color: white;
        border: none;
    }
    QDateEdit::drop-down, QComboBox::drop-down {
        border: none;
        background: transparent;
        width: 30px;
    }
    QDateEdit::down-arrow, QComboBox::down-arrow {
        image: none;
        border: none;
    }
    QDateEdit::drop-down {
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMzMzMzMzMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSI0IiB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHJ4PSIyIiByeT0iMiI+PC9yZWN0PjpsaW5lIHgxPSIxNiIgeTE9IjIiIHgyPSIxNiIgeTI9IjYiPjwvbGluZT48bGluZSB4MT0iOCIgeTE9IjIiIHgyPSI4IiB5Mj0iNiI+PC9saW5lPjpsaW5lIHgxPSIzIiB5MT0iMTAiIHgyPSIyMSIgeTI9IjEwIj48L2xpbmU+PC9zdmc+);
        subcontrol-origin: padding;
        subcontrol-position: center right;
        margin-right: 8px;
    }
    QCalendarWidget QWidget {
        background-color: #333333;
        color: white;
        border-radius: 12px;
    }
    QCalendarWidget QToolButton {
        color: white;
        background-color: transparent;
        font-weight: bold;
    }
    QCalendarWidget QMenu {
        background-color: #333333;
        color: white;
    }
    QCalendarWidget QSpinBox {
        background-color: #444444;
        color: white;
        selection-background-color: #4a90e2;
        border-radius: 4px;
    }
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #333333;
        color: white;
        selection-background-color: #ffffff;
        selection-color: #333333;
    }
    QCalendarWidget QAbstractItemView:disabled {
        color: #666666;
    }
    QCalendarWidget #qt_calendar_navigationbar {
        background-color: #333333;
        border-bottom: 1px solid #444444;
    }
    QCalendarWidget #qt_calendar_prevmonth, QCalendarWidget #qt_calendar_nextmonth {
        qproperty-icon: none;
        background-color: transparent;
    }
    QCalendarWidget #qt_calendar_prevmonth {
        margin-left: 5px;
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMTUgMTggOSAxMiAxNSA2Ij48L3BvbHlsaW5lPjwvc3ZnPg==);
    }
    QCalendarWidget #qt_calendar_nextmonth {
        margin-right: 5px;
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iOSAxOCAxNSAxMiA5IDYiPjwvcG9seWxpbmU+PC9zdmc+);
    }
    QTimeEdit::up-button, QTimeEdit::down-button {
        border: none;
        background: transparent;
    }
"""

CARD_STYLE = """
    QFrame {
        background-color: white;
        border-radius: 18px;
        border: 1px solid #e0e0e0;
        color: black;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        background-color: white;
        color: #333333;
        border: none;
        gridline-color: #f0f0f0;
        selection-background-color: #e3f2fd;
        selection-color: #1976d2;
        font-size: 11pt;
        outline: none;
    }
    QTableWidget::item {
        padding: 8px;
    }
    QHeaderView::section {
        background-color: #ffffff;
        color: #5d6d7e;
        padding: 12px 8px;
        border: none;
        border-bottom: 1px solid #e0e0e0;
        font-weight: bold;
    }
    QScrollBar:vertical {
        border: none;
        background: #f1f1f1;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #cccccc;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""
