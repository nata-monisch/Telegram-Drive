# --- KONFIGURASI APLIKASI ---
SESSION_FILE = 'tg_drive'
INDEX_FILE_LOCAL = 'tg_drive_index.json'
INDEX_CAPTION = '#TGDRIVE_INDEX'
CONFIG_FILE = 'tg_drive_config.json'

# ================= TEMA QSS =================
LOGIN_UI_QSS = """
*:focus { outline: none; } 
QTreeView QLineEdit { background-color: #151821; color: #ffffff; border: 1px solid #664dd1; border-radius: 4px; padding: 2px 5px; }
QWidget#login_bg { background-color: #080022; }
QWidget#login_card { background-color: #1f2327; border-radius: 16px; }
QLabel#login_icon { background-color: #080022; color: white; border-radius: 12px; font-size: 22px; }
QLabel#login_title { color: #ffffff; font-size: 20px; font-weight: bold; }
QLabel#login_subtitle { color: #7a8299; font-size: 13px; }
QLabel#login_label { color: #7a8299; font-size: 11px; font-weight: bold; letter-spacing: 1px;}
QWidget#input_container { background-color: #151821; border-radius: 8px; border: 1px solid #282d3e; }
QLineEdit#login_input { background: transparent; border: none; color: #fff; font-size: 14px; padding: 0px; }
QPushButton#btn_login_submit { background-color: #664dd1; color: #fff; font-weight: bold; border-radius: 8px; padding: 12px; font-size: 14px; border: none; }
QPushButton#btn_login_submit:hover { background-color: #553bb8; }
QPushButton#btn_login_submit:disabled { background-color: #888888; color: #555555; }
QPushButton#btn_login_helper { background: transparent; border: none; color: #7a8299; font-size: 12px; }
QPushButton#btn_login_helper:hover { color: #664dd1; }
QLabel a { color: #7a8299; text-decoration: none; }
QLabel a:hover { color: #664dd1; }
"""

DARK_THEME_QSS = LOGIN_UI_QSS + """
QMainWindow { background-color: #1c1d2b; }
QWidget { font-family: 'Segoe UI', Helvetica, sans-serif; color: #a4a6b3; }
QWidget#sidebar { background-color: #1c1d2b; border-right: 1px solid #2a2c3f; }
QPushButton { background-color: #27293d; color: #ffffff; border: 1px solid #3d3f54; border-radius: 5px; padding: 6px 12px; }
QPushButton:hover { background-color: #32354e; }
QPushButton#btn_create { padding: 12px; font-weight: bold; border-radius: 8px; }
QTreeView { background-color: #1c1d2b; border: none; font-size: 13px; color: #d1d2df; }
QTreeView::item { padding: 6px; border-radius: 5px; margin-bottom: 2px; }
QTreeView::item:hover { background-color: #27293d; }
QTreeView::item:selected { background-color: #0056b3; color: white; }
QLabel#main_title { color: #ffffff; font-size: 18px; font-weight: bold; }
QLineEdit, QComboBox { background-color: #1c1d2b; border: 1px solid #2a2c3f; border-radius: 10px; padding: 6px 15px; color: white; }
QLineEdit:focus { border: 1px solid #0056b3; }
QTableWidget { background-color: #27293d; border: 1px solid #2a2c3f; border-radius: 10px; gridline-color: transparent; selection-background-color: #32354e; color: #d1d2df; }
QHeaderView::section { background-color: #27293d; color: #a4a6b3; padding: 12px; border: none; border-bottom: 1px solid #2a2c3f; font-weight: bold; text-align: left; }
QTableWidget::item { border-bottom: 1px solid #2a2c3f; padding: 8px; }
QTextEdit#log_console { background-color: #161723; border: 1px solid #2a2c3f; border-radius: 8px; padding: 10px; font-family: Consolas, monospace; }
"""