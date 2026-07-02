import os
import io
import asyncio
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QPixmap
from telethon.tl.functions.messages import ForwardMessagesRequest
from func.models import SizeTableItem
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt, QPoint

class FileMixin:

    def setup_context_menu(self):
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        
        menu = QMenu()
        
        preview_action = None
        download_action = None
        share_action = None
        rename_action = None
        move_action = None
        delete_action = None
        back_action = None
        
        if item:
            item_type, data = item.data(Qt.ItemDataRole.UserRole)
            
            selected_items = self.table.selectedItems()
            selected_rows = set(i.row() for i in selected_items)
            is_single_selection = len(selected_rows) == 1
            
            if item_type == "file":
                filename = item.text().replace("📄 ", "").split("  (")[0]
                allowed_exts = ['txt', 'html', 'php', 'js', 'json', 'css', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                
                if ext in allowed_exts and is_single_selection:
                    preview_action = menu.addAction("👁️ Preview")
                    
                download_action = menu.addAction("📥 Download")
            
            share_action = menu.addAction("🔗 Share")
            
            if is_single_selection:
                rename_action = menu.addAction("✏️ Rename")
                
            move_action = menu.addAction("📦 Move")
            delete_action = menu.addAction("🗑️ Delete")
            menu.addSeparator() 

        if self.current_path != "/Root":
            back_action = menu.addAction("⬅️ Back")
            
        create_action = menu.addAction("📁 Create New Folder")
        upload_f_action = menu.addAction("📤 Upload File")
        upload_d_action = menu.addAction("📁 Upload Folder")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action:
            if preview_action and action == preview_action: self.on_preview()
            elif download_action and action == download_action: self.on_download()
            elif share_action and action == share_action: self.on_share()
            elif rename_action and action == rename_action: self.on_rename()
            elif move_action and action == move_action: self.on_move()
            elif delete_action and action == delete_action: self.on_delete()
            elif action == create_action: self.on_new_folder()
            elif action == upload_f_action: self.on_upload()
            elif action == upload_d_action: self.on_upload_folder()
            elif back_action and action == back_action: self.on_up_clicked()

    def render_all_views(self):
        self.update_sidebar_tree()
        self.update_main_table()

    def update_sidebar_tree(self):
        try: self.tree_model.itemChanged.disconnect(self.on_tree_item_changed)
        except: pass
        
        self.tree_model.clear()
        root_item = QStandardItem("🗄️ Drive Saya")
        root_item.setData("/Root", Qt.ItemDataRole.UserRole)
        root_item.setEditable(False)
        self.tree_model.appendRow(root_item)
        
        nodes = {"/Root": root_item}
        for path in sorted(self.fs_data["folders"]):
            if path == "/Root": continue
            parent_path = "/".join(path.split("/")[:-1])
            folder_name = path.split("/")[-1]
            
            item = QStandardItem(f"📁 {folder_name}")
            item.setData(path, Qt.ItemDataRole.UserRole)
            if parent_path in nodes:
                nodes[parent_path].appendRow(item)
                nodes[path] = item
                
        self.tree_view.expand(self.tree_model.index(0, 0))
        self.tree_model.itemChanged.connect(self.on_tree_item_changed)

    def on_tree_item_changed(self, item):
        self.tree_model.blockSignals(True)
        
        old_path = item.data(Qt.ItemDataRole.UserRole)
        if not old_path or old_path == "/Root":
            item.setText("🗄️ Drive Saya")
            self.tree_model.blockSignals(False)
            return
            
        new_text = item.text().replace("📁 ", "").strip()
        old_name = old_path.split("/")[-1]
        
        if not new_text or new_text == old_name:
            item.setText(f"📁 {old_name}")
            self.tree_model.blockSignals(False)
            return
            
        parent_path = "/".join(old_path.split("/")[:-1])
        new_path = f"{parent_path}/{new_text}"
        
        if new_path in self.fs_data["folders"]:
            item.setText(f"📁 {old_name}")
            self.tree_model.blockSignals(False)
            QMessageBox.warning(self, "Error", "Nama folder sudah digunakan!")
            return
            
        new_folders = [new_path if f == old_path else f.replace(old_path, new_path, 1) if f.startswith(old_path + "/") else f for f in self.fs_data["folders"]]
        self.fs_data["folders"] = new_folders
        
        for msg_id_str, info in self.fs_data["files"].items():
            if info["path"] == old_path: info["path"] = new_path
            elif info["path"].startswith(old_path + "/"): info["path"] = info["path"].replace(old_path, new_path, 1)
        
        if self.current_path == old_path or self.current_path.startswith(old_path + "/"):
            self.current_path = self.current_path.replace(old_path, new_path, 1)
            
        item.setText(f"📁 {new_text}")
        item.setData(new_path, Qt.ItemDataRole.UserRole)
        
        self.update_child_paths(item, old_path, new_path)
        
        self.tree_model.blockSignals(False)
        self.update_main_table()
        
        import asyncio
        asyncio.create_task(self.save_and_upload_index())
        self.log_activity(f"Berhasil rename folder ke '{new_text}'", "success")

    def update_child_paths(self, parent_item, old_base_path, new_base_path):
        for row in range(parent_item.rowCount()):
            child = parent_item.child(row)
            child_old_path = child.data(Qt.ItemDataRole.UserRole)
            if child_old_path and child_old_path.startswith(old_base_path + "/"):
                child_new_path = child_old_path.replace(old_base_path, new_base_path, 1)
                child.setData(child_new_path, Qt.ItemDataRole.UserRole)
                self.update_child_paths(child, old_base_path, new_base_path)
                
    def update_main_table(self, search_query=""):
        self.table.setSortingEnabled(False) 
        self.table.setRowCount(0)
        
        self.btn_back.setEnabled(self.current_path != "/Root")
        
        if search_query:
            self.lbl_title.setText(f"Search Results for: '{search_query}'")
        else:
            self.lbl_title.setText(f"My Files {self.current_path.replace('/Root', '')}")
            
        row = 0
        
        for folder_path in self.fs_data["folders"]:
            folder_name = folder_path.split('/')[-1]
            if folder_path == "/Root": continue
            
            is_match = False
            if search_query and search_query in folder_name.lower():
                is_match = True
            elif not search_query and folder_path.startswith(self.current_path + "/") and folder_path.count("/") == self.current_path.count("/") + 1:
                is_match = True
                
            if is_match:
                self.table.insertRow(row)
                display_name = f"📁 {folder_name}"
                if search_query: display_name += f"  ({folder_path})" 
                
                item = QTableWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, ("folder", folder_path))
                self.table.setItem(row, 0, item)
                self.table.setItem(row, 1, SizeTableItem("-", 0)) 
                self.table.setItem(row, 2, QTableWidgetItem("Folder"))
                row += 1
                
        for msg_id_str, info in self.fs_data["files"].items():
            is_match = False
            if search_query and search_query in info['name'].lower():
                is_match = True
            elif not search_query and info["path"] == self.current_path:
                is_match = True
                
            if is_match:
                self.table.insertRow(row)
                display_name = f"📄 {info['name']}"
                if search_query: display_name += f"  ({info['path']})"
                
                item = QTableWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, ("file", int(msg_id_str)))
                self.table.setItem(row, 0, item)
                
                size_kb = info['size'] / 1024
                size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{(size_kb/1024):.1f} MB"
                
                self.table.setItem(row, 1, SizeTableItem(size_str, info['size'])) 
                self.table.setItem(row, 2, QTableWidgetItem("File"))
                row += 1
                
        self.table.setSortingEnabled(True) 
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)

    def on_search_changed(self, text):
        self.update_main_table(search_query=text.strip().lower())

    def on_tree_clicked(self, index):
        path = self.tree_model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
        if path:
            self.current_path = path
            self.search_bar.clear()
            self.update_main_table()
            
    def on_up_clicked(self):
        if self.current_path != "/Root":
            self.current_path = "/".join(self.current_path.split("/")[:-1])
            if not self.current_path: self.current_path = "/Root"
            self.search_bar.clear()
            self.update_main_table()

    def on_table_double_clicked(self, row, column):
        item_type, data = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if item_type == "folder":
            self.current_path = data
            self.search_bar.clear() 
            self.update_main_table()
        elif item_type == "file":
            self.on_preview() 

    def on_new_folder(self):
        text, ok = QInputDialog.getText(self, 'New Folder', 'Nama Folder:')
        if ok and text:
            new_path = f"{self.current_path}/{text}"
            if new_path not in self.fs_data["folders"]:
                self.fs_data["folders"].append(new_path)
                self.render_all_views()
                asyncio.create_task(self.save_and_upload_index())

    def on_rename(self):
        selected = self.table.selectedItems()
        if not selected: return QMessageBox.warning(self, "Pilih Item", "Pilih item untuk direname.")
        
        item_type, data = self.table.item(selected[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if item_type == "file":
            msg_id = str(data)
            old_name = self.fs_data["files"][msg_id]["name"]
            new_name, ok = QInputDialog.getText(self, 'Rename File', 'Nama baru:', text=old_name)
            if ok and new_name and new_name != old_name:
                self.fs_data["files"][msg_id]["name"] = new_name
                self.render_all_views(); asyncio.create_task(self.save_and_upload_index())
                self.log_activity(f"Berhasil ganti nama ke '{new_name}'", "success")
                
        elif item_type == "folder":
            old_path = data
            old_name = old_path.split("/")[-1]
            new_name, ok = QInputDialog.getText(self, 'Rename Folder', 'Nama baru:', text=old_name)
            if ok and new_name and new_name != old_name:
                parent_path = "/".join(old_path.split("/")[:-1])
                new_path = f"{parent_path}/{new_name}"
                
                new_folders = [new_path if f == old_path else f.replace(old_path, new_path, 1) if f.startswith(old_path + "/") else f for f in self.fs_data["folders"]]
                self.fs_data["folders"] = new_folders
                
                for msg_id_str, info in self.fs_data["files"].items():
                    if info["path"] == old_path: info["path"] = new_path
                    elif info["path"].startswith(old_path + "/"): info["path"] = info["path"].replace(old_path, new_path, 1)
                
                self.render_all_views(); asyncio.create_task(self.save_and_upload_index())
                self.log_activity(f"Berhasil ganti nama folder ke '{new_name}'", "success")

    def on_move(self):
        selected = self.table.selectedItems()
        if not selected: return QMessageBox.warning(self, "Pilih Item", "Pilih item yang ingin dipindah.")
        
        rows = set(i.row() for i in selected)
        folders = self.fs_data["folders"]
        dest, ok = QInputDialog.getItem(self, "Move To...", "Pilih folder tujuan:", folders, 0, False)
        
        if ok and dest:
            moved_count = 0
            for r in rows:
                item_type, data = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
                if item_type == "file":
                    self.fs_data["files"][str(data)]["path"] = dest
                    moved_count += 1
                elif item_type == "folder":
                    if dest.startswith(data): 
                        QMessageBox.warning(self, "Error", f"Tidak bisa memindahkan {data} ke dalam dirinya sendiri!")
                        continue
                    new_path = f"{dest}/{data.split('/')[-1]}"
                    
                    new_folders = [new_path if f == data else f.replace(data, new_path, 1) if f.startswith(data + "/") else f for f in self.fs_data["folders"]]
                    self.fs_data["folders"] = new_folders
                    
                    for msg_id_str, info in self.fs_data["files"].items():
                        if info["path"] == data: info["path"] = new_path
                        elif info["path"].startswith(data + "/"): info["path"] = info["path"].replace(data, new_path, 1)
                    moved_count += 1
                    
            if moved_count > 0:
                self.render_all_views()
                asyncio.create_task(self.save_and_upload_index())
                self.log_activity(f"{moved_count} item dipindahkan ke '{dest}'", "success")

    def on_delete(self):
        selected_items = self.table.selectedItems()
        if not selected_items: return
        
        rows = set(item.row() for item in selected_items)
        
        confirm = QMessageBox.question(
            self, 
            'Hapus Item', 
            f'Yakin ingin menghapus {len(rows)} item terpilih?', 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            items_to_delete = []
            for r in rows:
                item_type, data = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
                items_to_delete.append((item_type, data))
                
            asyncio.create_task(self.delete_multiple_items(items_to_delete))

    async def delete_multiple_items(self, items_to_delete):
        self.log_activity(f"Sedang menghapus {len(items_to_delete)} item...", "info")
        msg_ids_to_delete = []
        
        for item_type, data in items_to_delete:
            if item_type == "file":
                msg_ids_to_delete.append(int(data))
                if str(data) in self.fs_data["files"]:
                    del self.fs_data["files"][str(data)]
                    
            elif item_type == "folder":
                folder_path = data
                if folder_path in self.fs_data["folders"]:
                    self.fs_data["folders"].remove(folder_path)
                
                sub_folders = [f for f in self.fs_data["folders"] if f.startswith(folder_path + "/")]
                for f in sub_folders:
                    self.fs_data["folders"].remove(f)
                    
                files_to_remove = []
                for msg_id_str, info in self.fs_data["files"].items():
                    if info["path"] == folder_path or info["path"].startswith(folder_path + "/"):
                        files_to_remove.append(msg_id_str)
                        msg_ids_to_delete.append(int(msg_id_str))
                
                for f_id in files_to_remove:
                    del self.fs_data["files"][f_id]
        
        if msg_ids_to_delete:
            try:
                await self.client.delete_messages('me', msg_ids_to_delete)
            except Exception as e:
                self.log_activity(f"Gagal menghapus pesan di Telegram: {e}", "error")
                
        await self.save_and_upload_index()
        self.render_all_views()
        self.log_activity(f"Berhasil menghapus item terpilih.", "success")

    def on_preview(self):
        items = self.table.selectedItems()
        if not items: return
        item_type, data = self.table.item(items[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if item_type == "folder": return QMessageBox.information(self, "Info", "Hanya file yang dapat di-preview.")
        
        filename = self.table.item(items[0].row(), 0).text().replace("📄 ", "").split("  (")[0]
        allowed_exts = ['txt', 'html', 'php', 'js', 'json', 'css', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if ext not in allowed_exts:
            QMessageBox.warning(self, "Preview Ditolak", f"File '{filename}' tidak didukung untuk preview langsung.\nSilakan gunakan tombol Download.")
            return
            
        asyncio.create_task(self.preview_media(data, filename))

    async def preview_media(self, msg_id, filename):
        self.log_activity(f"Memuat preview untuk {filename} ke memori...", "info")
        try:
            msg = await self.client.get_messages('me', ids=msg_id)
            mem_file = io.BytesIO()
            await self.client.download_media(msg, file=mem_file)
            mem_file.seek(0)
            
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle(f"Preview - {filename}")
            preview_dialog.resize(650, 650)
            layout = QVBoxLayout(preview_dialog)
            
            ext = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
                pixmap = QPixmap()
                pixmap.loadFromData(mem_file.read())
                lbl = QLabel()
                lbl.setPixmap(pixmap.scaled(630, 630, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(lbl)
                
            elif ext in ['txt', 'html', 'php', 'js', 'json', 'css']:
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                text_edit.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
                text_edit.setText(mem_file.read().decode('utf-8', errors='ignore'))
                layout.addWidget(text_edit)
                
            preview_dialog.exec()
            self.log_activity("Preview selesai ditutup.", "success")
        except Exception as e:
            self.log_activity(f"Gagal memuat preview: {e}", "error")
            QMessageBox.critical(self, "Error Preview", f"Gagal memuat file:\n{e}")

    def on_share(self):
        items = self.table.selectedItems()
        if not items: return
        
        rows = set(item.row() for item in items)
        
        msg_ids_to_share = set() 
        
        for r in rows:
            item_type, data = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
            
            if item_type == "file":
                msg_ids_to_share.add(int(data))
                
            elif item_type == "folder":
                folder_path = data
                for msg_id_str, info in self.fs_data["files"].items():
                    if info["path"] == folder_path or info["path"].startswith(folder_path + "/"):
                        msg_ids_to_share.add(int(msg_id_str))
                        
        if not msg_ids_to_share:
            return QMessageBox.warning(self, "Oops", "Tidak ada file yang ditemukan untuk dibagikan dalam folder tersebut.")
            
        msg_ids_list = list(msg_ids_to_share)
            
        target, ok = QInputDialog.getText(self, 'Share File', f'Kirim {len(msg_ids_list)} file ke Username/No HP (@username):')
        if ok and target:
            asyncio.create_task(self.forward_item(msg_ids_list, target))

    async def forward_item(self, msg_ids, target):
        self.log_activity(f"Sedang meneruskan {len(msg_ids)} file ke {target}...", "info")
        try:
            await self.client(ForwardMessagesRequest(from_peer='me', id=msg_ids, to_peer=target))
            self.log_activity(f"{len(msg_ids)} File berhasil diteruskan ke {target}", "success")
            QMessageBox.information(self, "Success", f"Berhasil membagikan {len(msg_ids)} file ke {target}!")
        except Exception as e:
            self.log_activity(f"Gagal membagikan ke {target}: {e}", "error")
            QMessageBox.critical(self, "Error", f"Gagal membagikan:\n{e}")

    def on_sync_clicked(self):
        asyncio.create_task(self.sync_with_telegram())