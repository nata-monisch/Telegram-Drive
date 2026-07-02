import os
import time
import asyncio
from PyQt6.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt6.QtCore import Qt
from func.models import TransferTask

class TransferMixin:
    def on_upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder untuk Diupload")
        if folder_path:
            self.queue_folder_upload(folder_path)

    def queue_folder_upload(self, folder_path):
        base_folder_name = os.path.basename(folder_path)
        base_virtual_path = f"{self.current_path}/{base_folder_name}"

        if base_virtual_path not in self.fs_data["folders"]:
            self.fs_data["folders"].append(base_virtual_path)

        for root, dirs, files in os.walk(folder_path):
            rel_path = os.path.relpath(root, folder_path)
            if rel_path == ".": current_virtual_path = base_virtual_path
            else:
                virtual_rel = rel_path.replace(os.sep, "/")
                current_virtual_path = f"{base_virtual_path}/{virtual_rel}"

            for d in dirs:
                sub_virtual_path = f"{current_virtual_path}/{d}"
                if sub_virtual_path not in self.fs_data["folders"]:
                    self.fs_data["folders"].append(sub_virtual_path)

            for f in files:
                local_file_path = os.path.join(root, f)
                self.add_transfer_task(f, local_file_path, is_upload=True, custom_target_path=current_virtual_path)

        self.render_all_views()
        asyncio.create_task(self.save_and_upload_index())

    def add_transfer_task(self, filename, filepath, is_upload, custom_target_path=None):
        self.task_counter += 1
        target = custom_target_path if custom_target_path else self.current_path
        task = TransferTask(self.task_counter, filename, filepath, is_upload, target)
        self.active_transfers[self.task_counter] = task
        self.transfer_queue.put_nowait(task)
        self.render_transfer_table()
        
        if not self.is_worker_running:
            self.is_worker_running = True 
            asyncio.create_task(self.process_transfer_queue())

    def render_transfer_table(self):
        self.transfer_table.setRowCount(0)
        
        for task_id, task in reversed(list(self.active_transfers.items())):
            row = self.transfer_table.rowCount()
            self.transfer_table.insertRow(row)
            
            icon = "📤" if task.is_upload else "📥"
            self.transfer_table.setItem(row, 0, QTableWidgetItem(f"{icon} {task.filename}"))
            
            if task.status in ["Done", "Error"]:
                self.transfer_table.setItem(row, 1, QTableWidgetItem(task.status))
                self.transfer_table.setItem(row, 2, QTableWidgetItem("-"))
                self.transfer_table.setItem(row, 3, QTableWidgetItem("-"))
            else:
                self.transfer_table.setItem(row, 1, QTableWidgetItem(f"{task.progress}%"))
                self.transfer_table.setItem(row, 2, QTableWidgetItem(f"{task.speed:.2f} MB/s"))
                eta_str = f"{int(task.eta)}s" if task.eta > 0 else "-"
                if task.eta > 60: eta_str = f"{int(task.eta//60)}m {int(task.eta%60)}s"
                self.transfer_table.setItem(row, 3, QTableWidgetItem(eta_str))

    def on_upload(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Pilih File")
        for p in filepaths: self.add_transfer_task(os.path.basename(p), p, is_upload=True)

    def on_download(self):
        items = self.table.selectedItems()
        if not items: 
            return
        
        rows = set(i.row() for i in items)
        files_to_download = []
        for r in rows:
            item_type, data = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
            if item_type == "file":
                raw_text = self.table.item(r, 0).text()
                clean_name = raw_text.replace("📄 ", "").replace("塘 ", "").split("  (")[0]
                files_to_download.append((data, clean_name))
        
        if not files_to_download:
            return

        if len(files_to_download) == 1:
            msg_id, name = files_to_download[0]
            default_path = os.path.join(os.path.expanduser("~/Downloads"), name)
            
            save_path, _ = QFileDialog.getSaveFileName(self, "Simpan File", default_path)
            if save_path:
                self.add_transfer_task(name, (msg_id, save_path), is_upload=False)
        
        else:
            default_dir = os.path.expanduser("~/Downloads")
            save_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder Tujuan", default_dir)
            if save_dir:
                for msg_id, name in files_to_download:
                    full_save_path = os.path.join(save_dir, name)
                    self.add_transfer_task(name, (msg_id, full_save_path), is_upload=False)

    async def process_transfer_queue(self):
        loop = asyncio.get_event_loop()
        while not self.transfer_queue.empty():
            task = await self.transfer_queue.get()
            def progress_cb(current, total):
                now = time.time()
                time_diff = now - task.last_time
                if time_diff >= 0.5: 
                    bytes_diff = current - task.last_bytes
                    speed_bps = bytes_diff / time_diff
                    task.speed = speed_bps / (1024 * 1024) 
                    if task.speed > 0: task.eta = (total - current) / speed_bps
                    task.progress = int((current / total) * 100)
                    task.last_time = now
                    task.last_bytes = current
                    loop.call_soon_threadsafe(self.render_transfer_table)
            try:
                task.status = "Transferring"
                if task.is_upload:
                    size = os.path.getsize(task.filepath)
                    if size == 0: raise Exception("File kosong.")
                    msg = await self.client.send_file('me', task.filepath, force_document=True, progress_callback=progress_cb)
                    self.fs_data["files"][str(msg.id)] = {"path": task.target_path, "name": task.filename, "size": size}
                else:
                    msg_id, save_path = task.filepath
                    msg = await self.client.get_messages('me', ids=msg_id)
                    await self.client.download_media(msg, file=save_path, progress_callback=progress_cb)
                task.status = "Done"
                task.progress = 100
                task.speed = 0
            except Exception as e:
                task.status = "Error"
                self.log_activity(f"[{task.status}] {task.filename}: {e}", "error")
                
            self.render_transfer_table()
            self.render_all_views() 
            self.transfer_queue.task_done()
            await asyncio.sleep(0.5)
            
        await self.save_and_upload_index()
        self.is_worker_running = False