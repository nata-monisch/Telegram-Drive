import sys
import os
import json
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QTextCursor, QIcon  # <--- FIX: Tambahkan QIcon di sini

from telethon import TelegramClient

from func.config import SESSION_FILE, CONFIG_FILE, DARK_THEME_QSS
from func.ui_mixin import UIMixin
from func.auth_mixin import AuthMixin
from func.cloud_mixin import CloudMixin
from func.file_mixin import FileMixin
from func.transfer_mixin import TransferMixin

class TelegramDriveApp(QMainWindow, UIMixin, AuthMixin, CloudMixin, FileMixin, TransferMixin):
    def __init__(self): 
        super().__init__()
        self.client = None 
        self.phone_hash = None
        self.phone_number = None
        
        self.fs_data = {"folders": ["/Root"], "files": {}}
        self.current_path = "/Root"
        self.index_msg_id = None
        
        self.config = {"theme": "Dark", "api_id": "", "api_hash": ""}
        self.load_config()
        
        self.transfer_queue = asyncio.Queue()
        self.active_transfers = {} 
        self.task_counter = 0
        self.is_worker_running = False
        
        self.setWindowTitle("Telegram Drive - Natamonisch")

        pixmap = self.load_logo_pixmap()
        if not pixmap.isNull():
            self.setWindowIcon(QIcon(pixmap))
            
        self.resize(1200, 750)
        self.setAcceptDrops(True)
        self.setStyleSheet(DARK_THEME_QSS) 
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.init_config_ui()
        self.init_login_ui()
        self.init_file_manager_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config.update(json.load(f))

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    async def initialize_client(self):
        self.client = TelegramClient(SESSION_FILE, int(self.config["api_id"]), self.config["api_hash"])
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            self.stacked_widget.setCurrentIndex(1) 
        else:
            self.stacked_widget.setCurrentIndex(2) 
            await self.init_cloud_filesystem()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and self.stacked_widget.currentIndex() == 2: event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        for path in paths: 
            if os.path.isfile(path):
                self.add_transfer_task(os.path.basename(path), path, is_upload=True)
            elif os.path.isdir(path):
                self.queue_folder_upload(path)

    def log_activity(self, msg, msg_type="info"):
        color = "#a4a6b3"
        if msg_type == "success": color = "#00ff00"
        elif msg_type == "error": color = "#ff4444"
        
        cursor = self.log_console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.insertHtml(f'<span style="color: {color};">{msg}</span><br>')
        
        self.log_console.verticalScrollBar().setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    async def start_app():
        global w; w = TelegramDriveApp(); w.showMaximized()
        
        if not w.config.get("api_id") or not w.config.get("api_hash"):
            w.stacked_widget.setCurrentIndex(0) 
        else:
            await w.initialize_client() 

    loop.create_task(start_app()); loop.run_forever()