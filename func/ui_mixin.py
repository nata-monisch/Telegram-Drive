import urllib.request
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QSplitter, QTreeView, QTableWidget, QHeaderView, QAbstractItemView, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QPixmap

class UIMixin:
    def load_logo_pixmap(self):
        if not hasattr(self, '_logo_pixmap'):
            self._logo_pixmap = QPixmap()
            try:
                url = "https://ntmn.eu.org/assets/img/logo.png"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req, timeout=5).read()
                self._logo_pixmap.loadFromData(data)
            except Exception as e:
                print(f"Gagal memuat logo dari web: {e}")
        return self._logo_pixmap

    def init_config_ui(self):
        w = QWidget()
        w.setObjectName("login_bg")
        bg_layout = QVBoxLayout(w)
        bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("login_card")
        card.setFixedSize(380, 480)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 30)

        icon_layout = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setObjectName("login_icon")
        lbl_icon.setFixedSize(52, 52)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = self.load_logo_pixmap()
        if not pixmap.isNull():
            lbl_icon.setPixmap(pixmap.scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_icon.setText("⚙️")
            
        icon_layout.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(icon_layout)
        card_layout.addSpacing(10)

        lbl_title = QLabel("Configuration")
        lbl_title.setObjectName("login_title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Set your Telegram API Credentials")
        lbl_subtitle.setObjectName("login_subtitle")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_subtitle)
        card_layout.addSpacing(30)

        lbl_api_id = QLabel("API ID")
        lbl_api_id.setObjectName("login_label")
        card_layout.addWidget(lbl_api_id)

        cont_api_id = QWidget()
        cont_api_id.setObjectName("input_container")
        cont_api_id.setFixedHeight(45)
        lay_api_id = QHBoxLayout(cont_api_id)
        lay_api_id.setContentsMargins(15, 0, 15, 0)
        
        self.input_api_id = QLineEdit()
        self.input_api_id.setObjectName("login_input")
        self.input_api_id.setPlaceholderText("e.g. 12345678")
        lay_api_id.addWidget(self.input_api_id)
        card_layout.addWidget(cont_api_id)
        card_layout.addSpacing(15)

        lbl_api_hash = QLabel("API HASH")
        lbl_api_hash.setObjectName("login_label")
        card_layout.addWidget(lbl_api_hash)

        cont_api_hash = QWidget()
        cont_api_hash.setObjectName("input_container")
        cont_api_hash.setFixedHeight(45)
        lay_api_hash = QHBoxLayout(cont_api_hash)
        lay_api_hash.setContentsMargins(15, 0, 15, 0)
        
        self.input_api_hash = QLineEdit()
        self.input_api_hash.setObjectName("login_input")
        self.input_api_hash.setPlaceholderText("e.g. 0123456789abcdef0123456789abcdef")
        lay_api_hash.addWidget(self.input_api_hash)
        card_layout.addWidget(cont_api_hash)
        card_layout.addSpacing(25)

        self.btn_config_submit = QPushButton("Configure →")
        self.btn_config_submit.setObjectName("btn_login_submit")
        self.btn_config_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_config_submit.clicked.connect(self.on_config_submit)
        card_layout.addWidget(self.btn_config_submit)
        card_layout.addSpacing(15)

        link_layout = QHBoxLayout()
        lbl_link = QLabel("<a href='https://github.com/nata-monisch/Telegram-Drive#installation'>How do I get my API credentials?</a>")
        lbl_link.setOpenExternalLinks(True) 
        lbl_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_layout.addWidget(lbl_link)
        card_layout.addLayout(link_layout)

        card_layout.addStretch()
        bg_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(w)

    def init_login_ui(self):
        w = QWidget()
        w.setObjectName("login_bg")
        bg_layout = QVBoxLayout(w)
        bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("login_card")
        card.setFixedSize(380, 420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 30)

        icon_layout = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setObjectName("login_icon")
        lbl_icon.setFixedSize(52, 52)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = self.load_logo_pixmap()
        if not pixmap.isNull():
            lbl_icon.setPixmap(pixmap.scaled(38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_icon.setText("🛡️")
            
        icon_layout.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(icon_layout)
        card_layout.addSpacing(10)

        lbl_title = QLabel("Telegram Drive")
        lbl_title.setObjectName("login_title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Self-Hosted Secure Storage")
        lbl_subtitle.setObjectName("login_subtitle")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_subtitle)
        card_layout.addSpacing(30)

        self.lbl_input_top = QLabel("PHONE NUMBER")
        self.lbl_input_top.setObjectName("login_label")
        card_layout.addWidget(self.lbl_input_top)

        self.input_container = QWidget()
        self.input_container.setObjectName("input_container")
        self.input_container.setFixedHeight(45)
        inp_layout = QHBoxLayout(self.input_container)
        inp_layout.setContentsMargins(15, 0, 15, 0)
        inp_layout.setSpacing(10)

        self.lbl_input_icon = QLabel("📞")
        self.lbl_input_icon.setStyleSheet("color: #7a8299; font-size: 16px; background: transparent;")
        inp_layout.addWidget(self.lbl_input_icon)

        self.input_login = QLineEdit()
        self.input_login.setObjectName("login_input")
        self.input_login.setPlaceholderText("+1 234 567 8900")
        inp_layout.addWidget(self.input_login)
        card_layout.addWidget(self.input_container)
        card_layout.addSpacing(20)

        self.btn_login_submit = QPushButton("Continue →")
        self.btn_login_submit.setObjectName("btn_login_submit")
        self.btn_login_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login_submit.clicked.connect(self.on_login_submit)
        card_layout.addWidget(self.btn_login_submit)
        card_layout.addSpacing(10)

        self.btn_login_helper = QPushButton("Back to Configuration")
        self.btn_login_helper.setObjectName("btn_login_helper")
        self.btn_login_helper.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login_helper.clicked.connect(self.reset_login_state)
        card_layout.addWidget(self.btn_login_helper)

        card_layout.addStretch()
        bg_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        self.login_state = 'PHONE'
        self.stacked_widget.addWidget(w)

    def init_file_manager_ui(self):
        fm_widget = QWidget()
        main_layout = QVBoxLayout(fm_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(200) 
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        self.btn_new_folder = QPushButton("+ Create New Folder")
        self.btn_new_folder.setObjectName("btn_create")
        self.btn_new_folder.clicked.connect(self.on_new_folder)
        sidebar_layout.addWidget(self.btn_new_folder)

        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        sidebar_layout.addWidget(self.tree_view)
        
        self.btn_logout = QPushButton("🚪 Logout")
        self.btn_logout.clicked.connect(self.on_logout)
        self.btn_logout.setStyleSheet("color: #ff4444;")
        sidebar_layout.addWidget(self.btn_logout)
        
        main_splitter.addWidget(sidebar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("My Files")
        self.lbl_title.setObjectName("main_title")
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search_bar")
        self.search_bar.setPlaceholderText("🔍 Search...")
        self.search_bar.setFixedWidth(250)
        self.search_bar.textChanged.connect(self.on_search_changed) 
        
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        content_layout.addLayout(header_layout)

        action_layout = QHBoxLayout()
        self.btn_back = QPushButton("⬅️ Back")
        self.btn_upload = QPushButton("📤 Upload File")
        self.btn_upload_folder = QPushButton("📁 Upload Folder") 
        self.btn_download = QPushButton("📥 Download")
        self.btn_preview = QPushButton("👁️ Preview") 
        self.btn_share = QPushButton("🔗 Share") 
        self.btn_rename = QPushButton("✏️ Rename")
        self.btn_move = QPushButton("📦 Move")
        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_sync = QPushButton("🔄 Sync")
        
        for btn in [self.btn_back, self.btn_upload, self.btn_upload_folder, self.btn_download, self.btn_preview, self.btn_share, self.btn_rename, self.btn_move, self.btn_delete]: action_layout.addWidget(btn)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_sync)
        content_layout.addLayout(action_layout)

        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Type"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True) 
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        content_splitter.addWidget(self.table)
        
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        self.log_console = QTextEdit()
        self.log_console.setObjectName("log_console")
        self.log_console.setReadOnly(True)
        bottom_layout.addWidget(self.log_console, stretch=1)
        
        self.transfer_table = QTableWidget(0, 4)
        self.transfer_table.setHorizontalHeaderLabels(["File", "Progress", "Speed", "ETA"])
        self.transfer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.transfer_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.transfer_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.transfer_table.verticalHeader().setVisible(False)
        bottom_layout.addWidget(self.transfer_table, stretch=2)
        
        content_splitter.addWidget(bottom_panel)
        content_splitter.setSizes([450, 200])
        content_layout.addWidget(content_splitter)
        
        main_splitter.addWidget(content_widget)
        main_splitter.setSizes([240, 960]) 
        
        main_layout.addWidget(main_splitter)
        self.stacked_widget.addWidget(fm_widget)

        self.btn_back.clicked.connect(self.on_up_clicked)
        self.btn_upload.clicked.connect(self.on_upload)
        self.btn_upload_folder.clicked.connect(self.on_upload_folder) 
        self.btn_download.clicked.connect(self.on_download)
        self.btn_rename.clicked.connect(self.on_rename)
        self.btn_move.clicked.connect(self.on_move)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_preview.clicked.connect(self.on_preview) 
        self.btn_share.clicked.connect(self.on_share)
        self.btn_sync.clicked.connect(self.on_sync_clicked)
        self.setup_context_menu()