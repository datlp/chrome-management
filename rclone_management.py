import os
import json
import subprocess
import time
import csv
import threading
import urllib.request
import urllib.error
import base64
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CONFIG_DIR = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "dsoft", "rclone-management")
CONFIG_FILE = os.path.join(CONFIG_DIR, "rclone_management_config.json")
RCLONE_CONF_FILE = os.path.join(CONFIG_DIR, "rclone.conf")
__version__ = "1.0.0"

class RcloneManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rclone & Tailscale Disk Manager")
        self.root.geometry("900x800")
        self.root.minsize(700, 600)
        
        # Color palette (Modern Dark Mode consistent with windows_management.py)
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#00adb5"
        self.accent_hover = "#00fff5"
        self.text_color = "#eeeeee"
        self.text_muted = "#aaaaaa"
        self.border_color = "#393e46"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_color, relief="flat")
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background=self.card_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color, font=("Segoe UI", 16, "bold"))
        self.style.configure("Sub.TLabel", background=self.card_color, foreground=self.text_muted, font=("Segoe UI", 9, "italic"))
        
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff", borderwidth=0, font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", self.accent_hover), ("pressed", self.accent_color)])
        
        self.style.configure("Normal.TButton", background=self.border_color, foreground=self.text_color, borderwidth=0, font=("Segoe UI", 10))
        self.style.map("Normal.TButton", background=[("active", "#4f555e")])

        self.style.configure("Vertical.TScrollbar", background=self.border_color, borderwidth=0, arrowsize=12)
        
        # Notebook styles
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.card_color, foreground=self.text_muted, borderwidth=1, lightcolor=self.border_color, bordercolor=self.border_color, font=("Segoe UI", 10, "bold"), padding=(15, 6))
        self.style.map("TNotebook.Tab", background=[("selected", self.bg_color)], foreground=[("selected", self.accent_color)])
        
        self.style.configure("Treeview", background=self.card_color, foreground=self.text_color, fieldbackground=self.card_color, borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background=self.border_color, foreground=self.text_color, borderwidth=1, font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", self.accent_color)], foreground=[("selected", "#ffffff")])

        # State Variables
        self.remotes = []
        self.active_mounts = {}  # disk_letter -> subprocess.Popen
        self.start_disk_letter_var = tk.StringVar(value="K")
        self.tailscale_api_key_var = tk.StringVar()
        self.tailscale_tailnet_var = tk.StringVar(value="-")
        self.start_with_windows_var = tk.BooleanVar(value=False)
        self.auto_mount_on_startup_var = tk.BooleanVar(value=False)
        
        self.tree_edit_entry = None
        
        # Load config
        self.load_config()
        
        # Build UI
        self.build_ui()
        
        # Check command line args for --silent mode
        import sys
        self.is_silent = "--silent" in sys.argv
        if self.is_silent:
            self.root.iconify()
        
        # Start periodic mount check thread
        self.running_status_check = True
        threading.Thread(target=self.periodic_status_checker, daemon=True).start()

        # Auto-mount if configured
        if self.auto_mount_on_startup_var.get() or self.is_silent:
            self.root.after(500, self.auto_mount_all_configured)

    def load_config(self):
        self.remotes = []
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.remotes = data.get("remotes", [])
                    self.start_disk_letter_var.set(data.get("start_disk_letter", "K"))
                    self.tailscale_api_key_var.set(data.get("tailscale_api_key", ""))
                    self.tailscale_tailnet_var.set(data.get("tailscale_tailnet", "-"))
                    self.start_with_windows_var.set(data.get("start_with_windows", False))
                    self.auto_mount_on_startup_var.set(data.get("auto_mount_on_startup", False))
            except Exception as e:
                print(f"Error loading config: {e}")
        
        if not self.remotes:
            # Default empty / placeholder remote configuration
            self.remotes = [
                {
                    "name": "example_webdav",
                    "backend": "webdav",
                    "username": "admin",
                    "password": "password123",
                    "port": "8080",
                    "host": "100.100.100.100",
                    "folder": "/",
                    "disk_letter": "K",
                    "status": "Disconnected"
                }
            ]
            self.save_config()

    def save_config(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            # Remove volatile status before saving config
            save_remotes = []
            for r in self.remotes:
                r_copy = dict(r)
                r_copy["status"] = "Disconnected"
                save_remotes.append(r_copy)
                
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "remotes": save_remotes,
                    "start_disk_letter": self.start_disk_letter_var.get(),
                    "tailscale_api_key": self.tailscale_api_key_var.get(),
                    "tailscale_tailnet": self.tailscale_tailnet_var.get(),
                    "start_with_windows": self.start_with_windows_var.get(),
                    "auto_mount_on_startup": self.auto_mount_on_startup_var.get()
                }, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Configuration Rclone
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Cấu hình Rclone")
        
        # Tab 2: Tailscale API
        self.tab_tailscale = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tailscale, text="Kết nối Tailscale")
        
        self.build_tab_config()
        self.build_tab_tailscale()

    def build_tab_config(self):
        container = ttk.Frame(self.tab_config, padding=20)
        container.pack(fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(container)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(header_frame, text="RCLONE DISK MOUNT MANAGER", style="Header.TLabel").pack(side="left")
        
        # Import / Export buttons
        self.btn_export_json = ttk.Button(header_frame, text="Export JSON", style="Normal.TButton", command=self.export_json)
        self.btn_export_json.pack(side="right", padx=(5, 0))
        
        self.btn_import_json = ttk.Button(header_frame, text="Import JSON", style="Normal.TButton", command=self.import_json)
        self.btn_import_json.pack(side="right", padx=(5, 0))
        
        self.btn_export_rclone = ttk.Button(header_frame, text="Export rclone.conf", style="Normal.TButton", command=self.export_rclone_conf)
        self.btn_export_rclone.pack(side="right", padx=(5, 0))

        self.btn_import_rclone = ttk.Button(header_frame, text="Import rclone.conf", style="Normal.TButton", command=self.import_rclone_conf)
        self.btn_import_rclone.pack(side="right")
        
        # Settings Bar
        settings_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        settings_card.pack(fill="x", pady=(0, 15))
        
        ttk.Label(settings_card, text="Ký tự ổ đĩa bắt đầu (Start Letter):", style="Card.TLabel").pack(side="left", padx=(0, 5))
        
        letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        self.combo_start_letter = ttk.Combobox(settings_card, textvariable=self.start_disk_letter_var, values=letters, state="readonly", width=5)
        self.combo_start_letter.pack(side="left", padx=(0, 15))
        self.combo_start_letter.bind("<<ComboboxSelected>>", lambda e: self.auto_assign_all_disk_letters())
        
        btn_auto_assign = ttk.Button(settings_card, text="Tự động phân bổ ổ đĩa", style="Normal.TButton", command=self.auto_assign_all_disk_letters)
        btn_auto_assign.pack(side="left")
        
        # Checkboxes for Startup and Auto-Mount (Styled for Dark Mode using tk.Checkbutton)
        self.chk_startup = tk.Checkbutton(
            settings_card, 
            text="Khởi động cùng Windows", 
            variable=self.start_with_windows_var, 
            command=self.toggle_startup,
            bg=self.card_color, 
            fg=self.text_color, 
            selectcolor=self.bg_color, 
            activebackground=self.card_color, 
            activeforeground=self.text_color,
            relief="flat", 
            bd=0, 
            font=("Segoe UI", 10)
        )
        self.chk_startup.pack(side="right", padx=(10, 0))
        
        self.chk_automount = tk.Checkbutton(
            settings_card, 
            text="Tự động Mount khi mở app", 
            variable=self.auto_mount_on_startup_var, 
            command=self.save_config,
            bg=self.card_color, 
            fg=self.text_color, 
            selectcolor=self.bg_color, 
            activebackground=self.card_color, 
            activeforeground=self.text_color,
            relief="flat", 
            bd=0, 
            font=("Segoe UI", 10)
        )
        self.chk_automount.pack(side="right", padx=(10, 0))
        
        # Treeview Configuration
        table_outer_frame = ttk.Frame(container, style="Card.TFrame")
        table_outer_frame.pack(fill="both", expand=True)
        
        # Column names
        self.tree_columns = ("Name", "Backend", "Username", "Password", "Port", "Host", "Folder", "Disk", "Status")
        self.tree = ttk.Treeview(table_outer_frame, columns=self.tree_columns, show="headings", style="Treeview", selectmode="extended")
        
        headers = {
            "Name": "Tên Remote",
            "Backend": "Giao thức",
            "Username": "Tài khoản",
            "Password": "Mật khẩu",
            "Port": "Cổng",
            "Host": "IP/Domain Tailscale",
            "Folder": "Folder Map",
            "Disk": "Ổ đĩa",
            "Status": "Trạng thái"
        }
        
        for col in self.tree_columns:
            self.tree.heading(col, text=headers[col], command=lambda c=col: self.sort_treeview(c, False))
            width = 120 if col in ("Name", "Host") else (80 if col in ("Port", "Disk", "Status", "Backend") else 100)
            self.tree.column(col, width=width, anchor="w" if col not in ("Port", "Disk", "Status", "Backend") else "center")
            
        self.scroll = ttk.Scrollbar(table_outer_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        # Event bindings
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", lambda e: self.mount_selected_remotes())
        
        # Context Menu
        self.context_menu = tk.Menu(self.tree, tearoff=0, bg=self.card_color, fg=self.text_color, activebackground=self.accent_color, activeforeground="#ffffff")
        self.context_menu.add_command(label="Gắn ổ đĩa (Mount)", command=self.mount_selected_remotes)
        self.context_menu.add_command(label="Gỡ ổ đĩa (Unmount)", command=self.unmount_selected_remotes)
        self.context_menu.add_command(label="Nạp lại (Reload)", command=self.reload_selected_remotes)
        self.context_menu.add_command(label="Xem Log Mount", command=self.view_selected_mount_log)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Xóa cấu hình", command=self.delete_selected_remotes)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Bottom controls
        ctrl_frame = ttk.Frame(container)
        ctrl_frame.pack(fill="x", pady=(10, 0))
        
        self.lbl_selected_count = ttk.Label(ctrl_frame, text="Đã chọn: 0 / 0 mục", font=("Segoe UI", 10, "italic"))
        self.lbl_selected_count.pack(side="left", padx=(0, 15))
        
        btn_select_all = ttk.Button(ctrl_frame, text="Chọn tất cả", style="Normal.TButton", command=self.select_all)
        btn_select_all.pack(side="left", padx=5)
        
        btn_deselect = ttk.Button(ctrl_frame, text="Bỏ chọn", style="Normal.TButton", command=self.deselect_all)
        btn_deselect.pack(side="left", padx=5)
        
        btn_unmount = tk.Button(ctrl_frame, text="GỠ CÁC Ổ ĐĨA ĐÃ CHỌN", bg="#d9534f", fg="#ffffff", 
                                activebackground="#c9302c", activeforeground="#ffffff", relief="flat", bd=0, 
                                font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.unmount_selected_remotes)
        btn_unmount.pack(side="right", padx=(5, 0))

        btn_reload = tk.Button(ctrl_frame, text="NẠP LẠI (RELOAD) ĐÃ CHỌN", bg="#f0ad4e", fg="#ffffff", 
                               activebackground="#ec971f", activeforeground="#ffffff", relief="flat", bd=0, 
                               font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.reload_selected_remotes)
        btn_reload.pack(side="right", padx=(5, 0))

        btn_mount = tk.Button(ctrl_frame, text="GẮN CÁC Ổ ĐĨA ĐÃ CHỌN", bg="#28a745", fg="#ffffff", 
                              activebackground="#218838", activeforeground="#ffffff", relief="flat", bd=0, 
                              font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.mount_selected_remotes)
        btn_mount.pack(side="right")
        
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_selected_count())
        self.populate_treeview()

    def build_tab_tailscale(self):
        container = ttk.Frame(self.tab_tailscale, padding=20)
        container.pack(fill="both", expand=True)
        
        # Header
        sys_header_frame = ttk.Frame(container)
        sys_header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(sys_header_frame, text="KẾT NỐI TAILSCALE QUA AUTH KEY / API KEY", style="Header.TLabel").pack(side="left")
        
        self.btn_scan_tailscale = ttk.Button(sys_header_frame, text="⟳ Quét thiết bị", style="Accent.TButton", command=self.scan_tailscale_devices)
        self.btn_scan_tailscale.pack(side="right")
        
        # API config card
        api_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        api_card.pack(fill="x", pady=(0, 15))
        
        ttk.Label(api_card, text="Tailscale Key (tskey-auth-... hoặc tskey-api-...):", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.entry_api_key = tk.Entry(api_card, textvariable=self.tailscale_api_key_var, show="*", bg=self.bg_color, fg=self.text_color, 
                                     insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                     highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), width=45)
        self.entry_api_key.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 10))
        
        ttk.Label(api_card, text="Tên Tailnet (Domain/Email - chỉ dùng cho API Key):", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        self.entry_tailnet = tk.Entry(api_card, textvariable=self.tailscale_tailnet_var, bg=self.bg_color, fg=self.text_color, 
                                     insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                     highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), width=45)
        self.entry_tailnet.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Devices table
        devices_outer = ttk.Frame(container, style="Card.TFrame")
        devices_outer.pack(fill="both", expand=True)
        
        self.ts_columns = ("Name", "IP", "OS", "Status")
        self.ts_tree = ttk.Treeview(devices_outer, columns=self.ts_columns, show="headings", style="Treeview", selectmode="browse")
        
        ts_headers = {
            "Name": "Tên Thiết Bị",
            "IP": "Địa chỉ IP",
            "OS": "Hệ điều hành",
            "Status": "Trạng thái kết nối"
        }
        
        for col in self.ts_columns:
            self.ts_tree.heading(col, text=ts_headers[col], command=lambda c=col: self.sort_ts_treeview(c, False))
            self.ts_tree.column(col, width=150 if col == "Name" else 100, anchor="w" if col == "Name" else "center")
            
        self.ts_scroll = ttk.Scrollbar(devices_outer, orient="vertical", command=self.ts_tree.yview)
        self.ts_tree.configure(yscrollcommand=self.ts_scroll.set)
        
        self.ts_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.ts_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        # Double click on device to copy IP
        self.ts_tree.bind("<Double-1>", self.on_ts_device_double_click)
        
        # Info & buttons bar
        ts_ctrl_bar = ttk.Frame(container)
        ts_ctrl_bar.pack(fill="x", pady=(10, 0))
        
        self.lbl_ts_status = ttk.Label(ts_ctrl_bar, text="Mẹo: Click đúp hoặc nhấn nút bên phải để tự động gán/tạo cấu hình & mount ổ đĩa ngay lập tức.", font=("Segoe UI", 9, "italic"))
        self.lbl_ts_status.pack(side="left", anchor="w")
        
        self.btn_ts_direct_mount = tk.Button(ts_ctrl_bar, text="GẮN Ổ ĐĨA TRỰC TIẾP", bg="#28a745", fg="#ffffff",
                                             activebackground="#218838", activeforeground="#ffffff", relief="flat", bd=0,
                                             font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.on_ts_direct_mount_clicked)
        self.btn_ts_direct_mount.pack(side="right")

    def populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Pinned row for adding a new configuration
        self.tree.insert("", "end", iid="__add_row__", values=("+ Thêm mới...", "webdav", "admin", "password", "80", "127.0.0.1", "/", "", "New"))
        
        for idx, remote in enumerate(self.remotes):
            status = remote.get("status", "Disconnected")
            # Obscure password visual output
            pwd_disp = "*" * len(remote.get("password", ""))
            self.tree.insert("", "end", iid=f"remote_{idx}", values=(
                remote.get("name", ""),
                remote.get("backend", "webdav"),
                remote.get("username", ""),
                pwd_disp,
                remote.get("port", ""),
                remote.get("host", ""),
                remote.get("folder", ""),
                remote.get("disk_letter", ""),
                status
            ))
        self.update_selected_count()

    def update_selected_count(self):
        total = len(self.remotes)
        selected_items = [item for item in self.tree.selection() if item != "__add_row__"]
        selected = len(selected_items)
        self.lbl_selected_count.config(text=f"Đã chọn: {selected} / {total} mục")

    def select_all(self):
        children = [c for c in self.tree.get_children() if c != "__add_row__"]
        self.tree.selection_set(children)
        self.update_selected_count()

    def deselect_all(self):
        self.tree.selection_remove(self.tree.get_children())
        self.update_selected_count()

    def sort_treeview(self, col, reverse):
        items = []
        for item_id in self.tree.get_children(""):
            if item_id == "__add_row__":
                continue
            val = self.tree.set(item_id, col)
            # If sorting passwords, sort by actual remote password value rather than asterisks
            if col == "Password" and item_id.startswith("remote_"):
                try:
                    idx = int(item_id.split("_")[1])
                    val = self.remotes[idx].get("password", "")
                except Exception:
                    pass
            items.append((val, item_id))
            
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, item_id) in enumerate(items):
            self.tree.move(item_id, "", index)
        self.tree.heading(col, command=lambda c=col: self.sort_treeview(c, not reverse))

    def sort_ts_treeview(self, col, reverse):
        items = [(self.ts_tree.set(item_id, col), item_id) for item_id in self.ts_tree.get_children("")]
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, item_id) in enumerate(items):
            self.ts_tree.move(item_id, "", index)
        self.ts_tree.heading(col, command=lambda c=col: self.sort_ts_treeview(c, not reverse))

    def on_tree_click(self, event):
        if self.tree_edit_entry:
            self.tree_edit_entry.destroy()
            self.tree_edit_entry = None
            
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        # Don't edit status column (#9)
        if column == "#9":
            return
            
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
            
        x, y, w, h = bbox
        
        # Column names mapping
        col_index = int(column.replace("#", "")) - 1
        col_name = self.tree_columns[col_index]
        
        # Get actual value from self.remotes if editing an existing row's password
        val = ""
        if item.startswith("remote_"):
            try:
                idx = int(item.split("_")[1])
                val = str(self.remotes[idx].get(col_name.lower(), ""))
            except Exception:
                val = self.tree.set(item, column)
        else:
            val = self.tree.set(item, column)
            if val in ("+ Thêm mới...", "Nhập..."):
                val = ""
                
        if col_name == "Backend":
            combo = ttk.Combobox(self.tree, values=["webdav", "sftp"], state="readonly")
            combo.set(val or "webdav")
            combo.place(x=x, y=y, width=w, height=h)
            combo.focus_set()
            combo.bind("<<ComboboxSelected>>", lambda e: self.save_cell_edit(item, col_name, combo.get()))
            combo.bind("<FocusOut>", lambda e: self.save_cell_edit(item, col_name, combo.get()))
            self.tree_edit_entry = combo
        elif col_name == "Disk":
            letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]
            combo = ttk.Combobox(self.tree, values=letters, state="readonly")
            combo.set(val or "K")
            combo.place(x=x, y=y, width=w, height=h)
            combo.focus_set()
            combo.bind("<<ComboboxSelected>>", lambda e: self.save_cell_edit(item, col_name, combo.get()))
            combo.bind("<FocusOut>", lambda e: self.save_cell_edit(item, col_name, combo.get()))
            self.tree_edit_entry = combo
        else:
            entry = tk.Entry(self.tree, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, relief="flat", font=("Segoe UI", 10))
            entry.insert(0, val)
            entry.select_range(0, tk.END)
            entry.place(x=x, y=y, width=w, height=h)
            entry.focus_set()
            entry.bind("<Return>", lambda e: self.save_cell_edit(item, col_name, entry.get()))
            entry.bind("<FocusOut>", lambda e: self.save_cell_edit(item, col_name, entry.get()))
            self.tree_edit_entry = entry

    def save_cell_edit(self, item, col_name, new_val):
        if self.tree_edit_entry:
            widget = self.tree_edit_entry
            self.tree_edit_entry = None
            widget.destroy()
            
        new_val = new_val.strip()
        
        if item == "__add_row__":
            # Temp row edits
            col_idx = self.tree_columns.index(col_name)
            self.tree.set(item, col_name, new_val)
            
            # Read row values
            row_vals = [self.tree.set(item, c) for c in self.tree_columns]
            name = row_vals[0]
            backend = row_vals[1]
            username = row_vals[2]
            password = row_vals[3]
            port = row_vals[4]
            host = row_vals[5]
            folder = row_vals[6]
            disk = row_vals[7]
            
            # If name and host are filled, create new entry
            if name and name != "+ Thêm mới..." and host and host != "127.0.0.1":
                # Auto increment disk letter if empty
                if not disk:
                    disk = self.get_next_available_disk_letter()
                
                self.remotes.append({
                    "name": name,
                    "backend": backend or "webdav",
                    "username": username,
                    "password": password,
                    "port": port or ("80" if backend == "webdav" else "22"),
                    "host": host,
                    "folder": folder or "/",
                    "disk_letter": disk,
                    "status": "Disconnected"
                })
                self.populate_treeview()
                self.save_config()
        else:
            if item.startswith("remote_"):
                try:
                    idx = int(item.split("_")[1])
                    if 0 <= idx < len(self.remotes):
                        self.remotes[idx][col_name.lower()] = new_val
                        # Refresh row
                        disp_val = "*" * len(new_val) if col_name == "Password" else new_val
                        self.tree.set(item, col_name, disp_val)
                        self.save_config()
                except Exception as e:
                    print(f"Error editing cell: {e}")

    def get_next_available_disk_letter(self):
        start_char = self.start_disk_letter_var.get() or "K"
        start_ord = ord(start_char)
        used_letters = {r.get("disk_letter", "").upper() for r in self.remotes}
        
        for i in range(start_ord, ord('Z')+1):
            char = chr(i)
            if char not in used_letters:
                return char
        for i in range(ord('A'), start_ord):
            char = chr(i)
            if char not in used_letters:
                return char
        return "Z"

    def auto_assign_all_disk_letters(self):
        start_char = self.start_disk_letter_var.get() or "K"
        start_ord = ord(start_char)
        
        current_idx = start_ord
        for r in self.remotes:
            if current_idx <= ord('Z'):
                r["disk_letter"] = chr(current_idx)
                current_idx += 1
            else:
                r["disk_letter"] = "Z"
                
        self.populate_treeview()
        self.save_config()

    def show_context_menu(self, event):
        item_under_mouse = self.tree.identify_row(event.y)
        if item_under_mouse and item_under_mouse != "__add_row__":
            current_selection = self.tree.selection()
            if item_under_mouse not in current_selection:
                self.tree.selection_set(item_under_mouse)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def delete_selected_remotes(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("remote_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một cấu hình để xóa.")
            return
            
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa {len(selected_items)} cấu hình Rclone?")
        if not confirm:
            return
            
        indices_to_delete = []
        for item in selected_items:
            try:
                idx = int(item.split("_")[1])
                indices_to_delete.append(idx)
            except ValueError:
                pass
                
        indices_to_delete.sort(reverse=True)
        for idx in indices_to_delete:
            if 0 <= idx < len(self.remotes):
                # Unmount if running
                disk = self.remotes[idx].get("disk_letter", "")
                if disk in self.active_mounts:
                    try:
                        self.active_mounts[disk].terminate()
                    except Exception:
                        pass
                    del self.active_mounts[disk]
                del self.remotes[idx]
                
        self.populate_treeview()
        self.save_config()

    def is_winfsp_installed(self):
        paths = [
            r"C:\Program Files (x86)\WinFsp",
            r"C:\Program Files\WinFsp"
        ]
        for p in paths:
            if os.path.exists(os.path.join(p, "bin", "winfsp-x64.dll")) or os.path.exists(os.path.join(p, "bin", "winfsp-x86.dll")):
                return True
        import winreg
        for hkey in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for subkey in (r"SOFTWARE\WinFsp", r"SOFTWARE\WOW6432Node\WinFsp"):
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        return True
                except Exception:
                    pass
        return False

    def check_and_install_winfsp(self):
        if self.is_winfsp_installed():
            return True
            
        ans = messagebox.askyesno(
            "Cài đặt WinFSP",
            "Máy tính chưa cài đặt phần mềm WinFSP (bắt buộc để Mount ổ đĩa ảo bằng Rclone).\n\n"
            "Bạn có muốn tiến hành cài đặt WinFSP ngay bây giờ không?"
        )
        if not ans:
            return False
            
        import sys
        msi_path = None
        if hasattr(sys, '_MEIPASS'):
            temp_path = os.path.join(sys._MEIPASS, "winfsp.msi")
            if os.path.exists(temp_path):
                msi_path = temp_path
        if not msi_path and os.path.exists("winfsp.msi"):
            msi_path = os.path.abspath("winfsp.msi")
            
        if msi_path:
            try:
                ps_cmd = f'Start-Process msiexec.exe -ArgumentList "/i \\"{msi_path}\\"" -Verb RunAs -Wait'
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
                if self.is_winfsp_installed():
                    messagebox.showinfo("Thành công", "Đã cài đặt WinFSP thành công! Bạn có thể sử dụng tính năng Mount.")
                    return True
                else:
                    messagebox.showwarning("Cảnh báo", "Tiến trình cài đặt WinFSP đã chạy nhưng hệ thống vẫn báo chưa cài đặt. Vui lòng kiểm tra lại.")
                    return False
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cài đặt WinFSP từ file đóng gói: {e}")
                return False
        else:
            # Download installer in background
            def run_download():
                try:
                    url = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"
                    target_path = os.path.join(CONFIG_DIR, "winfsp.msi")
                    os.makedirs(CONFIG_DIR, exist_ok=True)
                    
                    import urllib.request
                    urllib.request.urlretrieve(url, target_path)
                    
                    ps_cmd = f'Start-Process msiexec.exe -ArgumentList "/i \\"{target_path}\\"" -Verb RunAs -Wait'
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if self.is_winfsp_installed():
                        self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã tải và cài đặt WinFSP thành công! Hãy bấm Mount lại ổ đĩa."))
                    else:
                        self.root.after(0, lambda: messagebox.showwarning("Cảnh báo", "Cài đặt hoàn tất nhưng chưa phát hiện được driver WinFSP."))
                except Exception as ex:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tải/cài đặt WinFSP: {ex}"))
                    
            messagebox.showinfo("Đang tải", "Đang tiến hành tải xuống WinFSP msi từ GitHub. Vui lòng đợi trong giây lát...")
            threading.Thread(target=run_download, daemon=True).start()
            return False

    # Rclone mounting logic
    def mount_selected_remotes(self):
        if not self.check_and_install_winfsp():
            return
            
        selected_items = [item for item in self.tree.selection() if item.startswith("remote_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cấu hình Rclone để gắn ổ đĩa.")
            return
            
        # Run mounting logic in a separate thread to prevent UI freezing
        threading.Thread(target=self._mount_remotes_thread, args=(selected_items,), daemon=True).start()

    def _mount_remotes_thread(self, selected_items):
        # 1. Write config to rclone.conf file
        self.generate_rclone_conf()
        
        # 2. Check if any selected remote is a Tailscale IP/domain
        has_tailscale_remote = False
        for item in selected_items:
            try:
                idx = int(item.split("_")[1])
                remote = self.remotes[idx]
                host = remote.get("host", "")
                if self.is_tailscale_ip(host):
                    has_tailscale_remote = True
                    break
            except Exception:
                pass
                
        if has_tailscale_remote:
            self.ensure_tailscale_running()
            
        # 3. Mount each remote
        for item in selected_items:
            try:
                idx = int(item.split("_")[1])
                remote = self.remotes[idx]
                name = remote["name"]
                disk = remote["disk_letter"]
                host = remote.get("host", "")
                folder = remote.get("folder", "/")
                
                if not disk:
                    self.root.after(0, lambda n=name: messagebox.showerror("Lỗi", f"Vui lòng định cấu hình ký tự ổ đĩa cho remote {n}"))
                    continue
                    
                if disk in self.active_mounts:
                    # Already mounted
                    continue
                    
                self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Checking connection..."))
                
                # Check host reachability
                reachable = False
                for _ in range(10):
                    if self.is_host_reachable(host):
                        reachable = True
                        break
                    time.sleep(1)
                    
                if not reachable:
                    self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Failed"))
                    self.root.after(0, lambda n=name, h=host: messagebox.showerror(
                        "Lỗi kết nối", 
                        f"Không thể kết nối tới {h} (Remote: '{n}').\nVui lòng kiểm tra kết nối mạng hoặc dịch vụ Tailscale."
                    ))
                    continue
                
                self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Mounting..."))
                
                # Start rclone mount in background
                rclone_path = "rclone"  # Assume in PATH
                rclone_folder = folder.lstrip("/")
                remote_path = f"{name}:{rclone_folder}" if rclone_folder else f"{name}:"
                
                log_file = os.path.join(CONFIG_DIR, f"rclone_mount_{disk}.log")
                cmd = [
                    rclone_path,
                    "mount",
                    remote_path,
                    f"{disk}:",
                    "--vfs-cache-mode", "writes",
                    "--config", RCLONE_CONF_FILE,
                    "--log-file", log_file,
                    "--log-level", "INFO"
                ]
                
                # Run process
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.active_mounts[disk] = proc
                remote["status"] = "Mounted"
                self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Mounted"))
                
                # Check for early process exit in a background thread
                def check_proc(p, r_name, r_item, r_disk):
                    try:
                        time.sleep(2.0)
                        poll = p.poll()
                        if poll is not None:
                            # Process exited, mount failed
                            err_output = p.stderr.read().decode("utf-8", errors="replace").strip()
                            
                            log_path = os.path.join(CONFIG_DIR, f"rclone_mount_{r_disk}.log")
                            if not err_output and os.path.exists(log_path):
                                try:
                                    with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                                        lines = lf.readlines()
                                        err_output = "".join(lines[-10:]).strip()
                                except Exception:
                                    pass
                                    
                            if r_disk in self.active_mounts:
                                del self.active_mounts[r_disk]
                            
                            self.root.after(0, lambda: self.tree.set(r_item, "Status", "Failed"))
                            
                            msg = f"Gắn ổ đĩa {r_disk}: cho remote '{r_name}' thất bại!\n\n"
                            if "winfsp" in err_output.lower() or "fuse" in err_output.lower():
                                msg += "LỖI: Rclone yêu cầu phần mềm WinFSP để gắn ổ đĩa ảo trên Windows.\nVui lòng cài đặt WinFSP (https://winfsp.dev/) và khởi động lại máy."
                            elif "network host" in err_output.lower() or "connection refused" in err_output.lower() or "connect: connection refused" in err_output.lower():
                                msg += "LỖI: Không thể kết nối tới IP/Cổng của remote. Hãy kiểm tra xem thiết bị Tailscale đã online chưa."
                            elif err_output:
                                msg += f"Chi tiết lỗi từ Rclone Log:\n{err_output}"
                            else:
                                msg += "Rclone kết thúc đột ngột mà không ghi lại mã lỗi."
                                
                            self.root.after(0, lambda m=msg: messagebox.showerror("Lỗi Rclone Mount", m))
                    except Exception as ex:
                        print(f"Error checking rclone proc: {ex}")

                threading.Thread(target=check_proc, args=(proc, name, item, disk), daemon=True).start()
            except FileNotFoundError:
                self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Failed"))
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy chương trình 'rclone' trên máy tính.\n\nVui lòng tải Rclone và thêm thư mục chứa rclone.exe vào biến môi trường PATH hệ thống."))
            except Exception as e:
                self.root.after(0, lambda it=item: self.tree.set(it, "Status", "Failed"))
                self.root.after(0, lambda ex=e: messagebox.showerror("Lỗi", f"Không thể gắn ổ đĩa: {ex}"))

    def unmount_selected_remotes(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("remote_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cấu hình Rclone để gỡ ổ đĩa.")
            return
            
        for item in selected_items:
            try:
                idx = int(item.split("_")[1])
                remote = self.remotes[idx]
                disk = remote["disk_letter"]
                
                if disk in self.active_mounts:
                    proc = self.active_mounts[disk]
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    del self.active_mounts[disk]
                    
                remote["status"] = "Disconnected"
                self.tree.set(item, "Status", "Disconnected")
            except Exception as e:
                print(f"Error unmounting {e}")

    def auto_mount_all_configured(self):
        # Select all configured remotes
        children = [c for c in self.tree.get_children() if c != "__add_row__"]
        if children:
            self.tree.selection_set(children)
            self.mount_selected_remotes()

    def is_tailscale_ip(self, host):
        if not host:
            return False
        # Match 100.x.y.z
        parts = host.split('.')
        if len(parts) == 4 and parts[0] == '100':
            return True
        if host.endswith(".tailscale.net"):
            return True
        return False

    def is_host_reachable(self, host):
        if not host:
            return False
        try:
            res = subprocess.run(["ping", "-n", "1", "-w", "1000", host], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False

    def ensure_tailscale_running(self):
        ts_path = self.get_tailscale_path()
        if not ts_path:
            return False
            
        # Check status first
        try:
            res = subprocess.run([ts_path, "status", "--json"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0:
                return True
        except Exception:
            pass
            
        # Try finding and starting tailscale-ipn.exe (GUI client)
        ts_dir = os.path.dirname(ts_path)
        gui_paths = []
        if ts_dir:
            gui_paths.append(os.path.join(ts_dir, "tailscale-ipn.exe"))
        else:
            gui_paths.extend([
                r"C:\Program Files\Tailscale\tailscale-ipn.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tailscale", "tailscale-ipn.exe"),
                "tailscale-ipn.exe"
            ])
            
        for gp in gui_paths:
            if gp == "tailscale-ipn.exe" or os.path.exists(gp):
                try:
                    subprocess.Popen([gp], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    time.sleep(3) # Give it a few seconds to start
                    return True
                except Exception:
                    pass
                    
        # Fallback to 'tailscale up'
        try:
            subprocess.Popen([ts_path, "up"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(3)
            return True
        except Exception:
            pass
            
        return False

    def toggle_startup(self):
        import winreg
        import sys
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "RcloneDiskManager"
        
        enabled = self.start_with_windows_var.get()
        self.save_config()
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                if hasattr(sys, 'frozen'):
                    app_path = sys.executable
                else:
                    app_path = os.path.abspath(sys.argv[0])
                
                cmd_line = f'"{app_path}" --silent'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd_line)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error toggling startup registry: {e}")

    def reload_selected_remotes(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("remote_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cấu hình Rclone để nạp lại.")
            return
            
        # Unmount first
        self.unmount_selected_remotes()
        
        # Wait 1 second to release resource then mount again
        def run_remount():
            time.sleep(1)
            self.root.after(0, self.mount_selected_remotes)
            
        threading.Thread(target=run_remount, daemon=True).start()

    def view_selected_mount_log(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("remote_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cấu hình Rclone để xem log.")
            return
            
        try:
            idx = int(selected_items[0].split("_")[1])
            disk = self.remotes[idx].get("disk_letter", "")
            if not disk:
                return
                
            log_file = os.path.join(CONFIG_DIR, f"rclone_mount_{disk}.log")
            if os.path.exists(log_file):
                os.startfile(log_file)
            else:
                messagebox.showinfo("Thông tin", f"Không tìm thấy tệp tin log tại:\n{log_file}\nHãy bấm Mount ổ đĩa trước.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở tệp tin log: {e}")

    def generate_rclone_conf(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(RCLONE_CONF_FILE, "w", encoding="utf-8") as f:
            for r in self.remotes:
                name = r["name"]
                backend = r["backend"]
                user = r["username"]
                pwd = r["password"]
                host = r["host"]
                port = r["port"]
                
                # Obscure password using rclone obscure via subprocess
                obscured_pwd = pwd
                try:
                    res = subprocess.run(["rclone", "obscure", pwd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if res.returncode == 0:
                        obscured_pwd = res.stdout.strip()
                except Exception:
                    pass
                
                f.write(f"[{name}]\n")
                if backend == "webdav":
                    f.write("type = webdav\n")
                    # WebDAV URL formation
                    f.write(f"url = http://{host}:{port}\n")
                    f.write(f"user = {user}\n")
                    f.write(f"pass = {obscured_pwd}\n")
                elif backend == "sftp":
                    f.write("type = sftp\n")
                    f.write(f"host = {host}\n")
                    f.write(f"port = {port}\n")
                    f.write(f"user = {user}\n")
                    f.write(f"pass = {obscured_pwd}\n")
                f.write("\n")

    def periodic_status_checker(self):
        while self.running_status_check:
            # Check if mount processes are still alive or if local drive is connected
            for disk, proc in list(self.active_mounts.items()):
                poll = proc.poll()
                # If poll is not None, the process has exited
                if poll is not None:
                    # Mount stopped/crashed
                    if disk in self.active_mounts:
                        del self.active_mounts[disk]
                    # Update status
                    for r in self.remotes:
                        if r["disk_letter"] == disk:
                            r["status"] = "Disconnected"
                            break
                            
            # Verify actual drive availability on Windows
            for r in self.remotes:
                disk = r["disk_letter"]
                if disk:
                    drive_exists = os.path.exists(f"{disk}:\\")
                    if drive_exists and r["status"] != "Mounted":
                        r["status"] = "Mounted"
                    elif not drive_exists and r["status"] == "Mounted" and disk not in self.active_mounts:
                        r["status"] = "Disconnected"
            
            # Update UI safely
            try:
                self.root.after(0, self.update_status_column_ui)
            except Exception:
                pass
            time.sleep(3)

    def update_status_column_ui(self):
        for idx, remote in enumerate(self.remotes):
            item_iid = f"remote_{idx}"
            if self.tree.exists(item_iid):
                self.tree.set(item_iid, "Status", remote.get("status", "Disconnected"))

    def get_tailscale_path(self):
        paths = [
            "tailscale",
            r"C:\Program Files\Tailscale\tailscale.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tailscale", "tailscale.exe")
        ]
        for p in paths:
            try:
                res = subprocess.run([p, "version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if res.returncode == 0:
                    return p
            except Exception:
                pass
        return "tailscale"

    # Tailscale API methods
    def scan_tailscale_devices(self):
        key = self.tailscale_api_key_var.get().strip()
        tailnet = self.tailscale_tailnet_var.get().strip()
        
        if not key:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập Tailscale Key.")
            return
            
        self.btn_scan_tailscale.config(state="disabled", text="⌛ Đang quét...")
        for item in self.ts_tree.get_children():
            self.ts_tree.delete(item)
            
        self.ts_tree.insert("", "end", values=("⌛ Đang kết nối Tailscale...", "", "", ""))
        
        def run_fetch():
            try:
                if key.startswith("tskey-auth-"):
                    # Local Tailscale authentication & status parsing
                    ts_path = self.get_tailscale_path()
                    
                    # 1. Run tailscale up with the auth key
                    up_cmd = [ts_path, "up", f"--authkey={key}"]
                    subprocess.run(up_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # 2. Get tailscale status in JSON format
                    status_cmd = [ts_path, "status", "--json"]
                    status_res = subprocess.run(status_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if status_res.returncode != 0:
                        raise Exception("Không thể chạy lệnh tailscale status. Vui lòng kiểm tra xem dịch vụ Tailscale đã chạy chưa.")
                        
                    data = json.loads(status_res.stdout)
                    devices = []
                    
                    # Add Self device
                    self_dev = data.get("Self", {})
                    if self_dev:
                        ips = self_dev.get("TailscaleIPs", [])
                        ip = "-"
                        for addr in ips:
                            if addr.startswith("100."):
                                ip = addr
                                break
                        if ip == "-" and ips:
                            ip = ips[0]
                        devices.append({
                            "hostname": self_dev.get("HostName", "This Device") + " (Self)",
                            "ip": ip,
                            "os": self_dev.get("OS", "-"),
                            "status": "Online"
                        })
                        
                    # Add Peer devices
                    peers = data.get("Peer", {})
                    if peers:
                        for peer_id, peer in peers.items():
                            p_ips = peer.get("TailscaleIPs", [])
                            ip = "-"
                            for addr in p_ips:
                                if addr.startswith("100."):
                                    ip = addr
                                    break
                            if ip == "-" and p_ips:
                                ip = p_ips[0]
                            devices.append({
                                "hostname": peer.get("HostName", "Unknown"),
                                "ip": ip,
                                "os": peer.get("OS", "-"),
                                "status": "Online" if peer.get("Active", False) else "Offline"
                            })
                            
                    self.root.after(0, lambda: self.populate_ts_devices_list(devices))
                else:
                    # REST API Fetching
                    t_net = tailnet if tailnet and tailnet != "-" else "me"
                    url = f"https://api.tailscale.com/api/v2/tailnet/{t_net}/devices"
                    
                    req = urllib.request.Request(url)
                    auth_str = base64.b64encode(f"{key}:".encode()).decode()
                    req.add_header("Authorization", f"Basic {auth_str}")
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_body = response.read().decode()
                        api_data = json.loads(res_body)
                        api_devices = api_data.get("devices", [])
                        
                        devices = []
                        for dev in api_devices:
                            ips = dev.get("addresses", [])
                            ip = "-"
                            for addr in ips:
                                if addr.startswith("100."):
                                    ip = addr
                                    break
                            if ip == "-" and ips:
                                ip = ips[0]
                            devices.append({
                                "hostname": dev.get("hostname", dev.get("name", "Unknown")),
                                "ip": ip,
                                "os": dev.get("os", "-"),
                                "status": "Online" if dev.get("clientConnectivity", {}).get("online", False) else "Offline"
                            })
                        self.root.after(0, lambda: self.populate_ts_devices_list(devices))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi xử lý Tailscale: {e}"))
                self.root.after(0, self.clear_ts_tree_error)
            finally:
                self.root.after(0, lambda: self.btn_scan_tailscale.config(state="normal", text="⟳ Quét thiết bị"))
                
        threading.Thread(target=run_fetch, daemon=True).start()

    def populate_ts_devices_list(self, devices):
        for item in self.ts_tree.get_children():
            self.ts_tree.delete(item)
            
        if not devices:
            self.ts_tree.insert("", "end", values=("Không có thiết bị nào", "", "", ""))
            return
            
        for dev in devices:
            self.ts_tree.insert("", "end", values=(dev["hostname"], dev["ip"], dev["os"], dev["status"]))

    def clear_ts_tree_error(self):
        for item in self.ts_tree.get_children():
            self.ts_tree.delete(item)

    def on_ts_device_double_click(self, event):
        self.on_ts_direct_mount_clicked()

    def on_ts_direct_mount_clicked(self):
        selected_ts = self.ts_tree.selection()
        if not selected_ts:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một thiết bị Tailscale.")
            return
            
        ts_values = self.ts_tree.item(selected_ts[0], "values")
        if not ts_values or len(ts_values) < 2:
            return
            
        name = ts_values[0]
        ip = ts_values[1]
        
        if ip == "-" or not ip:
            messagebox.showwarning("Cảnh báo", "Thiết bị không có địa chỉ IP Tailscale hợp lệ.")
            return
            
        # Clean hostname for rclone remote name
        clean_name = "".join(c for c in name if c.isalnum() or c in ("_", "-")).lower()
        if clean_name.endswith("self"):
            clean_name = clean_name.replace("self", "")
        clean_name = clean_name.strip("-_")
        if not clean_name:
            clean_name = "ts_remote"
            
        # Check if remote already exists with this IP or name
        existing_idx = None
        for idx, r in enumerate(self.remotes):
            if r.get("host") == ip or r.get("name") == clean_name:
                existing_idx = idx
                break
                
        if existing_idx is not None:
            # Mount the existing remote
            remote = self.remotes[existing_idx]
            item_iid = f"remote_{existing_idx}"
            self.notebook.select(self.tab_config) # switch to Tab 1
            self.tree.selection_set(item_iid)
            self.tree.focus(item_iid)
            self.mount_selected_remotes()
            messagebox.showinfo("Thành công", f"Đã tìm thấy cấu hình '{remote['name']}' và tiến hành gắn ổ đĩa {remote['disk_letter']}:")
        else:
            # Create a new remote configuration
            disk = self.get_next_available_disk_letter()
            new_remote = {
                "name": clean_name,
                "backend": "webdav",
                "username": "admin",
                "password": "password",
                "port": "80",
                "host": ip,
                "folder": "/",
                "disk_letter": disk,
                "status": "Disconnected"
            }
            self.remotes.append(new_remote)
            self.populate_treeview()
            self.save_config()
            
            # Select the newly added remote and mount it
            new_idx = len(self.remotes) - 1
            item_iid = f"remote_{new_idx}"
            self.notebook.select(self.tab_config) # switch to Tab 1
            self.tree.selection_set(item_iid)
            self.tree.focus(item_iid)
            self.mount_selected_remotes()
            messagebox.showinfo("Thành công", f"Đã tạo cấu hình mới '{clean_name}' và gắn vào ổ đĩa {disk}:")

    # JSON Import / Export
    def export_json(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Rclone Manager Config",
            initialfile="rclone_manager_config.json",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "remotes": self.remotes,
                    "start_disk_letter": self.start_disk_letter_var.get(),
                    "tailscale_api_key": self.tailscale_api_key_var.get(),
                    "tailscale_tailnet": self.tailscale_tailnet_var.get()
                }, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Thành công", f"Đã xuất cấu hình JSON thành công:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file JSON: {e}")

    def import_json(self):
        file_path = filedialog.askopenfilename(
            title="Import Rclone Manager Config",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            remotes = data.get("remotes", [])
            if not isinstance(remotes, list):
                messagebox.showerror("Lỗi", "Định dạng file JSON không hợp lệ.")
                return
                
            ans = messagebox.askyesno("Import Config", "Bạn có muốn thay thế toàn bộ danh sách cấu hình hiện tại không?")
            if ans:
                self.remotes = remotes
            else:
                # Merge
                for r in remotes:
                    if not any(ex["name"].lower() == r["name"].lower() for ex in self.remotes):
                        self.remotes.append(r)
            
            if "start_disk_letter" in data:
                self.start_disk_letter_var.set(data["start_disk_letter"])
            if "tailscale_api_key" in data:
                self.tailscale_api_key_var.set(data["tailscale_api_key"])
            if "tailscale_tailnet" in data:
                self.tailscale_tailnet_var.set(data["tailscale_tailnet"])
                
            self.populate_treeview()
            self.save_config()
            messagebox.showinfo("Thành công", "Đã nhập cấu hình JSON thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập file JSON: {e}")

    # Standard rclone.conf Import / Export
    def export_rclone_conf(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Rclone Config File",
            initialfile="rclone.conf",
            defaultextension=".conf",
            filetypes=[("Conf Files", "*.conf"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            self.generate_rclone_conf()
            # Copy local rclone.conf to the target path
            import shutil
            shutil.copy(RCLONE_CONF_FILE, file_path)
            messagebox.showinfo("Thành công", f"Đã xuất file rclone.conf thành công:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file rclone.conf: {e}")

    def import_rclone_conf(self):
        file_path = filedialog.askopenfilename(
            title="Import Rclone Config File",
            filetypes=[("Conf Files", "*.conf"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            # Parse .conf / INI format
            imported_remotes = []
            current_remote = None
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith(";"):
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        if current_remote:
                            imported_remotes.append(current_remote)
                        current_remote = {"name": line[1:-1], "backend": "webdav", "username": "", "password": "", "port": "", "host": "", "folder": "/", "disk_letter": ""}
                    elif current_remote and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().lower()
                        v = v.strip()
                        
                        if k == "type":
                            current_remote["backend"] = v
                        elif k == "user":
                            current_remote["username"] = v
                        elif k == "pass":
                            # Try to de-obscure
                            clear_pwd = v
                            try:
                                res = subprocess.run(["rclone", "reveal", v], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                                if res.returncode == 0:
                                    clear_pwd = res.stdout.strip()
                            except Exception:
                                pass
                            current_remote["password"] = clear_pwd
                        elif k == "port":
                            current_remote["port"] = v
                        elif k == "host":
                            current_remote["host"] = v
                        elif k == "url":
                            # Try parsing host/port/folder from webdav url
                            # Format: http://host:port/folder or similar
                            from urllib.parse import urlparse
                            try:
                                parsed = urlparse(v)
                                current_remote["host"] = parsed.hostname or ""
                                if parsed.port:
                                    current_remote["port"] = str(parsed.port)
                                current_remote["folder"] = parsed.path or "/"
                            except Exception:
                                current_remote["host"] = v
                                
                if current_remote:
                    imported_remotes.append(current_remote)
                    
            if not imported_remotes:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy cấu hình hợp lệ trong file conf.")
                return
                
            ans = messagebox.askyesno("Import Config", "Bạn có muốn thay thế toàn bộ danh sách cấu hình hiện tại bằng dữ liệu import?")
            if ans:
                self.remotes = imported_remotes
            else:
                for ir in imported_remotes:
                    if not any(ex["name"].lower() == ir["name"].lower() for ex in self.remotes):
                        self.remotes.append(ir)
            
            # Fill missing disk letters
            for r in self.remotes:
                if not r.get("disk_letter"):
                    r["disk_letter"] = self.get_next_available_disk_letter()
                    
            self.populate_treeview()
            self.save_config()
            messagebox.showinfo("Thành công", f"Đã nhập thành công {len(imported_remotes)} cấu hình từ rclone.conf.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập file rclone.conf: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RcloneManagementApp(root)
    # Stop periodic check when window closes
    def on_closing():
        app.running_status_check = False
        # Clean mount processes
        for disk, proc in app.active_mounts.items():
            try:
                proc.terminate()
            except Exception:
                pass
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
