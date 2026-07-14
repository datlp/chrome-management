import os
import json
import subprocess
import time
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CONFIG_DIR = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "dsoft", "chrome-profile-management")
CONFIG_FILE = os.path.join(CONFIG_DIR, "chrome_profiles_config.json")
BAT_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "old-refer-only", "chrome_all_profiles_must_install_extension_ids.bat")

DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(DEFAULT_CHROME_PATH):
    DEFAULT_CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

class ChromeProfileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Profiles Manager")
        self.root.geometry("680x750")
        self.root.minsize(450, 500)
        
        # Color palette (Modern Dark Mode)
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#00adb5"
        self.accent_hover = "#00fff5"
        self.text_color = "#eeeeee"
        self.text_muted = "#aaaaaa"
        self.border_color = "#393e46"
        self.narrow_mode = None
        
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Apply dark theme styles to standard ttk widgets
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_color, relief="flat")
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background=self.card_color, foreground=self.text_color, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color, font=("Segoe UI", 16, "bold"))
        self.style.configure("Sub.TLabel", background=self.card_color, foreground=self.text_muted, font=("Segoe UI", 9, "italic"))
        
        # Button styles
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="#ffffff", borderwidth=0, font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", self.accent_hover), ("pressed", self.accent_color)])
        
        self.style.configure("Normal.TButton", background=self.border_color, foreground=self.text_color, borderwidth=0, font=("Segoe UI", 10))
        self.style.map("Normal.TButton", background=[("active", "#4f555e")])

        self.style.configure("Open.TButton", background="#28a745", foreground="#ffffff", font=("Segoe UI", 9, "bold"))
        self.style.map("Open.TButton", background=[("active", "#218838")])

        # Scrollbar and Canvas styling
        self.style.configure("Vertical.TScrollbar", background=self.border_color, borderwidth=0, arrowsize=12)
        
        # Notebook styles
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.card_color, foreground=self.text_muted, borderwidth=1, lightcolor=self.border_color, bordercolor=self.border_color, font=("Segoe UI", 10, "bold"), padding=(15, 6))
        self.style.map("TNotebook.Tab", background=[("selected", self.bg_color)], foreground=[("selected", self.accent_color)])
        
        # Treeview styles
        self.style.configure("Treeview", background=self.card_color, foreground=self.text_color, fieldbackground=self.card_color, borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background=self.border_color, foreground=self.text_color, borderwidth=1, font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", self.accent_color)], foreground=[("selected", "#ffffff")])

        # Debounce and change state
        self.debounce_timer = None
        self.current_mode = "sequential"
        self.is_loading_config = False
        
        # Variables
        self.website_var = tk.StringVar(value="https://google.com")
        self.simultaneous_var = tk.IntVar(value=5)
        self.chrome_path_var = tk.StringVar(value=DEFAULT_CHROME_PATH)
        self.select_n_var = tk.IntVar(value=5)
        
        # Extension CRUD variables
        self.extensions = []
        self.bat_header = []
        self.bat_footer = []
        self.ext_name_var = tk.StringVar()
        self.ext_id_var = tk.StringVar()
        self.selected_ext_idx = None # Tracks selected item index
        
        # Load existing config if available
        self.load_config()
        self.load_extensions_from_bat()
        
        # Bind traces after loading config
        self.website_var.trace_add("write", self.on_config_change)
        self.simultaneous_var.trace_add("write", self.on_config_change)
        self.chrome_path_var.trace_add("write", self.on_config_change)
        
        self.build_ui()

    def on_config_change(self, *args):
        if self.is_loading_config:
            return
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        self.debounce_timer = self.root.after(500, self.apply_config_change)

    def apply_config_change(self):
        self.refresh_profile_list(from_debounce=True)

    def load_config(self):
        self.is_loading_config = True
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.website_var.set(config.get("website", "https://google.com"))
                    self.simultaneous_var.set(config.get("simultaneous", 5))
                    self.chrome_path_var.set(config.get("chrome_path", DEFAULT_CHROME_PATH))
            except Exception as e:
                print(f"Error loading config: {e}")
        self.is_loading_config = False
 
    def save_config(self):
        config = {
            "website": self.website_var.get(),
            "simultaneous": self.simultaneous_var.get(),
            "chrome_path": self.chrome_path_var.get()
        }
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def build_ui(self):
        # Create ttk.Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Profile Manager
        self.tab_profiles = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_profiles, text="Quản lý Profile")
        
        # Tab 2: Extension Manager
        self.tab_extensions = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_extensions, text="Quản lý Extensions")
        
        # ==========================================
        # TAB 1: Profile Manager UI Construction
        # ==========================================
        # Main container with padding
        self.main_container = ttk.Frame(self.tab_profiles, padding=20)
        self.main_container.pack(fill="both", expand=True)
        
        # Header
        self.header_lbl = ttk.Label(self.main_container, text="CHROME PROFILES MANAGER", style="Header.TLabel")
        self.header_lbl.pack(pady=(0, 15), anchor="w")
        
        # Configuration Card
        self.config_card = ttk.Frame(self.main_container, style="Card.TFrame", padding=15)
        self.config_card.pack(fill="x", pady=(0, 15))
        
        # Website Selection
        self.web_lbl = ttk.Label(self.config_card, text="Trang Web (URL):", style="Card.TLabel")
        self.web_entry = tk.Entry(self.config_card, textvariable=self.website_var, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10))
        
        # Preset website buttons
        self.preset_frame = ttk.Frame(self.config_card, style="Card.TFrame")
        presets = ["google.com", "facebook.com", "youtube.com", "gmail.com"]
        for p in presets:
            btn = tk.Button(self.preset_frame, text=p, bg=self.border_color, fg=self.text_muted, activebackground=self.accent_color,
                            activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 8), padx=6, pady=2,
                            command=lambda url=p: self.set_website_preset(url))
            btn.pack(side="left", padx=(0, 5))
            


        # List Header Frame
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill="x", pady=(5, 5))
        
        self.list_header_lbl = ttk.Label(self.header_frame, text="Danh sách Profiles:", style="TLabel", font=("Segoe UI", 11, "bold"))
        self.list_header_lbl.pack(side="left", anchor="w")
        
        self.refresh_btn = ttk.Button(self.header_frame, text="⟳ Làm mới", style="Accent.TButton", width=12, command=self.refresh_profile_list)
        self.refresh_btn.pack(side="right", anchor="e")
        
        self.chrome_path_btn = ttk.Button(self.header_frame, text="⚙ Chrome", style="Normal.TButton", width=10, command=self.browse_chrome_path)
        self.chrome_path_btn.pack(side="right", anchor="e", padx=(0, 6))

        # Simultaneous Count Group (Label + Combobox)
        self.sim_header_frame = ttk.Frame(self.header_frame)
        self.sim_header_frame.pack(side="right", anchor="e", padx=(0, 10))
        
        self.sim_lbl = ttk.Label(self.sim_header_frame, text="Cùng lúc:", style="TLabel")
        self.sim_lbl.pack(side="left", padx=(0, 4))
        
        self.sim_combo = ttk.Combobox(self.sim_header_frame, textvariable=self.simultaneous_var, values=[2, 3, 4, 5, 6, 7, 8, 9], width=3, justify="center")
        self.sim_combo.pack(side="left")
        
        self.btn_open_new = ttk.Button(self.sim_header_frame, text="Mở profile mới", style="Normal.TButton", command=self.open_n_new_profiles)
        self.btn_open_new.pack(side="left", padx=(8, 0))
        
        # Scrollable List Frame (Treeview table)
        list_outer_frame = ttk.Frame(self.main_container, style="Card.TFrame")
        list_outer_frame.pack(fill="both", expand=True)
        
        self.profile_tree = ttk.Treeview(list_outer_frame, columns=("Directory", "Email", "Status"), show="headings", style="Treeview", selectmode="extended")
        self.profile_tree.heading("Directory", text="Thư mục Profile", command=lambda: self.sort_treeview(self.profile_tree, "Directory", False))
        self.profile_tree.heading("Email", text="Email / Tên", command=lambda: self.sort_treeview(self.profile_tree, "Email", False))
        self.profile_tree.heading("Status", text="Trạng thái", command=lambda: self.sort_treeview(self.profile_tree, "Status", False))
        self.profile_tree.column("Directory", width=200, anchor="w")
        self.profile_tree.column("Email", width=250, anchor="w")
        self.profile_tree.column("Status", width=120, anchor="center")
        
        self.profile_scroll = ttk.Scrollbar(list_outer_frame, orient="vertical", command=self.profile_tree.yview)
        self.profile_tree.configure(yscrollcommand=self.profile_scroll.set)
        
        self.profile_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.profile_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        # Bind selection change to update label
        self.profile_tree.bind("<<TreeviewSelect>>", self.on_profile_select_change)
        
        # Right-click Context Menu
        self.profile_context_menu = tk.Menu(self.profile_tree, tearoff=0, bg=self.card_color, fg=self.text_color, activebackground=self.accent_color, activeforeground="#ffffff")
        self.profile_context_menu.add_command(label="Mở các profile đã chọn", command=self.open_selected_profiles)
        self.profile_context_menu.add_separator()
        self.profile_context_menu.add_command(label="Xóa các profile đã chọn", command=self.delete_selected_profiles)
        self.profile_tree.bind("<Button-3>", self.show_profile_context_menu)
        self.profile_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.profile_tree.bind("<B1-Motion>", self.on_drag_motion)
        self.profile_tree.bind("<Double-1>", lambda e: self.open_selected_profiles())
        
        # Selection & Open Controls Bar
        self.profile_ctrl_frame = ttk.Frame(self.main_container)
        self.profile_ctrl_frame.pack(fill="x", pady=(10, 0))
        
        self.lbl_selected_count = ttk.Label(self.profile_ctrl_frame, text="Đã chọn: 0 / 0 profiles", font=("Segoe UI", 10, "italic"))
        self.btn_select_all = ttk.Button(self.profile_ctrl_frame, text="Chọn tất cả", style="Normal.TButton", command=self.select_all_profiles)
        self.btn_deselect = ttk.Button(self.profile_ctrl_frame, text="Bỏ chọn", style="Normal.TButton", command=self.deselect_all_profiles)
        
        self.select_n_frame = ttk.Frame(self.profile_ctrl_frame)
        self.lbl_select_n = ttk.Label(self.select_n_frame, text="Chọn:", style="TLabel")
        self.ent_select_n = tk.Entry(self.select_n_frame, textvariable=self.select_n_var, width=5, bg=self.bg_color, fg=self.text_color, 
                                     insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                     highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        self.lbl_select_n_suffix = ttk.Label(self.select_n_frame, text="dòng đầu", style="TLabel")
        self.btn_select_n = ttk.Button(self.select_n_frame, text="Chọn nhanh", style="Normal.TButton", command=self.select_first_n_profiles)
        
        self.btn_open_selected = tk.Button(self.profile_ctrl_frame, text="MỞ PROFILE ĐÃ CHỌN", bg="#28a745", fg="#ffffff", 
                                           activebackground="#218838", activeforeground="#ffffff", relief="flat", bd=0, 
                                           font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.open_selected_profiles)
        
        # ==========================================
        # TAB 2: Extension Manager UI Construction
        # ==========================================
        self.ext_pane = ttk.Frame(self.tab_extensions, padding=20)
        self.ext_pane.pack(fill="both", expand=True)
        
        # Header
        ext_header_lbl = ttk.Label(self.ext_pane, text="QUẢN LÝ CHROMIUM EXTENSIONS", style="Header.TLabel")
        ext_header_lbl.pack(pady=(0, 15), anchor="w")
        
        # Grid frame container to manage responsive layout of Treeview & Form
        self.ext_grid_frame = ttk.Frame(self.ext_pane)
        self.ext_grid_frame.pack(fill="both", expand=True)
        
        # Left/Top: Treeview Frame
        self.tree_frame = ttk.Frame(self.ext_grid_frame, style="Card.TFrame", padding=10)
        
        # Title of Tab 2 Table
        ttk.Label(self.tree_frame, text="Danh sách Extensions:", style="TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "ID"), show="headings", style="Treeview")
        self.tree.heading("Name", text="Tên Extension", command=lambda: self.sort_treeview(self.tree, "Name", False))
        self.tree.heading("ID", text="Extension ID", command=lambda: self.sort_treeview(self.tree, "ID", False))
        self.tree.column("Name", width=250, anchor="w")
        self.tree.column("ID", width=250, anchor="w")
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)
        
        # Right/Bottom: Form Frame
        self.form_frame = ttk.Frame(self.ext_grid_frame, style="Card.TFrame", padding=15)
        
        self.lbl_ext_name = ttk.Label(self.form_frame, text="Tên Extension:", style="Card.TLabel")
        self.ent_ext_name = tk.Entry(self.form_frame, textvariable=self.ext_name_var, bg=self.bg_color, fg=self.text_color, 
                                     insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                     highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10))
                                     
        self.lbl_ext_id = ttk.Label(self.form_frame, text="Extension ID:", style="Card.TLabel")
        self.ent_ext_id = tk.Entry(self.form_frame, textvariable=self.ext_id_var, bg=self.bg_color, fg=self.text_color, 
                                   insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                   highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10))
                                   
        self.btn_ext_add = ttk.Button(self.form_frame, text="Thêm Mới", style="Accent.TButton", command=self.add_extension)
        self.btn_ext_update = ttk.Button(self.form_frame, text="Cập Nhật", style="Normal.TButton", command=self.update_extension)
        self.btn_ext_delete = ttk.Button(self.form_frame, text="Xóa", style="Normal.TButton", command=self.delete_extension)
        self.btn_ext_import = ttk.Button(self.form_frame, text="Import CSV", style="Normal.TButton", command=self.import_extensions_csv)
        self.btn_ext_export = ttk.Button(self.form_frame, text="Export CSV", style="Normal.TButton", command=self.export_extensions_csv)
        self.btn_ext_save = tk.Button(self.form_frame, text="LƯU THAY ĐỔI SCRIPT", bg="#28a745", fg="#ffffff", activebackground="#218838", activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 10, "bold"), command=self.save_extensions_to_bat)
        self.btn_ext_run = tk.Button(self.form_frame, text="CHẠY SCRIPT (ADMIN)", bg=self.accent_color, fg="#ffffff", activebackground=self.accent_hover, activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 10, "bold"), command=self.run_extension_script)
        
        # Populate initial treeview list
        self.populate_treeview()
        
        # Bind root resize to responsive adjustment
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Initialize default responsive layout
        self.apply_responsive_layout(narrow=False)
        
        # Generate list automatically on startup
        self.refresh_profile_list()

    def on_window_resize(self, event):
        if event.widget == self.root:
            is_narrow = event.width < 580
            if self.narrow_mode != is_narrow:
                self.narrow_mode = is_narrow
                self.apply_responsive_layout(narrow=is_narrow)

    def apply_responsive_layout(self, narrow):
        # Clean up Tab 1 configuration card grid settings
        for widget in [self.web_lbl, self.web_entry, self.preset_frame]:
            widget.grid_forget()
        
        # Clean up Tab 1 selection controls
        for widget in [self.lbl_selected_count, self.btn_select_all, self.btn_deselect, self.select_n_frame, self.btn_open_selected]:
            widget.pack_forget()
        for widget in [self.lbl_select_n, self.ent_select_n, self.lbl_select_n_suffix, self.btn_select_n]:
            widget.pack_forget()
        
        # Clean up Tab 2 layouts
        self.tree_frame.pack_forget()
        self.form_frame.pack_forget()
        self.tree.pack_forget()
        self.tree_scroll.pack_forget()
        for widget in [self.lbl_ext_name, self.ent_ext_name, self.lbl_ext_id, self.ent_ext_id, self.btn_ext_add, self.btn_ext_update, self.btn_ext_delete, self.btn_ext_import, self.btn_ext_export, self.btn_ext_save, self.btn_ext_run]:
            widget.grid_forget()

        if narrow:
            # ==========================================
            # TAB 1: Narrow Layout
            # ==========================================
            self.web_lbl.grid(row=0, column=0, columnspan=3, sticky="w", pady=(5, 2))
            self.web_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 5))
            self.preset_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 8))
            
            self.config_card.columnconfigure(0, weight=1)
            self.config_card.columnconfigure(1, weight=1)
            self.config_card.columnconfigure(2, weight=0)

            
            # Narrow selection controls
            self.lbl_selected_count.pack(side="top", anchor="w", pady=(0, 5))
            self.select_n_frame.pack(side="top", fill="x", pady=5)
            self.lbl_select_n.pack(side="left")
            self.ent_select_n.pack(side="left", padx=5)
            self.lbl_select_n_suffix.pack(side="left")
            self.btn_select_n.pack(side="left", padx=5)
            
            self.btn_select_all.pack(side="top", fill="x", pady=2)
            self.btn_deselect.pack(side="top", fill="x", pady=2)
            self.btn_open_selected.pack(side="top", fill="x", pady=(8, 0))
            
            # ==========================================
            # TAB 2: Narrow Layout
            # ==========================================
            self.tree_frame.pack(side="top", fill="both", expand=True, pady=(0, 10))
            self.form_frame.pack(side="top", fill="x", expand=False)
            
            self.tree.pack(side="left", fill="both", expand=True)
            self.tree_scroll.pack(side="right", fill="y")
            
            self.lbl_ext_name.grid(row=0, column=0, sticky="w", pady=2)
            self.ent_ext_name.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 8))
            self.lbl_ext_id.grid(row=2, column=0, sticky="w", pady=2)
            self.ent_ext_id.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(2, 8))
            
            self.btn_ext_add.grid(row=4, column=0, sticky="ew", padx=(0, 2), pady=5)
            self.btn_ext_update.grid(row=4, column=1, sticky="ew", padx=2, pady=5)
            self.btn_ext_delete.grid(row=4, column=2, sticky="ew", padx=(2, 0), pady=5)
            
            self.btn_ext_import.grid(row=5, column=0, sticky="ew", padx=(0, 2), pady=5)
            self.btn_ext_export.grid(row=5, column=1, columnspan=2, sticky="ew", padx=(2, 0), pady=5)
            
            self.btn_ext_save.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5)
            self.btn_ext_run.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5)
            
            self.form_frame.columnconfigure(0, weight=1)
            self.form_frame.columnconfigure(1, weight=1)
            self.form_frame.columnconfigure(2, weight=1)
        else:
            # ==========================================
            # TAB 1: Wide Layout
            # ==========================================
            self.web_lbl.grid(row=0, column=0, sticky="w", pady=5)
            self.web_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))
            self.preset_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=(2, 8), padx=(10, 0))
            
            self.config_card.columnconfigure(0, weight=0)
            self.config_card.columnconfigure(1, weight=1)
            self.config_card.columnconfigure(2, weight=0)


            
            # Wide selection controls
            self.lbl_selected_count.pack(side="left", padx=(0, 15))
            self.btn_select_all.pack(side="left", padx=5)
            self.btn_deselect.pack(side="left", padx=5)
            
            self.select_n_frame.pack(side="left", padx=15)
            self.lbl_select_n.pack(side="left")
            self.ent_select_n.pack(side="left", padx=5)
            self.lbl_select_n_suffix.pack(side="left")
            self.btn_select_n.pack(side="left", padx=5)
            
            self.btn_open_selected.pack(side="right", padx=(10, 0))
            
            # ==========================================
            # TAB 2: Wide Layout
            # ==========================================
            self.tree_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.form_frame.pack(side="right", fill="both", expand=False)
            
            self.tree.pack(side="left", fill="both", expand=True)
            self.tree_scroll.pack(side="right", fill="y")
            
            self.lbl_ext_name.grid(row=0, column=0, sticky="w", pady=2)
            self.ent_ext_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 10))
            self.lbl_ext_id.grid(row=2, column=0, sticky="w", pady=2)
            self.ent_ext_id.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 15))
            
            self.btn_ext_add.grid(row=4, column=0, sticky="ew", padx=(0, 2), pady=5)
            self.btn_ext_update.grid(row=4, column=1, sticky="ew", padx=(2, 0), pady=5)
            self.btn_ext_delete.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
            
            self.btn_ext_import.grid(row=6, column=0, sticky="ew", padx=(0, 2), pady=5)
            self.btn_ext_export.grid(row=6, column=1, sticky="ew", padx=(2, 0), pady=5)
            
            self.btn_ext_save.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(15, 5))
            self.btn_ext_run.grid(row=8, column=0, columnspan=2, sticky="ew", pady=5)
            
            self.form_frame.columnconfigure(0, weight=1)
            self.form_frame.columnconfigure(1, weight=1)
            self.form_frame.columnconfigure(2, weight=0)

    # ==========================================
    # EXTENSIONS CRUD METHODS
    # ==========================================
    def populate_treeview(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Populate
        for ext in self.extensions:
            self.tree.insert("", "end", values=(ext["name"], ext["id"]))
            
    def on_treeview_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, "values")
            self.ext_name_var.set(values[0])
            self.ext_id_var.set(values[1])
            # Find index in list
            for idx, ext in enumerate(self.extensions):
                if ext["id"] == values[1]:
                    self.selected_ext_idx = idx
                    break
        else:
            self.selected_ext_idx = None
            
    def add_extension(self):
        name = self.ext_name_var.get().strip()
        ext_id = self.ext_id_var.get().strip()
        if not name or not ext_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ Tên và ID Extension.")
            return
            
        # Check if ID already exists
        if any(ext["id"] == ext_id for ext in self.extensions):
            messagebox.showwarning("Cảnh báo", f"Extension ID '{ext_id}' đã tồn tại.")
            return
            
        self.extensions.append({"name": name, "id": ext_id})
        self.populate_treeview()
        self.clear_ext_fields()
        
    def update_extension(self):
        if self.selected_ext_idx is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn Extension từ bảng để cập nhật.")
            return
            
        name = self.ext_name_var.get().strip()
        ext_id = self.ext_id_var.get().strip()
        if not name or not ext_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ Tên và ID Extension.")
            return
            
        # Update
        self.extensions[self.selected_ext_idx] = {"name": name, "id": ext_id}
        self.populate_treeview()
        self.clear_ext_fields()
        
    def delete_extension(self):
        if self.selected_ext_idx is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn Extension từ bảng để xóa.")
            return
            
        del self.extensions[self.selected_ext_idx]
        self.populate_treeview()
        self.clear_ext_fields()
        
    def clear_ext_fields(self):
        self.ext_name_var.set("")
        self.ext_id_var.set("")
        self.selected_ext_idx = None
        self.tree.selection_remove(self.tree.selection())

    def load_extensions_from_bat(self):
        self.extensions = []
        self.bat_header = []
        self.bat_footer = []
        
        if not os.path.exists(BAT_FILE_PATH):
            return
            
        try:
            with open(BAT_FILE_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(lines):
                if 'set "EXT_LIST="' in line:
                    start_idx = i
                elif 'set /a count=1' in line:
                    end_idx = i
                    break
                    
            if start_idx != -1 and end_idx != -1:
                self.bat_header = lines[:start_idx + 1]
                self.bat_footer = lines[end_idx:]
                
                import re
                for line in lines[start_idx + 1 : end_idx]:
                    line_str = line.strip()
                    if not line_str:
                        continue
                    if line_str.startswith("echo ") and " & set " in line_str:
                        parts = line_str.split(" & set ")
                        name = parts[0][5:] # Strip "echo "
                        id_part = parts[1]
                        m_id = re.search(r'!EXT_LIST!\s+([a-zA-Z0-9]+)"', id_part)
                        if m_id:
                            ext_id = m_id.group(1)
                            self.extensions.append({"name": name, "id": ext_id})
            else:
                self.bat_footer = lines
        except Exception as e:
            print(f"Error loading extensions: {e}")

    def save_extensions_to_bat(self):
        try:
            os.makedirs(os.path.dirname(BAT_FILE_PATH), exist_ok=True)
            with open(BAT_FILE_PATH, "w", encoding="utf-8") as f:
                # Write header
                f.writelines(self.bat_header)
                
                # Write extensions
                f.write("\n")
                for ext in self.extensions:
                    f.write(f'echo {ext["name"]} & set "EXT_LIST=!EXT_LIST! {ext["id"]}"\n')
                f.write("\n\n")
                
                # Write footer
                f.writelines(self.bat_footer)
            messagebox.showinfo("Thành công", "Đã lưu thay đổi vào file script .bat thành công.")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
            return False

    def run_extension_script(self):
        if not os.path.exists(BAT_FILE_PATH):
            messagebox.showerror("Lỗi", "Không tìm thấy file script .bat")
            return
        try:
            # Execute the bat file with Administrator privileges using powershell
            cmd = f'Start-Process -FilePath "{BAT_FILE_PATH}" -Verb RunAs'
            subprocess.Popen(["powershell", "-Command", cmd], shell=True)
            messagebox.showinfo("Thành công", "Đang chạy script cài đặt Extension với quyền Administrator.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chạy script: {e}")

    def import_extensions_csv(self):
        file_path = filedialog.askopenfilename(
            title="Import CSV Extensions",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            imported_exts = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            if not rows:
                messagebox.showwarning("Cảnh báo", "File CSV trống.")
                return
                
            # Skip header row if it contains header keywords
            start_row = 0
            first_row = rows[0]
            if len(first_row) >= 2:
                # If first row has labels like 'name', 'id', 'tên', etc.
                val0_lower = first_row[0].lower()
                val1_lower = first_row[1].lower()
                if "name" in val0_lower or "tên" in val0_lower or "id" in val1_lower:
                    start_row = 1
                    
            for row in rows[start_row:]:
                if not row or len(row) < 2:
                    continue
                name = row[0].strip()
                ext_id = row[1].strip()
                if name and ext_id:
                    imported_exts.append({"name": name, "id": ext_id})
                    
            if not imported_exts:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu Extension hợp lệ trong file CSV.")
                return
                
            # Ask to append or replace
            ans = messagebox.askyesnocancel(
                "Import CSV",
                "Bạn có muốn giữ lại danh sách Extension hiện tại không?\n\n- Chọn 'Yes' để Thêm/Gộp dữ liệu.\n- Chọn 'No' để Thay thế toàn bộ."
            )
            
            if ans is None:
                return # User cancelled
                
            if ans:
                # Append: Only add if ID doesn't already exist
                appended_count = 0
                for ext in imported_exts:
                    if not any(existing["id"] == ext["id"] for existing in self.extensions):
                        self.extensions.append(ext)
                        appended_count += 1
                messagebox.showinfo("Thành công", f"Đã gộp thêm {appended_count} Extensions mới từ file CSV.")
            else:
                # Replace
                self.extensions = imported_exts
                messagebox.showinfo("Thành công", f"Đã thay thế toàn bộ danh sách bằng {len(imported_exts)} Extensions từ file CSV.")
                
            self.populate_treeview()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể import file CSV: {e}")

    def export_extensions_csv(self):
        if not self.extensions:
            messagebox.showwarning("Cảnh báo", "Danh sách Extension trống, không thể export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export CSV Extensions",
            initialfile="chrome_extension.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "ID"])
                for ext in self.extensions:
                    writer.writerow([ext["name"], ext["id"]])
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu ra file CSV thành công:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể export file CSV: {e}")



    def _on_canvas_configure(self, event):
        # Match the width of the scrollable frame to the canvas width
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def set_website_preset(self, domain):
        url = f"https://{domain}"
        self.website_var.set(url)

    def browse_chrome_path(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file Chrome.exe",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.chrome_path_var.set(file_path)
            self.save_config()

    def get_actual_profiles(self):
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        profiles_list = []
        if not os.path.exists(user_data_path):
            return []
            
        for entry in os.scandir(user_data_path):
            if entry.is_dir():
                if entry.name.lower() in ("system profile", "guest profile"):
                    continue
                pref_path = os.path.join(entry.path, "Preferences")
                if os.path.exists(pref_path):
                    email = ""
                    name = ""
                    try:
                        with open(pref_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            profile = data.get("profile", {})
                            name = profile.get("name", "")
                            email = profile.get("google_services_username", "")
                            if not email:
                                account_info = data.get("account_info", [])
                                if account_info and isinstance(account_info, list):
                                    email = account_info[0].get("email", "")
                            if not email:
                                account_info = profile.get("account_info", [])
                                if account_info and isinstance(account_info, list):
                                    email = account_info[0].get("email", "")
                            if not email:
                                google = data.get("google", {})
                                services = google.get("services", {})
                                email = services.get("username", "")
                    except Exception:
                        pass
                    
                    profiles_list.append({
                        "dir": entry.name,
                        "name": name or entry.name,
                        "email": email or "-"
                    })
        
        # Sort profiles naturally by directory name
        import re
        def natural_sort_key(item):
            s = item["dir"]
            if s.lower() == "default":
                return [0, ""]
            return [1] + [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
        profiles_list.sort(key=natural_sort_key)
        return profiles_list

    def refresh_profile_list(self, from_debounce=False):
        self.save_config()
        
        # 1. Scan actual profiles on the machine
        actual_profiles = self.get_actual_profiles()
        
        # 2. Sort naturally by directory name
        import re
        def natural_sort_key(item):
            s = item["dir"]
            if s.lower() == "default":
                return [0, ""]
            return [1] + [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
        actual_profiles.sort(key=natural_sort_key)
        
        # 3. Clear treeview and populate
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
            
        for p in actual_profiles:
            self.profile_tree.insert("", "end", values=(p["dir"], p["email"], "Sẵn sàng"))
            
        self.update_profile_selected_count_label()

    def on_profile_select_change(self, event):
        self.update_profile_selected_count_label()
        
    def update_profile_selected_count_label(self):
        total = len(self.profile_tree.get_children())
        selected = len(self.profile_tree.selection())
        self.lbl_selected_count.config(text=f"Đã chọn: {selected} / {total} profiles")

    def select_all_profiles(self):
        self.profile_tree.selection_set(self.profile_tree.get_children())
        self.update_profile_selected_count_label()
        
    def deselect_all_profiles(self):
        self.profile_tree.selection_remove(self.profile_tree.get_children())
        self.update_profile_selected_count_label()
        
    def select_first_n_profiles(self):
        try:
            n = self.select_n_var.get()
            if n <= 0:
                raise ValueError()
        except (tk.TclError, ValueError):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập số lượng nguyên dương hợp lệ.")
            return
            
        children = self.profile_tree.get_children()
        to_select = children[:n]
        self.profile_tree.selection_remove(children)
        self.profile_tree.selection_set(to_select)
        self.update_profile_selected_count_label()

    def open_selected_profiles(self):
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile trong bảng.")
            return
            
        chrome_path = self.chrome_path_var.get()
        website = self.website_var.get()
        
        if not (website.startswith("http://") or website.startswith("https://")):
            website = "https://" + website
            
        if not os.path.exists(chrome_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file Chrome tại: {chrome_path}\nVui lòng kiểm tra lại đường dẫn.")
            return
            
        opened_count = 0
        for item in selected_items:
            values = self.profile_tree.item(item, "values")
            dir_name = values[0]
            if dir_name == "Không có profile nào":
                continue
            try:
                subprocess.Popen([chrome_path, f"--profile-directory={dir_name}", website])
                opened_count += 1
                time.sleep(0.3) # Mild delay to prevent CPU spike
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở Profile {dir_name}: {e}")
                break
                
        print(f"Đã mở {opened_count} profiles đã chọn.")

    def show_profile_context_menu(self, event):
        item_under_mouse = self.profile_tree.identify_row(event.y)
        if item_under_mouse:
            current_selection = self.profile_tree.selection()
            if item_under_mouse not in current_selection:
                self.profile_tree.selection_set(item_under_mouse)
                self.update_profile_selected_count_label()
                
            try:
                self.profile_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.profile_context_menu.grab_release()

    def sort_treeview(self, treeview, col, reverse):
        items = [(treeview.set(item_id, col), item_id) for item_id in treeview.get_children("")]
        
        import re
        def natural_sort_key(item_tuple):
            val = item_tuple[0]
            if val.lower() == "default":
                return [0, ""]
            return [1] + [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', val)]
            
        items.sort(key=natural_sort_key, reverse=reverse)
        
        for index, (_, item_id) in enumerate(items):
            treeview.move(item_id, "", index)
            
        treeview.heading(col, command=lambda c=col: self.sort_treeview(treeview, c, not reverse))

    def on_drag_start(self, event):
        item = self.profile_tree.identify_row(event.y)
        if item:
            self.drag_start_item = item

    def on_drag_motion(self, event):
        item = self.profile_tree.identify_row(event.y)
        if item and hasattr(self, 'drag_start_item') and self.drag_start_item:
            children = list(self.profile_tree.get_children(""))
            try:
                start_idx = children.index(self.drag_start_item)
                end_idx = children.index(item)
                
                low = min(start_idx, end_idx)
                high = max(start_idx, end_idx)
                
                to_select = children[low:high+1]
                self.profile_tree.selection_set(to_select)
                self.update_profile_selected_count_label()
            except ValueError:
                pass

    def delete_selected_profiles(self):
        selected_items = self.profile_tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một profile để xóa.")
            return
            
        dirs_to_delete = []
        for item in selected_items:
            values = self.profile_tree.item(item, "values")
            dir_name = values[0]
            if dir_name == "Không có profile nào":
                continue
            dirs_to_delete.append(dir_name)
            
        if not dirs_to_delete:
            return
            
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa vĩnh viễn {len(dirs_to_delete)} profile đã chọn khỏi máy tính?\n\n"
            "Cảnh báo: Hành động này sẽ xóa toàn bộ dữ liệu duyệt web, tài khoản của các profile này và KHÔNG THỂ HOÀN TÁC."
        )
        if not confirm:
            return
            
        import shutil
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        
        deleted_count = 0
        failed_dirs = []
        for d in dirs_to_delete:
            path = os.path.join(user_data_path, d)
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    deleted_count += 1
                except Exception as e:
                    failed_dirs.append(f"{d} (Lỗi: {e})")
                    
        if failed_dirs:
            err_msg = "\n".join(failed_dirs)
            messagebox.showwarning(
                "Hoàn thành một phần",
                f"Đã xóa thành công {deleted_count} profile.\n\n"
                f"Không thể xóa các profile sau (vui lòng tắt Chrome trước khi xóa):\n{err_msg}"
            )
        else:
            messagebox.showinfo("Thành công", f"Đã xóa thành công {deleted_count} profile khỏi máy tính.")
            
        self.refresh_profile_list()

    def open_n_new_profiles(self):
        try:
            n = self.simultaneous_var.get()
            if n <= 0:
                raise ValueError()
        except (tk.TclError, ValueError):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn số lượng luồng cùng lúc hợp lệ.")
            return
            
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        existing_nums = []
        if os.path.exists(user_data_path):
            import re
            for entry in os.scandir(user_data_path):
                if entry.is_dir():
                    match = re.match(r"^Profile (\d+)$", entry.name, re.IGNORECASE)
                    if match:
                        existing_nums.append(int(match.group(1)))
                        
        max_num = max(existing_nums) if existing_nums else 0
        new_dirs = [f"Profile {max_num + i}" for i in range(1, n + 1)]
        
        chrome_path = self.chrome_path_var.get()
        website = self.website_var.get()
        if not (website.startswith("http://") or website.startswith("https://")):
            website = "https://" + website
            
        if not os.path.exists(chrome_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file Chrome tại: {chrome_path}\nVui lòng kiểm tra lại đường dẫn.")
            return
            
        opened_count = 0
        for dir_name in new_dirs:
            try:
                subprocess.Popen([chrome_path, f"--profile-directory={dir_name}", website])
                opened_count += 1
                time.sleep(0.3)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở Profile {dir_name}: {e}")
                break
                
        messagebox.showinfo("Thành công", f"Đã khởi chạy {opened_count} profiles mới: {', '.join(new_dirs)}")
        self.root.after(1000, self.refresh_profile_list)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChromeProfileManagerApp(root)
    root.mainloop()
