import json
import asyncio
import mimetypes 
from func.config import INDEX_FILE_LOCAL, INDEX_CAPTION

class CloudMixin:
    async def init_cloud_filesystem(self):
        self.log_activity("Memuat file dari Telegram...", "info")
        try:
            messages = await self.client.get_messages('me', search=INDEX_CAPTION, limit=1)
            if messages:
                self.index_msg_id = messages[0].id
                await self.client.download_media(messages[0], INDEX_FILE_LOCAL)
                with open(INDEX_FILE_LOCAL, 'r') as f: self.fs_data = json.load(f)
                self.log_activity("Data berhasil dimuat.", "success")
            else:
                await self.save_and_upload_index()
            self.render_all_views()
        except Exception as e: 
            self.log_activity(f"Error Index: {str(e)}", "error")

    async def save_and_upload_index(self):
        with open(INDEX_FILE_LOCAL, 'w') as f: json.dump(self.fs_data, f, indent=4)
        if self.index_msg_id: await self.client.delete_messages('me', self.index_msg_id)
        msg = await self.client.send_file('me', INDEX_FILE_LOCAL, caption=INDEX_CAPTION)
        self.index_msg_id = msg.id

    async def sync_with_telegram(self):
        self.log_activity("Memulai Sync...", "info")
        try:
            all_messages = []
            async for msg in self.client.iter_messages('me'):
                if msg.media:
                    all_messages.append(msg)
            
            valid_telegram_ids = [str(msg.id) for msg in all_messages]
            self.log_activity(f"Ditemukan {len(valid_telegram_ids)} file di Telegram.", "info")
            
            new_files_found = 0
            for msg in all_messages:
                if not (msg.file and msg.file.name == INDEX_FILE_LOCAL):
                    msg_id_str = str(msg.id)
                    if msg_id_str not in self.fs_data["files"]:
                        file_name = msg.file.name if msg.file.name else f"file_{msg.id}{mimetypes.guess_extension(msg.file.mime_type) or ''}"
                        self.fs_data["files"][msg_id_str] = {
                            "path": "/Root", 
                            "name": file_name, 
                            "size": msg.file.size or 0
                        }
                        new_files_found += 1
            
            removed_files_count = 0
            current_index_ids = list(self.fs_data["files"].keys())
            for msg_id in current_index_ids:
                if msg_id not in valid_telegram_ids:
                    del self.fs_data["files"][msg_id]
                    removed_files_count += 1
            
            # Simpan
            await self.save_and_upload_index()
            self.render_all_views()
            self.log_activity(f"Sync selesai! (+{new_files_found}, -{removed_files_count}).", "success")
                
        except Exception as e:
            self.log_activity(f"Error Sync: {e}", "error")