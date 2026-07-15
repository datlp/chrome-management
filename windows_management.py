import os
import json
import subprocess
import time
import csv
import threading
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CONFIG_DIR = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "dsoft", "windows-debloat-management")
CONFIG_FILE = os.path.join(CONFIG_DIR, "windows_debloat_config.json")

DEFAULT_APPS = [
    # Exact Match packages (using -AllUsers)
    {"name": "Bing Weather", "pattern": "Microsoft.BingWeather", "type": "exact"},
    {"name": "Get Started", "pattern": "Microsoft.Getstarted", "type": "exact"},
    {"name": "Office Hub", "pattern": "Microsoft.MicrosoftOfficeHub", "type": "exact"},
    {"name": "Solitaire Collection", "pattern": "Microsoft.MicrosoftSolitaireCollection", "type": "exact"},
    {"name": "Mixed Reality Portal", "pattern": "Microsoft.MixedReality.Portal", "type": "exact"},
    {"name": "Outlook for Windows", "pattern": "Microsoft.OutlookForWindows", "type": "exact"},
    {"name": "People", "pattern": "Microsoft.People", "type": "exact"},
    {"name": "Skype", "pattern": "Microsoft.SkypeApp", "type": "exact"},
    {"name": "Alarms & Clock", "pattern": "Microsoft.WindowsAlarms", "type": "exact"},
    {"name": "Calculator", "pattern": "Microsoft.WindowsCalculator", "type": "exact"},
    {"name": "Camera", "pattern": "Microsoft.WindowsCamera", "type": "exact"},
    {"name": "Feedback Hub", "pattern": "Microsoft.WindowsFeedbackHub", "type": "exact"},
    {"name": "Maps", "pattern": "Microsoft.WindowsMaps", "type": "exact"},
    {"name": "Sound Recorder", "pattern": "Microsoft.WindowsSoundRecorder", "type": "exact"},
    {"name": "Xbox TCUI", "pattern": "Microsoft.Xbox.TCUI", "type": "exact"},
    {"name": "Xbox App", "pattern": "Microsoft.XboxApp", "type": "exact"},
    {"name": "Xbox Game Callable UI", "pattern": "Microsoft.XboxGameCallableUI", "type": "exact"},
    {"name": "Xbox Game Overlay", "pattern": "Microsoft.XboxGameOverlay", "type": "exact"},
    {"name": "Xbox Gaming Overlay", "pattern": "Microsoft.XboxGamingOverlay", "type": "exact"},
    {"name": "Xbox Identity Provider", "pattern": "Microsoft.XboxIdentityProvider", "type": "exact"},
    {"name": "Xbox Speech To Text Overlay", "pattern": "Microsoft.XboxSpeechToTextOverlay", "type": "exact"},
    {"name": "Groove Music", "pattern": "Microsoft.ZuneMusic", "type": "exact"},
    {"name": "Movies & TV", "pattern": "Microsoft.ZuneVideo", "type": "exact"},
    {"name": "Get Help", "pattern": "Microsoft.GetHelp", "type": "exact"},
    {"name": "Copilot", "pattern": "Microsoft.Copilot", "type": "exact"},
    {"name": "To Do", "pattern": "Microsoft.Todos", "type": "exact"},
    {"name": "Bing News", "pattern": "Microsoft.BingNews", "type": "exact"},
    {"name": "Clipchamp", "pattern": "Clipchamp.Clipchamp", "type": "exact"},

    # Wildcard Match packages
    {"name": "Adobe Photoshop Express", "pattern": "*AdobeSystemsIncorporated.AdobePhotoshopExpress*", "type": "wildcard"},
    {"name": "Autodesk SketchBook", "pattern": "*AutodeskSketchBook*", "type": "wildcard"},
    {"name": "Bing Sports", "pattern": "*bingsports*", "type": "wildcard"},
    {"name": "Comms Phone", "pattern": "*CommsPhone*", "type": "wildcard"},
    {"name": "Connectivity Store", "pattern": "*ConnectivityStore*", "type": "wildcard"},
    {"name": "Facebook", "pattern": "*Facebook*", "type": "wildcard"},
    {"name": "Candy Crush Soda Saga", "pattern": "*king.com.CandyCrushSodaSaga*", "type": "wildcard"},
    {"name": "3D Builder", "pattern": "*Microsoft.3dbuilder*", "type": "wildcard"},
    {"name": "Cortana / Voice Activation", "pattern": "*Microsoft.549981C3F5F10*", "type": "wildcard"},
    {"name": "App Connector", "pattern": "*Microsoft.Appconnector*", "type": "wildcard"},
    {"name": "Asphalt 8 Airborne", "pattern": "*Microsoft.Asphalt8Airborne*", "type": "wildcard"},
    {"name": "Drawboard PDF", "pattern": "*Microsoft.DrawboardPDF*", "type": "wildcard"},
    {"name": "Messaging", "pattern": "*Microsoft.Messaging*", "type": "wildcard"},
    {"name": "Edge Beta", "pattern": "*Microsoft.MicrosoftEdge.Beta*", "type": "wildcard"},
    {"name": "Edge Canary", "pattern": "*Microsoft.MicrosoftEdge.Canary*", "type": "wildcard"},
    {"name": "Edge", "pattern": "*Microsoft.MicrosoftEdge*", "type": "wildcard"},
    {"name": "Edge DevTools Client", "pattern": "*Microsoft.MicrosoftEdgeDevToolsClient*", "type": "wildcard"},
    {"name": "OneConnect", "pattern": "*Microsoft.OneConnect*", "type": "wildcard"},
    {"name": "Print 3D", "pattern": "*Microsoft.Print3D*", "type": "wildcard"},
    {"name": "Screen Sketch", "pattern": "*Microsoft.ScreenSketch*", "type": "wildcard"},
    {"name": "Whiteboard", "pattern": "*Microsoft.Whiteboard*", "type": "wildcard"},
    {"name": "Mail and Calendar", "pattern": "*microsoft.windowscommunicationsapps*", "type": "wildcard"},
    {"name": "3D Viewer", "pattern": "*Microsoft3DViewer*", "type": "wildcard"},
    {"name": "Minecraft UWP", "pattern": "*MinecraftUWP*", "type": "wildcard"},
    {"name": "Netflix", "pattern": "*Netflix*", "type": "wildcard"},
    {"name": "Office Sway", "pattern": "*Office.Sway*", "type": "wildcard"},
    {"name": "OneNote", "pattern": "*OneNote*", "type": "wildcard"},
    {"name": "Pandora", "pattern": "*PandoraMediaInc*", "type": "wildcard"},
    {"name": "Twitter", "pattern": "*Twitter*", "type": "wildcard"},
    {"name": "Windows Scan", "pattern": "*WindowsScan*", "type": "wildcard"},
    {"name": "Xbox One SmartGlass", "pattern": "*XboxOneSmartGlass*", "type": "wildcard"}
]

class WindowsDebloatManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Debloat Manager")
        self.root.geometry("800x800")
        self.root.minsize(600, 600)
        
        # Color palette (Modern Dark Mode consistent with chrome_profiles.py)
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
        self.apps = []
        self.system_packages = []
        self.checking_status = False
        self.scanning_system = False
        self.debloating = False
        self.tree_edit_entry = None
        self.drag_start_item = None
        
        self.system_search_var = tk.StringVar()
        self.system_search_var.trace_add("write", self.on_system_search_change)
        
        # Load config
        self.load_config()
        
        # Build UI
        self.build_ui()
        
        # Refresh statuses on startup
        self.refresh_app_statuses()
        self.scan_system_packages()

    def load_config(self):
        self.apps = []
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.apps = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        if not self.apps:
            # Deep copy default apps
            self.apps = [dict(app) for app in DEFAULT_APPS]
            # Ensure they all have status
            for app in self.apps:
                app["status"] = "Chưa kiểm tra"
            self.save_config()

    def save_config(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                save_data = []
                for app in self.apps:
                    save_data.append({
                        "name": app["name"],
                        "pattern": app["pattern"],
                        "type": app["type"]
                    })
                json.dump(save_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def build_ui(self):
        # Create ttk.Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Debloat Manager
        self.tab_debloat = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_debloat, text="Quản lý Debloat")
        
        # Tab 2: Get-AppxPackage (System)
        self.tab_system = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_system, text="Get-AppxPackage (Hệ thống)")
        
        # ==========================================
        # TAB 1: Debloat Manager UI Construction
        # ==========================================
        self.debloat_container = ttk.Frame(self.tab_debloat, padding=20)
        self.debloat_container.pack(fill="both", expand=True)
        
        # Header Tab 1
        header_frame = ttk.Frame(self.debloat_container)
        header_frame.pack(fill="x", pady=(0, 15))
        
        self.header_lbl = ttk.Label(header_frame, text="WINDOWS DEBLOAT MANAGER", style="Header.TLabel")
        self.header_lbl.pack(side="left", anchor="w")
        
        self.btn_reset_defaults = ttk.Button(header_frame, text="Reset Mặc Định", style="Normal.TButton", command=self.reset_to_defaults)
        self.btn_reset_defaults.pack(side="right", padx=(5, 0))
        
        self.btn_export = ttk.Button(header_frame, text="Export CSV", style="Normal.TButton", command=self.export_csv)
        self.btn_export.pack(side="right", padx=(5, 0))
        
        self.btn_import = ttk.Button(header_frame, text="Import CSV", style="Normal.TButton", command=self.import_csv)
        self.btn_import.pack(side="right")
        
        # Info & Refresh
        info_frame = ttk.Frame(self.debloat_container)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.list_header_lbl = ttk.Label(info_frame, text="Danh sách ứng dụng debloat:", style="TLabel", font=("Segoe UI", 11, "bold"))
        self.list_header_lbl.pack(side="left", anchor="w")
        
        self.btn_refresh = ttk.Button(info_frame, text="⟳ Kiểm tra Trạng thái", style="Accent.TButton", command=self.refresh_app_statuses)
        self.btn_refresh.pack(side="right", anchor="e")
        
        # Treeview Tab 1
        table_outer_frame = ttk.Frame(self.debloat_container, style="Card.TFrame")
        table_outer_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(table_outer_frame, columns=("Name", "Pattern", "Type", "Status"), show="headings", style="Treeview", selectmode="extended")
        self.tree.heading("Name", text="Tên Ứng Dụng", command=lambda: self.sort_treeview("Name", False))
        self.tree.heading("Pattern", text="Gói / Pattern", command=lambda: self.sort_treeview("Pattern", False))
        self.tree.heading("Type", text="Loại Khớp", command=lambda: self.sort_treeview("Type", False))
        self.tree.heading("Status", text="Trạng thái", command=lambda: self.sort_treeview("Status", False))
        
        self.tree.column("Name", width=180, anchor="w")
        self.tree.column("Pattern", width=250, anchor="w")
        self.tree.column("Type", width=100, anchor="center")
        self.tree.column("Status", width=120, anchor="center")
        
        self.scroll = ttk.Scrollbar(table_outer_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        # Event bindings Tab 1
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start, add="+")
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<Double-1>", lambda e: self.debloat_selected_apps())
        
        # Context Menu Tab 1
        self.context_menu = tk.Menu(self.tree, tearoff=0, bg=self.card_color, fg=self.text_color, activebackground=self.accent_color, activeforeground="#ffffff")
        self.context_menu.add_command(label="Gỡ bỏ (Debloat) các mục đã chọn", command=self.debloat_selected_apps)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Xóa khỏi danh sách cấu hình", command=self.delete_selected_apps)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Bottom controls Tab 1
        self.ctrl_frame = ttk.Frame(self.debloat_container)
        self.ctrl_frame.pack(fill="x", pady=(10, 0))
        
        self.lbl_selected_count = ttk.Label(self.ctrl_frame, text="Đã chọn: 0 / 0 mục", font=("Segoe UI", 10, "italic"))
        self.lbl_selected_count.pack(side="left", padx=(0, 15))
        
        self.btn_select_all = ttk.Button(self.ctrl_frame, text="Chọn tất cả", style="Normal.TButton", command=self.select_all)
        self.btn_select_all.pack(side="left", padx=5)
        
        self.btn_deselect = ttk.Button(self.ctrl_frame, text="Bỏ chọn", style="Normal.TButton", command=self.deselect_all)
        self.btn_deselect.pack(side="left", padx=5)
        
        self.btn_debloat_selected = tk.Button(self.ctrl_frame, text="GỠ BỎ (DEBLOAT) ĐÃ CHỌN", bg="#d9534f", fg="#ffffff", 
                                             activebackground="#c9302c", activeforeground="#ffffff", relief="flat", bd=0, 
                                             font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.debloat_selected_apps)
        self.btn_debloat_selected.pack(side="right")
        
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_selected_count())
        self.populate_treeview()

        # ==========================================
        # TAB 2: Get-AppxPackage Live UI Construction
        # ==========================================
        self.system_container = ttk.Frame(self.tab_system, padding=20)
        self.system_container.pack(fill="both", expand=True)
        
        # Header & Search Tab 2
        sys_header_frame = ttk.Frame(self.system_container)
        sys_header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(sys_header_frame, text="DANH SÁCH APPX HỆ THỐNG", style="Header.TLabel").pack(side="left")
        
        self.btn_scan_system = ttk.Button(sys_header_frame, text="⟳ Quét lại hệ thống", style="Accent.TButton", command=self.scan_system_packages)
        self.btn_scan_system.pack(side="right")
        
        # Search Box Card
        search_card = ttk.Frame(self.system_container, style="Card.TFrame", padding=12)
        search_card.pack(fill="x", pady=(0, 15))
        
        ttk.Label(search_card, text="Tìm kiếm gói Appx:", style="Card.TLabel").pack(side="left", padx=(0, 10))
        self.search_entry = tk.Entry(search_card, textvariable=self.system_search_var, bg=self.bg_color, fg=self.text_color, 
                                     insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                     highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10))
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # System List Table
        sys_table_outer = ttk.Frame(self.system_container, style="Card.TFrame")
        sys_table_outer.pack(fill="both", expand=True)
        
        self.sys_tree = ttk.Treeview(sys_table_outer, columns=("Name", "PackageFullName"), show="headings", style="Treeview", selectmode="extended")
        self.sys_tree.heading("Name", text="Tên Gói", command=lambda: self.sort_sys_treeview("Name", False))
        self.sys_tree.heading("PackageFullName", text="Package ID (Full Name)", command=lambda: self.sort_sys_treeview("PackageFullName", False))
        
        self.sys_tree.column("Name", width=280, anchor="w")
        self.sys_tree.column("PackageFullName", width=460, anchor="w")
        
        self.sys_scroll = ttk.Scrollbar(sys_table_outer, orient="vertical", command=self.sys_tree.yview)
        self.sys_tree.configure(yscrollcommand=self.sys_scroll.set)
        
        self.sys_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.sys_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)
        
        # Controls Bar Tab 2
        sys_ctrl_frame = ttk.Frame(self.system_container)
        sys_ctrl_frame.pack(fill="x", pady=(10, 0))
        
        self.lbl_sys_count = ttk.Label(sys_ctrl_frame, text="Tìm thấy: 0 packages", font=("Segoe UI", 10, "italic"))
        self.lbl_sys_count.pack(side="left", anchor="w")
        
        # Action Buttons
        self.btn_direct_uninstall = tk.Button(sys_ctrl_frame, text="GỠ BỎ TRỰC TIẾP", bg="#d9534f", fg="#ffffff",
                                             activebackground="#c9302c", activeforeground="#ffffff", relief="flat", bd=0,
                                             font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.uninstall_sys_packages)
        self.btn_direct_uninstall.pack(side="right", padx=(10, 0))
        
        self.btn_add_to_debloat = tk.Button(sys_ctrl_frame, text="THÊM VÀO DEBLOAT LIST", bg="#28a745", fg="#ffffff",
                                            activebackground="#218838", activeforeground="#ffffff", relief="flat", bd=0,
                                            font=("Segoe UI", 10, "bold"), padx=15, pady=6, command=self.add_system_package_to_debloat)
        self.btn_add_to_debloat.pack(side="right")

    # ==========================================
    # DEBLOAT MANAGER METHODS (TAB 1)
    # ==========================================
    def populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Pinned row for adding a new debloat app
        self.tree.insert("", "end", iid="__add_row__", values=("+ Thêm mới...", "Nhập package pattern...", "wildcard", "-"))
        
        for idx, app in enumerate(self.apps):
            status = app.get("status", "Chưa kiểm tra")
            self.tree.insert("", "end", iid=f"app_{idx}", values=(app["name"], app["pattern"], app["type"], status))
            
        self.update_selected_count()

    def update_selected_count(self):
        total = len(self.apps)
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
        items = [(self.tree.set(item_id, col), item_id) for item_id in self.tree.get_children("") if item_id != "__add_row__"]
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, item_id) in enumerate(items):
            self.tree.move(item_id, "", index)
        self.tree.heading(col, command=lambda c=col: self.sort_treeview(c, not reverse))

    def on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item and item != "__add_row__":
            self.drag_start_item = item

    def on_drag_motion(self, event):
        item = self.tree.identify_row(event.y)
        if item and item != "__add_row__" and self.drag_start_item:
            children = [c for c in self.tree.get_children("") if c != "__add_row__"]
            try:
                start_idx = children.index(self.drag_start_item)
                end_idx = children.index(item)
                low = min(start_idx, end_idx)
                high = max(start_idx, end_idx)
                self.tree.selection_set(children[low:high+1])
                self.update_selected_count()
            except ValueError:
                pass

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

    def on_tree_click(self, event):
        if self.tree_edit_entry:
            self.tree_edit_entry.destroy()
            self.tree_edit_entry = None
            
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
            
        x, y, w, h = bbox
        val = self.tree.set(item, column)
        
        # Clicked "+ Thêm mới..." row or status column (don't edit status column)
        if column == "#4":
            return
            
        if item == "__add_row__" and val in ("+ Thêm mới...", "Nhập package pattern...", "wildcard"):
            val = ""
            
        if column == "#3": # Type column, make a Combobox
            combo = ttk.Combobox(self.tree, values=["exact", "wildcard"], state="readonly")
            combo.set(val or "wildcard")
            combo.place(x=x, y=y, width=w, height=h)
            combo.focus_set()
            combo.bind("<<ComboboxSelected>>", lambda e: self.save_cell_edit(item, column, combo.get()))
            combo.bind("<FocusOut>", lambda e: self.save_cell_edit(item, column, combo.get()))
            self.tree_edit_entry = combo
        else: # Standard text entry
            entry = tk.Entry(self.tree, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, relief="flat", font=("Segoe UI", 10))
            entry.insert(0, val)
            entry.select_range(0, tk.END)
            entry.place(x=x, y=y, width=w, height=h)
            entry.focus_set()
            entry.bind("<Return>", lambda e: self.save_cell_edit(item, column, entry.get()))
            entry.bind("<FocusOut>", lambda e: self.save_cell_edit(item, column, entry.get()))
            self.tree_edit_entry = entry

    def save_cell_edit(self, item, column, new_val):
        if self.tree_edit_entry:
            widget = self.tree_edit_entry
            self.tree_edit_entry = None
            widget.destroy()
            
        new_val = new_val.strip()
        
        if item == "__add_row__":
            current_name = self.tree.set(item, "Name")
            current_pattern = self.tree.set(item, "Pattern")
            current_type = self.tree.set(item, "Type")
            
            if column == "#1":
                if new_val and new_val != "+ Thêm mới...":
                    self.tree.set(item, "Name", new_val)
                    current_name = new_val
            elif column == "#2":
                if new_val and new_val != "Nhập package pattern...":
                    self.tree.set(item, "Pattern", new_val)
                    current_pattern = new_val
            elif column == "#3":
                self.tree.set(item, "Type", new_val)
                current_type = new_val
                    
            if (current_name and current_name != "+ Thêm mới..." and 
                current_pattern and current_pattern != "Nhập package pattern..."):
                self.apps.append({
                    "name": current_name,
                    "pattern": current_pattern,
                    "type": current_type,
                    "status": "Chưa kiểm tra"
                })
                self.populate_treeview()
                self.save_config()
        else:
            if item.startswith("app_"):
                try:
                    idx = int(item.split("_")[1])
                    if 0 <= idx < len(self.apps):
                        if column == "#1":
                            self.apps[idx]["name"] = new_val
                        elif column == "#2":
                            self.apps[idx]["pattern"] = new_val
                        elif column == "#3":
                            self.apps[idx]["type"] = new_val
                        
                        self.tree.set(item, column, new_val)
                        self.save_config()
                except Exception as e:
                    print(f"Error editing cell: {e}")

    def delete_selected_apps(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("app_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một ứng dụng để xóa khỏi danh sách cấu hình.")
            return
            
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa {len(selected_items)} ứng dụng khỏi danh sách cấu hình?")
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
            if 0 <= idx < len(self.apps):
                del self.apps[idx]
                
        self.populate_treeview()
        self.save_config()

    def reset_to_defaults(self):
        confirm = messagebox.askyesno("Reset Mặc Định", "Bạn có chắc chắn muốn khôi phục danh sách ứng dụng debloat mặc định không?")
        if not confirm:
            return
        self.apps = [dict(app) for app in DEFAULT_APPS]
        for app in self.apps:
            app["status"] = "Chưa kiểm tra"
        self.populate_treeview()
        self.save_config()
        self.refresh_app_statuses()

    def refresh_app_statuses(self):
        if self.checking_status:
            return
        
        self.checking_status = True
        self.btn_refresh.config(state="disabled", text="⌛ Đang kiểm tra...")
        
        # Set all statuses to "Đang check..." in the treeview
        for item in self.tree.get_children():
            if item != "__add_row__":
                self.tree.set(item, "Status", "Đang check...")
        
        def run_check():
            try:
                # Query all installed package names via PowerShell (fastest way)
                cmd = ["powershell", "-NoProfile", "-Command", "Get-AppxPackage | Select-Object -Property Name | ConvertTo-Json"]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                installed_names = set()
                if stdout_text.strip():
                    try:
                        data = json.loads(stdout_text)
                        if isinstance(data, list):
                            for pkg in data:
                                if pkg and "Name" in pkg and pkg["Name"]:
                                    installed_names.add(pkg["Name"].lower())
                        elif isinstance(data, dict):
                            if "Name" in data and data["Name"]:
                                installed_names.add(data["Name"].lower())
                    except Exception as json_err:
                        lines = stdout_text.split("\n")
                        for line in lines:
                            if '"Name":' in line:
                                name_part = line.split(":")[-1].replace('"', '').replace(',', '').strip()
                                if name_part:
                                    installed_names.add(name_part.lower())

                # Update statuses in self.apps
                for app in self.apps:
                    pattern = app["pattern"].lower()
                    app_type = app["type"]
                    
                    found = False
                    if app_type == "exact":
                        if pattern in installed_names:
                            found = True
                    else: # wildcard match
                        cleaned_pattern = pattern.strip("*")
                        for inst_name in installed_names:
                            if fnmatch.fnmatch(inst_name, pattern) or cleaned_pattern in inst_name:
                                found = True
                                break
                    
                    app["status"] = "Đang cài đặt" if found else "Đã gỡ bỏ"
                
                self.root.after(0, self.update_statuses_ui)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi quét trạng thái: {e}"))
                self.root.after(0, self.reset_refresh_button)

        threading.Thread(target=run_check, daemon=True).start()

    def update_statuses_ui(self):
        for idx, app in enumerate(self.apps):
            item_iid = f"app_{idx}"
            if self.tree.exists(item_iid):
                self.tree.set(item_iid, "Status", app["status"])
        self.reset_refresh_button()

    def reset_refresh_button(self):
        self.checking_status = False
        self.btn_refresh.config(state="normal", text="⟳ Kiểm tra Trạng thái")

    def debloat_selected_apps(self):
        selected_items = [item for item in self.tree.selection() if item.startswith("app_")]
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một ứng dụng để thực hiện debloat.")
            return
            
        confirm = messagebox.askyesno(
            "Xác nhận Debloat",
            f"Bạn có chắc chắn muốn gỡ bỏ (debloat) {len(selected_items)} ứng dụng đã chọn?\n\n"
            "Thao tác này sẽ chạy lệnh Remove-AppxPackage trong PowerShell."
        )
        if not confirm:
            return
            
        apps_to_debloat = []
        for item in selected_items:
            try:
                idx = int(item.split("_")[1])
                apps_to_debloat.append((item, self.apps[idx]))
            except ValueError:
                pass
                
        # Run debloat in a background thread to prevent UI freezing
        def run_debloat():
            try:
                for item_iid, app in apps_to_debloat:
                    self.root.after(0, lambda: self.tree.set(item_iid, "Status", "Đang gỡ..."))
                    pattern = app["pattern"]
                    
                    if app["type"] == "exact":
                        ps_cmd = f'Get-AppxPackage -AllUsers "{pattern}" | Remove-AppxPackage'
                    else:
                        cleaned_pat = pattern
                        if not cleaned_pat.startswith("*"):
                            cleaned_pat = "*" + cleaned_pat
                        if not cleaned_pat.endswith("*"):
                            cleaned_pat = cleaned_pat + "*"
                        ps_cmd = f'Get-AppxPackage "{cleaned_pat}" | Remove-AppxPackage'
                    
                    cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Check status again once completed
                self.root.after(0, self.refresh_app_statuses)
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã hoàn thành tiến trình debloat ứng dụng đã chọn."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi xảy ra khi debloat: {e}"))
                self.root.after(0, self.refresh_app_statuses)

        threading.Thread(target=run_debloat, daemon=True).start()

    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Import CSV Config",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            imported_apps = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            if not rows:
                messagebox.showwarning("Cảnh báo", "File CSV trống.")
                return
                
            start_row = 0
            if len(rows[0]) >= 3:
                val0 = rows[0][0].lower()
                val1 = rows[0][1].lower()
                val2 = rows[0][2].lower()
                if "name" in val0 or "tên" in val0 or "pattern" in val1 or "type" in val2 or "loại" in val2:
                    start_row = 1
                    
            for row in rows[start_row:]:
                if not row or len(row) < 3:
                    continue
                name = row[0].strip()
                pattern = row[1].strip()
                match_type = row[2].strip().lower()
                if match_type not in ("exact", "wildcard"):
                    match_type = "wildcard"
                if name and pattern:
                    imported_apps.append({
                        "name": name,
                        "pattern": pattern,
                        "type": match_type,
                        "status": "Chưa kiểm tra"
                    })
                    
            if not imported_apps:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu hợp lệ trong file CSV.")
                return
                
            ans = messagebox.askyesnocancel(
                "Import CSV",
                "Bạn có muốn giữ lại danh sách ứng dụng hiện tại không?\n\n- Chọn 'Yes' để Thêm/Gộp dữ liệu.\n- Chọn 'No' để Thay thế toàn bộ."
            )
            
            if ans is None:
                return
                
            if ans:
                # Merge
                appended_count = 0
                for app in imported_apps:
                    if not any(existing["pattern"].lower() == app["pattern"].lower() for existing in self.apps):
                        self.apps.append(app)
                        appended_count += 1
                messagebox.showinfo("Thành công", f"Đã gộp thêm {appended_count} ứng dụng mới từ file CSV.")
            else:
                # Replace
                self.apps = imported_apps
                messagebox.showinfo("Thành công", f"Đã thay thế toàn bộ bằng {len(imported_apps)} ứng dụng từ file CSV.")
                
            self.populate_treeview()
            self.save_config()
            self.refresh_app_statuses()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể import file CSV: {e}")

    def export_csv(self):
        if not self.apps:
            messagebox.showwarning("Cảnh báo", "Danh sách ứng dụng trống, không thể export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export CSV Config",
            initialfile="windows_debloat_apps.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Pattern", "Type"])
                for app in self.apps:
                    writer.writerow([app["name"], app["pattern"], app["type"]])
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu ra file CSV thành công:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể export file CSV: {e}")

    # ==========================================
    # GET-APPXPACKAGE METHODS (TAB 2)
    # ==========================================
    def on_system_search_change(self, *args):
        self.apply_system_search()

    def scan_system_packages(self):
        if self.scanning_system:
            return
        
        self.scanning_system = True
        self.btn_scan_system.config(state="disabled", text="⌛ Đang quét...")
        
        # Clear system treeview and show status
        for item in self.sys_tree.get_children():
            self.sys_tree.delete(item)
        self.sys_tree.insert("", "end", values=("⌛ Đang quét hệ thống...", ""))
        
        def run_scan():
            try:
                # Run PowerShell query to fetch live installed AppxPackages
                cmd = ["powershell", "-NoProfile", "-Command", "Get-AppxPackage | Select-Object -Property Name, PackageFullName, Version | ConvertTo-Json"]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                packages = []
                if stdout_text.strip():
                    try:
                        data = json.loads(stdout_text)
                        if isinstance(data, list):
                            for item in data:
                                if item and "Name" in item and item["Name"]:
                                    packages.append({
                                        "name": item.get("Name", ""),
                                        "version": item.get("Version", ""),
                                        "package_full_name": item.get("PackageFullName", "")
                                    })
                        elif isinstance(data, dict):
                            if "Name" in data and data["Name"]:
                                packages.append({
                                    "name": data.get("Name", ""),
                                    "version": data.get("Version", ""),
                                    "package_full_name": data.get("PackageFullName", "")
                                })
                    except Exception:
                        # Parsing fallback using text processing
                        lines = stdout_text.split("\n")
                        current_pkg = {}
                        for line in lines:
                            line = line.strip()
                            if '"Name":' in line:
                                current_pkg["name"] = line.split(":")[-1].replace('"', '').replace(',', '').strip()
                            elif '"Version":' in line:
                                current_pkg["version"] = line.split(":")[-1].replace('"', '').replace(',', '').strip()
                            elif '"PackageFullName":' in line:
                                current_pkg["package_full_name"] = line.split(":")[-1].replace('"', '').replace(',', '').strip()
                                if current_pkg.get("name"):
                                    packages.append(current_pkg)
                                current_pkg = {}

                # Sort naturally by name
                packages.sort(key=lambda x: x["name"].lower())
                self.system_packages = packages
                
                self.root.after(0, self.apply_system_search)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi quét hệ thống: {e}"))
            finally:
                self.root.after(0, self.reset_scan_button)

        threading.Thread(target=run_scan, daemon=True).start()

    def reset_scan_button(self):
        self.scanning_system = False
        self.btn_scan_system.config(state="normal", text="⟳ Quét lại hệ thống")

    def apply_system_search(self):
        search_query = self.system_search_var.get().lower().strip()
        
        # Clear tree
        for item in self.sys_tree.get_children():
            self.sys_tree.delete(item)
            
        filtered_pkgs = []
        for pkg in self.system_packages:
            if not search_query or search_query in pkg["name"].lower() or search_query in pkg["package_full_name"].lower():
                filtered_pkgs.append(pkg)
                
        for pkg in filtered_pkgs:
            self.sys_tree.insert("", "end", values=(pkg["name"], pkg["package_full_name"]))
            
        self.lbl_sys_count.config(text=f"Tìm thấy: {len(filtered_pkgs)} packages")

    def sort_sys_treeview(self, col, reverse):
        items = [(self.sys_tree.set(item_id, col), item_id) for item_id in self.sys_tree.get_children("")]
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, item_id) in enumerate(items):
            self.sys_tree.move(item_id, "", index)
        self.sys_tree.heading(col, command=lambda c=col: self.sort_sys_treeview(c, not reverse))

    def add_system_package_to_debloat(self):
        selected = self.sys_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một Appx package trong bảng hệ thống.")
            return
            
        added_count = 0
        for item in selected:
            values = self.sys_tree.item(item, "values")
            pkg_name = values[0]
            
            # Check if already exists in self.apps
            if not any(app["pattern"].lower() == pkg_name.lower() for app in self.apps):
                self.apps.append({
                    "name": pkg_name.split(".")[-1] if "." in pkg_name else pkg_name,
                    "pattern": pkg_name,
                    "type": "exact",
                    "status": "Đang cài đặt"
                })
                added_count += 1
                
        if added_count > 0:
            self.populate_treeview()
            self.save_config()
            self.refresh_app_statuses()
            messagebox.showinfo("Thành công", f"Đã thêm {added_count} ứng dụng mới vào danh sách Debloat ở Tab 1.")
        else:
            messagebox.showinfo("Thông tin", "Các ứng dụng đã chọn đã có sẵn trong danh sách Debloat.")

    def uninstall_sys_packages(self):
        selected = self.sys_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một Appx package từ hệ thống để gỡ cài đặt trực tiếp.")
            return
            
        confirm = messagebox.askyesno(
            "Xác nhận gỡ bỏ trực tiếp",
            f"Bạn có chắc chắn muốn gỡ cài đặt trực tiếp {len(selected)} Appx package đã chọn khỏi máy tính không?\n\n"
            "Thao tác này sẽ chạy lệnh Remove-AppxPackage trực tiếp trên Windows."
        )
        if not confirm:
            return
            
        packages_to_uninstall = []
        for item in selected:
            values = self.sys_tree.item(item, "values")
            packages_to_uninstall.append((item, values[0], values[1])) # iid, name, package_full_name
            
        def run_direct_uninstall():
            try:
                for item_iid, name, full_name in packages_to_uninstall:
                    self.root.after(0, lambda i=item_iid: self.sys_tree.set(i, "PackageFullName", "Đang gỡ..."))
                    
                    # Direct uninstall command by piping Get-AppxPackage -Name to Remove-AppxPackage
                    # This is safe and removes it for current user, matching typical behavior.
                    ps_cmd = f'Get-AppxPackage -Name "{name}" | Remove-AppxPackage'
                    cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                # Re-scan system once uninstalled
                self.root.after(0, self.scan_system_packages)
                self.root.after(0, self.refresh_app_statuses)
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã gỡ cài đặt trực tiếp các gói đã chọn thành công."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi xảy ra khi gỡ cài đặt trực tiếp: {e}"))
                self.root.after(0, self.scan_system_packages)

        threading.Thread(target=run_direct_uninstall, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsDebloatManagerApp(root)
    root.mainloop()
