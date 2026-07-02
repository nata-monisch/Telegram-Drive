import time
from PyQt6.QtWidgets import QTableWidgetItem

class SizeTableItem(QTableWidgetItem):
    def __init__(self, size_str, size_bytes):
        super().__init__(size_str)
        self.size_bytes = size_bytes

    def __lt__(self, other):
        if isinstance(other, SizeTableItem):
            return self.size_bytes < other.size_bytes
        return super().__lt__(other)

class TransferTask:
    def __init__(self, task_id, filename, filepath, is_upload, target_path=""):
        self.task_id = task_id
        self.filename = filename
        self.filepath = filepath 
        self.is_upload = is_upload
        self.target_path = target_path 
        self.status = "Queued" 
        self.progress = 0
        self.speed = 0
        self.eta = 0
        self.size = 0
        self.last_time = time.time()
        self.last_bytes = 0