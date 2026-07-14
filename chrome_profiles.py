import os
import json
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CONFIG_DIR = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "dsoft", "chrome-profile-management")
CONFIG_FILE = os.path.join(CONFIG_DIR, "chrome_profiles_config.json")

DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(DEFAULT_CHROME_PATH):
    DEFAULT_CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

class ChromeProfileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Profiles Manager")
        self.root.geometry("680x750")
        self.root.minsize(600, 500)
        
        # Color palette (Modern Dark Mode)
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
        
        # Load existing config if available
        self.load_config()
        
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
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill="both", expand=True)
        
        # Header
        header_lbl = ttk.Label(main_container, text="CHROME PROFILES MANAGER", style="Header.TLabel")
        header_lbl.pack(pady=(0, 15), anchor="w")
        
        # Configuration Card
        config_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        config_card.pack(fill="x", pady=(0, 15))
        
        # Website Selection
        ttk.Label(config_card, text="Trang Web (URL):", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        web_entry = tk.Entry(config_card, textvariable=self.website_var, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10))
        web_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))
        
        # Preset website buttons
        preset_frame = ttk.Frame(config_card, style="Card.TFrame")
        preset_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=(2, 8), padx=(10, 0))
        
        presets = ["google.com", "facebook.com", "youtube.com", "gmail.com"]
        for p in presets:
            btn = tk.Button(preset_frame, text=p, bg=self.border_color, fg=self.text_muted, activebackground=self.accent_color,
                            activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 8), padx=6, pady=2,
                            command=lambda url=p: self.set_website_preset(url))
            btn.pack(side="left", padx=(0, 5))
            
        # Range Frame
        range_frame = ttk.Frame(config_card, style="Card.TFrame")
        range_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(range_frame, text="Profile bắt đầu:", style="Card.TLabel").pack(side="left")
        start_entry = tk.Entry(range_frame, textvariable=self.start_profile_var, width=6, bg=self.bg_color, fg=self.text_color, 
                               insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                               highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        start_entry.pack(side="left", padx=(5, 15))

        ttk.Label(range_frame, text="Profile kết thúc:", style="Card.TLabel").pack(side="left")
        end_entry = tk.Entry(range_frame, textvariable=self.end_profile_var, width=6, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        end_entry.pack(side="left", padx=(5, 15))

        # Sim count Frame (row 3)
        sim_frame = ttk.Frame(config_card, style="Card.TFrame")
        sim_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(sim_frame, text="Số lượng cùng lúc:", style="Card.TLabel").pack(side="left")
        sim_entry = tk.Entry(sim_frame, textvariable=self.simultaneous_var, width=6, bg=self.bg_color, fg=self.text_color, 
                             insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                             highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 10), justify="center")
        sim_entry.pack(side="left", padx=(5, 15))
        
        # profileNum presets
        ttk.Label(sim_frame, text="Mặc định:", style="Card.TLabel").pack(side="left", padx=(0, 5))
        for num in [2, 4, 6, 8, 10, 12]:
            btn = tk.Button(sim_frame, text=str(num), bg=self.border_color, fg=self.text_muted, activebackground=self.accent_color,
                            activeforeground="#ffffff", relief="flat", bd=0, font=("Segoe UI", 8, "bold"), padx=8, pady=2,
                            command=lambda n=num: self.simultaneous_var.set(n))
            btn.pack(side="left", padx=(0, 4))
        
        # Chrome path selection (row 4)
        ttk.Label(config_card, text="Đường dẫn Chrome:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=8)
        chrome_entry = tk.Entry(config_card, textvariable=self.chrome_path_var, bg=self.bg_color, fg=self.text_color, 
                                insertbackground=self.text_color, highlightthickness=1, highlightbackground=self.border_color, 
                                highlightcolor=self.accent_color, relief="flat", font=("Segoe UI", 9))
        chrome_entry.grid(row=4, column=1, sticky="ew", pady=8, padx=(10, 5))
        
        browse_btn = ttk.Button(config_card, text="Chọn file", style="Normal.TButton", command=self.browse_chrome_path)
        browse_btn.grid(row=4, column=2, sticky="e", pady=8)
        
        config_card.columnconfigure(1, weight=1)
        
        # Generate Action Buttons Frame
        action_btn_frame = ttk.Frame(main_container)
        action_btn_frame.pack(fill="x", pady=(0, 15))
        
        gen_btn = ttk.Button(action_btn_frame, text="TẠO NHÓM THEO SỐ THỨ TỰ", style="Accent.TButton", command=self.generate_profile_list)
        gen_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        scan_btn = ttk.Button(action_btn_frame, text="QUÉT PROFILE THỰC TẾ (CÓ EMAIL)", style="Accent.TButton", command=self.generate_actual_profile_list)
        scan_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # List Container Header
        ttk.Label(main_container, text="Danh sách nhóm Profile:", style="TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(5, 5))
        
        # Scrollable List Frame
        list_outer_frame = ttk.Frame(main_container, style="Card.TFrame")
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
        
        # Generate list automatically on startup
        self.generate_profile_list()

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
            
            # Pack order
            left_btn.pack(side="left", padx=(5, 0))
            chips_canvas.pack(side="left", fill="x", expand=True, padx=2, pady=5)
            right_btn.pack(side="left", padx=(0, 5))
            
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
            open_btn.pack(side="right", padx=10, pady=5)
            
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
            lbl.pack(side="left", fill="x", expand=True, padx=15, pady=8)
            
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
            open_btn.pack(side="right", padx=10, pady=5)
            
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
