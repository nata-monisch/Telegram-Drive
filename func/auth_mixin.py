import os
import asyncio
from PyQt6.QtWidgets import QMessageBox, QLineEdit
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from func.config import SESSION_FILE

class AuthMixin:
    def on_config_submit(self):
        api_id = self.input_api_id.text().strip()
        api_hash = self.input_api_hash.text().strip()
        
        if not api_id or not api_hash:
            QMessageBox.warning(self, "Error", "API ID dan API HASH tidak boleh kosong!")
            return
            
        if not api_id.isdigit():
            QMessageBox.warning(self, "Error", "API ID harus berupa angka tanpa spasi!")
            return
            
        self.config["api_id"] = api_id
        self.config["api_hash"] = api_hash
        self.save_config()
        
        self.btn_config_submit.setEnabled(False)
        self.btn_config_submit.setText("Connecting...")
        
        asyncio.create_task(self.initialize_client_wrapper())

    async def initialize_client_wrapper(self):
        try:
            await self.initialize_client()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menghubungkan ke Telegram API:\n{e}")
        finally:
            self.btn_config_submit.setEnabled(True)
            self.btn_config_submit.setText("Configure →")

    def reset_login_state(self):
        self.stacked_widget.setCurrentIndex(0)

    def on_login_submit(self):
        text = self.input_login.text().strip()
        if not text: return
        self.btn_login_submit.setEnabled(False)
        self.btn_login_submit.setText("Loading...")
        if self.login_state == 'PHONE': asyncio.create_task(self.request_otp(text))
        elif self.login_state == 'OTP': asyncio.create_task(self.verify_otp(text))
        elif self.login_state == 'PASSWORD': asyncio.create_task(self.verify_2fa(text))

    async def request_otp(self, phone):
        try:
            self.phone_number = phone
            result = await self.client.send_code_request(phone)
            self.phone_hash = result.phone_code_hash
            
            self.login_state = 'OTP'
            self.lbl_input_top.setText("TELEGRAM CODE")
            self.lbl_input_icon.setText("🔑")
            self.input_login.clear()
            self.input_login.setPlaceholderText("1 2 3 4 5")
            self.btn_login_submit.setText("Sign In")
            self.btn_login_helper.setText("Change Phone Number")
            
        except Exception as e: 
            QMessageBox.critical(self, "Error", str(e))
            self.btn_login_submit.setText("Continue →")
        finally: 
            self.btn_login_submit.setEnabled(True)

    async def verify_otp(self, code):
        try:
            await self.client.sign_in(self.phone_number, code, phone_code_hash=self.phone_hash)
            self.on_login_success()
        except SessionPasswordNeededError:
            self.login_state = 'PASSWORD'
            self.lbl_input_top.setText("CLOUD PASSWORD")
            self.lbl_input_icon.setText("🔒")
            self.input_login.clear()
            self.input_login.setEchoMode(QLineEdit.EchoMode.Password)
            self.input_login.setPlaceholderText("••••••••")
            self.btn_login_submit.setText("Sign In")
            self.btn_login_helper.setText("Change Phone Number")
        except Exception as e: 
            QMessageBox.critical(self, "Error", str(e))
            self.btn_login_submit.setText("Sign In")
        finally: 
            self.btn_login_submit.setEnabled(True)

    async def verify_2fa(self, password):
        try:
            await self.client.sign_in(password=password)
            self.on_login_success()
        except Exception as e: 
            QMessageBox.critical(self, "Error", str(e))
            self.btn_login_submit.setText("Sign In")
        finally: 
            self.btn_login_submit.setEnabled(True)

    def on_login_success(self):
        self.stacked_widget.setCurrentIndex(2)
        asyncio.create_task(self.init_cloud_filesystem())

    def on_logout(self):
        confirm = QMessageBox.question(self, "Logout", "Logout akan menghapus sesi Anda saat ini. Lanjutkan?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            asyncio.create_task(self.perform_logout())

    async def perform_logout(self):
        try: await self.client.log_out()
        except: pass
        
        if os.path.exists(SESSION_FILE + ".session"):
            try: os.remove(SESSION_FILE + ".session")
            except: pass
        
        QMessageBox.information(self, "Logout", "Logout berhasil.")
        
        self.client = TelegramClient(SESSION_FILE, int(self.config["api_id"]), self.config["api_hash"])
        await self.client.connect()
        
        self.fs_data = {"folders": ["/Root"], "files": {}}
        self.current_path = "/Root"
        self.index_msg_id = None
        self.table.setRowCount(0)
        self.tree_model.clear()
        self.log_console.clear()
        
        self.login_state = 'PHONE'
        self.lbl_input_top.setText("PHONE NUMBER")
        self.lbl_input_icon.setText("📞")
        self.input_login.clear()
        self.input_login.setEchoMode(QLineEdit.EchoMode.Normal)
        self.input_login.setPlaceholderText("+1 234 567 8900")
        self.btn_login_submit.setText("Continue →")
        self.btn_login_helper.setText("Back to Configuration")
        
        self.stacked_widget.setCurrentIndex(1) # Kembali ke Layar Login (Bukan Layar Config)