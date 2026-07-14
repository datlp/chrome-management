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
        self.start_profile_var = tk.IntVar(value=1)
        self.end_profile_var = tk.IntVar(value=180)
        self.simultaneous_var = tk.IntVar(value=5)
        self.chrome_path_var = tk.StringVar(value=DEFAULT_CHROME_PATH)
        
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
        self.start_profile_var.trace_add("write", self.on_config_change)
        self.end_profile_var.trace_add("write", self.on_config_change)
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
        if self.current_mode == "actual":
            self.generate_actual_profile_list(from_debounce=True)
        else:
            self.generate_profile_list(from_debounce=True)

    def load_config(self):
        self.is_loading_config = True
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.website_var.set(config.get("website", "https://google.com"))
                    self.start_profile_var.set(config.get("start_profile", 1))
                    self.end_profile_var.set(config.get("end_profile", 180))
                    self.simultaneous_var.set(config.get("simultaneous", 5))
                    self.chrome_path_var.set(config.get("chrome_path", DEFAULT_CHROME_PATH))
            except Exception as e:
                print(f"Error loading config: {e}")
        self.is_loading_config = False

    def save_config(self):
        config = {
            "website": self.website_var.get(),
            "start_profile": self.start_profile_var.get(),
            "end_profile": self.end_profile_var.get(),
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
            
        # Range Frame
        self.range_frame = ttk.Frame(self.config_card, style="Card.TFrame")
        self.range_lbl1 = ttk.Label(self.range_frame, text="Profile bắt đầu:", style="Card.TLabel")
        self.start_entry = tk.Entry(self.range_frame, textvariable=self.start_profile_var, width=6, bg=self.bg_color, fg=self.text_color, 
                               insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                               highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        self.range_lbl2 = ttk.Label(self.range_frame, text="Profile kết thúc:", style="Card.TLabel")
        self.end_entry = tk.Entry(self.range_frame, textvariable=self.end_profile_var, width=6, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")

        # Sim count Frame
        self.sim_frame = ttk.Frame(self.config_card, style="Card.TFrame")
        self.sim_lbl = ttk.Label(self.sim_frame, text="Số lượng cùng lúc:", style="Card.TLabel")
        self.sim_entry = tk.Entry(self.sim_frame, textvariable=self.simultaneous_var, width=6, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        self.sim_preset_lbl = ttk.Label(self.sim_frame, text="Mặc định:", style="Card.TLabel")
        self.sim_preset_buttons_frame = ttk.Frame(self.sim_frame, style="Card.TFrame")
        for num in [2, 4, 6, 8, 10, 12]:
            btn = tk.Button(self.sim_preset_buttons_frame, text=str(num), bg=self.border_color, fg=self.text_muted, activebackground=self.accent_color,
                            activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 8, "bold"), padx=8, pady=2,
                            command=lambda n=num: self.simultaneous_var.set(n))
            btn.pack(side="left", padx=(0, 4))
        
        # Chrome path selection
        self.chrome_lbl = ttk.Label(self.config_card, text="Đường dẫn Chrome:", style="Card.TLabel")
        self.chrome_entry = tk.Entry(self.config_card, textvariable=self.chrome_path_var, bg=self.bg_color, fg=self.text_color, 
                                insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 9))
        self.browse_btn = ttk.Button(self.config_card, text="Chọn file", style="Normal.TButton", command=self.browse_chrome_path)
        
        # Generate Action Buttons Frame
        self.action_btn_frame = ttk.Frame(self.main_container)
        self.action_btn_frame.pack(fill="x", pady=(0, 15))
        
        self.gen_btn = ttk.Button(self.action_btn_frame, text="TẠO NHÓM THEO SỐ THỨ TỰ", style="Accent.TButton", command=self.generate_profile_list)
        self.scan_btn = ttk.Button(self.action_btn_frame, text="QUÉT PROFILE THỰC TẾ (CÓ EMAIL)", style="Accent.TButton", command=self.generate_actual_profile_list)
        
        # List Container Header
        ttk.Label(self.main_container, text="Danh sách nhóm Profile:", style="TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(5, 5))
        
        # Scrollable List Frame
        list_outer_frame = ttk.Frame(self.main_container, style="Card.TFrame")
        list_outer_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(list_outer_frame, bg=self.card_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mousewheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
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
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "ID"), show="headings", style="Treeview")
        self.tree.heading("Name", text="Tên Extension")
        self.tree.heading("ID", text="Extension ID")
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
        self.generate_profile_list()

    def on_window_resize(self, event):
        if event.widget == self.root:
            is_narrow = event.width < 580
            if self.narrow_mode != is_narrow:
                self.narrow_mode = is_narrow
                self.apply_responsive_layout(narrow=is_narrow)

    def apply_responsive_layout(self, narrow):
        # Clean up Tab 1 configuration card grid settings
        for widget in [self.web_lbl, self.web_entry, self.preset_frame, self.range_frame, self.sim_frame, self.chrome_lbl, self.chrome_entry, self.browse_btn]:
            widget.grid_forget()
        for widget in [self.range_lbl1, self.start_entry, self.range_lbl2, self.end_entry]:
            widget.grid_forget()
        for widget in [self.sim_lbl, self.sim_entry, self.sim_preset_lbl, self.sim_preset_buttons_frame]:
            widget.grid_forget()
        
        self.gen_btn.pack_forget()
        self.scan_btn.pack_forget()
        
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
            self.range_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
            self.sim_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
            self.chrome_lbl.grid(row=5, column=0, columnspan=3, sticky="w", pady=(8, 2))
            self.chrome_entry.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(2, 8), padx=(0, 5))
            self.browse_btn.grid(row=6, column=2, sticky="e", pady=(2, 8))
            
            self.config_card.columnconfigure(0, weight=1)
            self.config_card.columnconfigure(1, weight=1)
            self.config_card.columnconfigure(2, weight=0)

            # Narrow Range frame grid
            self.range_lbl1.grid(row=0, column=0, sticky="w", pady=2)
            self.start_entry.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)
            self.range_lbl2.grid(row=1, column=0, sticky="w", pady=2)
            self.end_entry.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)

            # Narrow Sim frame grid
            self.sim_lbl.grid(row=0, column=0, sticky="w", pady=2)
            self.sim_entry.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)
            self.sim_preset_lbl.grid(row=1, column=0, sticky="w", pady=2)
            self.sim_preset_buttons_frame.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)

            # Narrow action buttons stack
            self.gen_btn.pack(side="top", fill="x", pady=(0, 5))
            self.scan_btn.pack(side="top", fill="x", pady=(5, 0))
            
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
            self.range_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
            self.sim_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
            self.chrome_lbl.grid(row=4, column=0, sticky="w", pady=8)
            self.chrome_entry.grid(row=4, column=1, sticky="ew", pady=8, padx=(10, 5))
            self.browse_btn.grid(row=4, column=2, sticky="e", pady=8)
            
            self.config_card.columnconfigure(0, weight=0)
            self.config_card.columnconfigure(1, weight=1)
            self.config_card.columnconfigure(2, weight=0)

            # Wide Range frame grid
            self.range_lbl1.grid(row=0, column=0, sticky="w")
            self.start_entry.grid(row=0, column=1, sticky="w", padx=(5, 15))
            self.range_lbl2.grid(row=0, column=2, sticky="w")
            self.end_entry.grid(row=0, column=3, sticky="w", padx=(5, 15))

            # Wide Sim frame grid
            self.sim_lbl.grid(row=0, column=0, sticky="w")
            self.sim_entry.grid(row=0, column=1, sticky="w", padx=(5, 15))
            self.sim_preset_lbl.grid(row=0, column=2, sticky="w")
            self.sim_preset_buttons_frame.grid(row=0, column=3, sticky="w", padx=(5, 0))

            # Wide action buttons side-by-side
            self.gen_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.scan_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
            
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

    def get_actual_profiles(self):
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        profiles_list = []
        if not os.path.exists(user_data_path):
            return []
            
        for entry in os.scandir(user_data_path):
            if entry.is_dir():
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
                    
                    if email:
                        profiles_list.append({
                            "dir": entry.name,
                            "name": name or entry.name,
                            "email": email
                        })
        
        # Sort profiles naturally by directory name
        import re
        def natural_sort_key(item):
            s = item["dir"]
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
        profiles_list.sort(key=natural_sort_key)
        return profiles_list

    def generate_actual_profile_list(self, from_debounce=False):
        self.current_mode = "actual"
        try:
            simultaneous = self.simultaneous_var.get()
            if simultaneous <= 0:
                raise ValueError()
        except (tk.TclError, ValueError):
            if not from_debounce:
                messagebox.showerror("Lỗi", "Số lượng cùng lúc phải lớn hơn 0.")
            return
            
        self.save_config()
        
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        profiles = self.get_actual_profiles()
        if not profiles:
            no_lbl = tk.Label(self.scrollable_frame, text="Không tìm thấy Chrome Profile nào đã đăng nhập email.", bg=self.card_color, fg=self.text_muted, font=("Segoe UI", 10, "italic"))
            no_lbl.pack(pady=20)
            return
            
        current_idx = 0
        total_profiles = len(profiles)
        row_idx = 0
        
        while current_idx < total_profiles:
            group = profiles[current_idx : current_idx + simultaneous]
            
            # Create a row frame for each item
            row_frame = tk.Frame(self.scrollable_frame, bg=self.card_color, highlightbackground=self.border_color, 
                                 highlightcolor=self.accent_color, highlightthickness=1)
            row_frame.pack(fill="x", pady=4, padx=5)
            
            dir_names = [p["dir"] for p in group]
            
            # Horizontal scrollable canvas for chips
            chips_canvas = tk.Canvas(row_frame, bg=self.card_color, highlightthickness=0, height=56)
            
            # Left arrow button
            left_btn = tk.Button(
                row_frame,
                text=" ‹ ",
                bg=self.card_color,
                fg=self.text_muted,
                activebackground=self.border_color,
                activeforeground=self.accent_color,
                relief="flat",
                bd=0,
                font=("Segoe UI", 14, "bold"),
                command=lambda canvas=chips_canvas: canvas.xview_scroll(-1, "pages")
            )
            
            # Right arrow button
            right_btn = tk.Button(
                row_frame,
                text=" › ",
                bg=self.card_color,
                fg=self.text_muted,
                activebackground=self.border_color,
                activeforeground=self.accent_color,
                relief="flat",
                bd=0,
                font=("Segoe UI", 14, "bold"),
                command=lambda canvas=chips_canvas: canvas.xview_scroll(1, "pages")
            )
            
            # Hover effects
            def on_enter(e):
                e.widget.config(fg=self.accent_color)
            def on_leave(e):
                e.widget.config(fg=self.text_muted)
                
            left_btn.bind("<Enter>", on_enter)
            left_btn.bind("<Leave>", on_leave)
            right_btn.bind("<Enter>", on_enter)
            right_btn.bind("<Leave>", on_leave)
            
            chips_inner = tk.Frame(chips_canvas, bg=self.card_color)
            canvas_win = chips_canvas.create_window((0, 0), window=chips_inner, anchor="nw")
            
            # Adjust canvas height and scroll region
            def _on_inner_configure(e, canvas=chips_canvas, inner=chips_inner):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.configure(height=inner.winfo_reqheight())

            chips_inner.bind("<Configure>", _on_inner_configure)
            
            # Bind horizontal scroll to mousewheel on canvas
            scroll_func = lambda e, canvas=chips_canvas: canvas.xview_scroll(int(-1*(e.delta/120)), "units")
            chips_canvas.bind("<MouseWheel>", scroll_func)
            chips_inner.bind("<MouseWheel>", scroll_func)
            
            for p in group:
                chip = tk.Frame(chips_inner, bg="#25282e", highlightbackground=self.border_color, highlightthickness=1)
                chip.pack(side="left", padx=4, pady=3)
                
                # Title: Email
                email_lbl = tk.Label(chip, text=p["email"] or "No Email", bg="#25282e", fg=self.text_color, font=("Segoe UI", 9, "bold"), anchor="center")
                email_lbl.pack(fill="x", padx=10, pady=(4, 1))
                
                # Subtitle: Profile directory
                sub_lbl = tk.Label(chip, text=p["dir"], bg="#25282e", fg=self.accent_color, font=("Segoe UI", 8, "italic"), anchor="center")
                sub_lbl.pack(fill="x", padx=10, pady=(1, 4))
                
                # Bind scroll to all elements in the chip
                chip.bind("<MouseWheel>", scroll_func)
                email_lbl.bind("<MouseWheel>", scroll_func)
                sub_lbl.bind("<MouseWheel>", scroll_func)
            
            open_btn = tk.Button(
                row_frame, 
                text="Mở Nhóm này", 
                bg="#28a745", 
                fg="#ffffff", 
                activebackground="#218838",
                activeforeground="#ffffff",
                relief="flat", 
                bd=0, 
                font=("Segoe UI", 9, "bold"), 
                padx=15, 
                pady=6,
                command=lambda dirs=dir_names: self.open_profile_dirs(dirs)
            )
            
            # Responsive configuration for actual rows
            def make_actual_row_responsive(event, l=left_btn, c=chips_canvas, r=right_btn, b=open_btn):
                if event.width < 500:
                    l.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=5)
                    c.grid(row=0, column=1, sticky="ew", padx=2, pady=5)
                    r.grid(row=0, column=2, sticky="e", padx=(0, 5), pady=5)
                    b.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=(2, 8))
                    event.widget.columnconfigure(0, weight=0)
                    event.widget.columnconfigure(1, weight=1)
                    event.widget.columnconfigure(2, weight=0)
                    event.widget.columnconfigure(3, weight=0)
                else:
                    l.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=5)
                    c.grid(row=0, column=1, sticky="ew", padx=2, pady=5)
                    r.grid(row=0, column=2, sticky="e", padx=(0, 5), pady=5)
                    b.grid(row=0, column=3, sticky="e", padx=10, pady=5)
                    event.widget.columnconfigure(0, weight=0)
                    event.widget.columnconfigure(1, weight=1)
                    event.widget.columnconfigure(2, weight=0)
                    event.widget.columnconfigure(3, weight=0)

            row_frame.bind("<Configure>", make_actual_row_responsive)
            
            current_idx += simultaneous
            row_idx += 1

    def open_profile_dirs(self, dir_names):
        chrome_path = self.chrome_path_var.get()
        website = self.website_var.get()
        
        if not (website.startswith("http://") or website.startswith("https://")):
            website = "https://" + website
            
        if not os.path.exists(chrome_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file Chrome tại: {chrome_path}\nVui lòng kiểm tra lại đường dẫn.")
            return
 
        opened_count = 0
        for d in dir_names:
            try:
                subprocess.Popen([chrome_path, f"--profile-directory={d}", website])
                opened_count += 1
                time.sleep(0.3)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở Profile {d}: {e}")
                break
                
        print(f"Đã mở {opened_count} profiles thực tế: {', '.join(dir_names)}")

    def generate_profile_list(self, from_debounce=False):
        self.current_mode = "sequential"
        try:
            start = self.start_profile_var.get()
            end = self.end_profile_var.get()
            simultaneous = self.simultaneous_var.get()
            if start <= 0 or end <= 0 or simultaneous <= 0 or start > end:
                raise ValueError()
        except (tk.TclError, ValueError):
            if not from_debounce:
                try:
                    s = self.start_profile_var.get()
                    e = self.end_profile_var.get()
                    sim = self.simultaneous_var.get()
                    if s <= 0 or e <= 0 or sim <= 0:
                        messagebox.showerror("Lỗi", "Vui lòng nhập các giá trị số nguyên dương lớn hơn 0.")
                    elif s > e:
                        messagebox.showerror("Lỗi", "Profile bắt đầu không thể lớn hơn Profile kết thúc.")
                except tk.TclError:
                    messagebox.showerror("Lỗi", "Vui lòng nhập các giá trị số nguyên hợp lệ.")
            return
            
        # Save current config
        self.save_config()
        
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Group profiles
        current = start
        row_idx = 0
        
        while current <= end:
            group_end = min(current + simultaneous - 1, end)
            
            # Create a row frame for each item
            row_frame = tk.Frame(self.scrollable_frame, bg=self.card_color, highlightbackground=self.border_color, 
                                 highlightcolor=self.accent_color, highlightthickness=1)
            row_frame.pack(fill="x", pady=4, padx=5)
            
            # Label showing the range of profiles
            label_text = f"Profiles {current} - {group_end}   ({group_end - current + 1} profiles)"
            lbl = tk.Label(row_frame, text=label_text, bg=self.card_color, fg=self.text_color, font=("Segoe UI", 10, "bold"), anchor="w")
            
            # Action button
            open_btn = tk.Button(
                row_frame, 
                text="Mở Nhóm này", 
                bg="#28a745", 
                fg="#ffffff", 
                activebackground="#218838",
                activeforeground="#ffffff",
                relief="flat", 
                bd=0, 
                font=("Segoe UI", 9, "bold"), 
                padx=15, 
                pady=6,
                command=lambda s=current, e=group_end: self.open_profiles(s, e)
            )
            
            # Responsive configuration for sequential rows
            def make_row_responsive(event, l=lbl, b=open_btn):
                if event.width < 500:
                    l.grid(row=0, column=0, sticky="w", padx=15, pady=(8, 2))
                    b.grid(row=1, column=0, sticky="ew", padx=15, pady=(2, 8))
                    event.widget.columnconfigure(0, weight=1)
                    event.widget.columnconfigure(1, weight=0)
                else:
                    l.grid(row=0, column=0, sticky="w", padx=15, pady=8)
                    b.grid(row=0, column=1, sticky="e", padx=10, pady=5)
                    event.widget.columnconfigure(0, weight=1)
                    event.widget.columnconfigure(1, weight=0)
                    
            row_frame.bind("<Configure>", make_row_responsive)
            
            current = group_end + 1
            row_idx += 1

        if row_idx == 0:
            no_lbl = tk.Label(self.scrollable_frame, text="Không có profile nào được tạo.", bg=self.card_color, fg=self.text_muted, font=("Segoe UI", 10, "italic"))
            no_lbl.pack(pady=20)

    def open_profiles(self, start_num, end_num):
        chrome_path = self.chrome_path_var.get()
        website = self.website_var.get()
        
        # Simple URL normalization
        if not (website.startswith("http://") or website.startswith("https://")):
            website = "https://" + website
            
        if not os.path.exists(chrome_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file Chrome tại: {chrome_path}\nVui lòng kiểm tra lại đường dẫn.")
            return
 
        opened_count = 0
        for i in range(start_num, end_num + 1):
            profile_dir = f"Profile {i}"
            try:
                # Launch Chrome window
                subprocess.Popen([chrome_path, f"--profile-directory={profile_dir}", website])
                opened_count += 1
                time.sleep(0.3) # Mild delay to prevent CPU spike
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở Profile {i}: {e}")
                break
                
        print(f"Đã mở {opened_count} profiles từ {start_num} đến {end_num}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChromeProfileManagerApp(root)
    root.mainloop()
