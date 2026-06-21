import os
import sys
import re
import json
import socket
import threading
import queue
import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Set up appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SocketServer:
    def __init__(self, port, msg_queue):
        self.port = port
        self.queue = msg_queue
        self.running = False
        self.sock = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Do NOT use SO_REUSEADDR — we want an error if another instance is already running
        self.sock.settimeout(1.0)
        try:
            self.sock.bind(('127.0.0.1', self.port))
            self.sock.listen(5)
            print(f"[Server] Listening on port {self.port}")
            while self.running:
                try:
                    conn, addr = self.sock.accept()
                    data = b""
                    # Read until we get a newline or connection close
                    while True:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        data += chunk
                        if b'\n' in data:
                            break
                    if data:
                        try:
                            lines = data.decode('utf-8').split('\n')
                            for line in lines:
                                if line.strip():
                                    msg = json.loads(line)
                                    if 'url' in msg:
                                        self.queue.put(msg['url'])
                        except Exception as e:
                            print(f"[Server] Error parsing JSON: {e}")
                    conn.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    if not self.running:
                        break
                    print(f"[Server] Accept error: {e}")
        except Exception as e:
            print(f"[Server] Bind error: {e}")
        finally:
            if self.sock:
                self.sock.close()
            print("[Server] Server stopped.")

    def stop(self):
        self.running = False


class AntiDoomscrollApp(ctk.CTk):
    TRANSLATIONS = {
        "DE": {
            "title": "Anti-Doomscroll & Timer",
            "subtitle": "Schütze deine Zeit vor ablenkenden Videos!",
            "settings": "Einstellungen",
            "time_limit": "Zeitlimit (Minuten):",
            "time_placeholder": "z. B. 15",
            "video_limit": "Video-Limit (0 = aus):",
            "video_placeholder": "z. B. 5",
            "actions_label": "Aktionen bei Ablauf",
            "close_browser": "Browser nach Ablauf schließen (Chrome, Edge, Firefox)",
            "standby": "PC danach in den Energiesparmodus (Standby) versetzen",
            "btn_done": "Fertig",
            "btn_start_timer": "Timer starten",
            "btn_stop_timer": "Stoppen",
            "countdown_default": "00:00:00",
            "stats_videos": "Angesehene Videos: {count} / {limit}",
            "stats_last_video": " (Letztes Video!)",
            "stats_limit_exceeded": " (Limit überschritten!)",
            "limit_reached": "Limit erreicht! Aktionen werden ausgeführt...",
            "time_expired": "Zeit abgelaufen! Aktionen werden ausgeführt...",
            "timer_stopped": "Timer gestoppt.",
            "unlimited": "Unbegrenzt",
            "cancelled": "Abgebrochen",
            "theme_label": "Farbmodus:",
            "theme_light": "Light Mode",
            "theme_night": "Night Mode",
            "theme_system": "System Default"
        },
        "EN": {
            "title": "Anti-Doomscroll & Timer",
            "subtitle": "Protect your time from distracting videos!",
            "settings": "Settings",
            "time_limit": "Time Limit (minutes):",
            "time_placeholder": "e.g. 15",
            "video_limit": "Video Limit (0 = off):",
            "video_placeholder": "e.g. 5",
            "actions_label": "Actions on Expiration",
            "close_browser": "Close browser on expiration (Chrome, Edge, Firefox)",
            "standby": "Put PC into standby mode afterwards",
            "btn_done": "Done",
            "btn_start_timer": "Start Timer",
            "btn_stop_timer": "Stop",
            "countdown_default": "00:00:00",
            "stats_videos": "Watched videos: {count} / {limit}",
            "stats_last_video": " (Last video!)",
            "stats_limit_exceeded": " (Limit exceeded!)",
            "limit_reached": "Limit reached! Executing actions...",
            "time_expired": "Time expired! Executing actions...",
            "timer_stopped": "Timer stopped.",
            "unlimited": "Unlimited",
            "cancelled": "Cancelled",
            "theme_label": "Color Mode:",
            "theme_light": "Light Mode",
            "theme_night": "Night Mode",
            "theme_system": "System Default"
        },
        "FR": {
            "title": "Anti-Doomscroll & Timer",
            "subtitle": "Protégez votre temps des vidéos distrayantes !",
            "settings": "Paramètres",
            "time_limit": "Limite de temps (minutes) :",
            "time_placeholder": "ex. 15",
            "video_limit": "Limite de vidéos (0 = désactivé) :",
            "video_placeholder": "ex. 5",
            "actions_label": "Actions à l'expiration",
            "close_browser": "Fermer le navigateur à l'expiration (Chrome, Edge, Firefox)",
            "standby": "Mettre le PC en veille ensuite",
            "btn_done": "Terminé",
            "btn_start_timer": "Démarrer le minuteur",
            "btn_stop_timer": "Arrêter",
            "countdown_default": "00:00:00",
            "stats_videos": "Vidéos regardées : {count} / {limit}",
            "stats_last_video": " (Dernière vidéo !)",
            "stats_limit_exceeded": " (Limite dépassée !)",
            "limit_reached": "Limite atteinte ! Exécution des actions...",
            "time_expired": "Temps écoulé ! Exécution des actions...",
            "timer_stopped": "Minuteur arrêté.",
            "unlimited": "Illimité",
            "cancelled": "Annulé",
            "theme_label": "Mode de couleur :",
            "theme_light": "Mode clair",
            "theme_night": "Mode nuit",
            "theme_system": "Par défaut du système"
        },
        "ZH": {
            "title": "防沉迷与计时器",
            "subtitle": "保护你的时间免受分心视频的干扰！",
            "settings": "设置",
            "time_limit": "时间限制（分钟）：",
            "time_placeholder": "例如 15",
            "video_limit": "视频限制（0 = 关闭）：",
            "video_placeholder": "例如 5",
            "actions_label": "超时后的操作",
            "close_browser": "超时后关闭浏览器（Chrome, Edge, Firefox）",
            "standby": "之后将电脑置于待机（休眠）模式",
            "btn_done": "完成",
            "btn_start_timer": "启动计时器",
            "btn_stop_timer": "停止",
            "countdown_default": "00:00:00",
            "stats_videos": "已看视频：{count} / {limit}",
            "stats_last_video": "（最后一个视频！）",
            "stats_limit_exceeded": "（超出限制！）",
            "limit_reached": "达到限制！正在执行操作...",
            "time_expired": "时间已到！正在执行操作...",
            "timer_stopped": "计时器已停止。",
            "unlimited": "无限制",
            "cancelled": "已取消",
            "theme_label": "颜色模式：",
            "theme_light": "浅色模式",
            "theme_night": "暗黑模式",
            "theme_system": "系统默认"
        },
        "RU": {
            "title": "Анти-Думскроллинг и Таймер",
            "subtitle": "Защитите свое время от отвлекающих видео!",
            "settings": "Настройки",
            "time_limit": "Лимит времени (минут):",
            "time_placeholder": "например, 15",
            "video_limit": "Лимит видео (0 = выкл):",
            "video_placeholder": "например, 5",
            "actions_label": "Действия при истечении",
            "close_browser": "Закрыть браузер при истечении (Chrome, Edge, Firefox)",
            "standby": "Перевести ПК в режим ожидания (Standby) после этого",
            "btn_done": "Готово",
            "btn_start_timer": "Запустить таймер",
            "btn_stop_timer": "Остановить",
            "countdown_default": "00:00:00",
            "stats_videos": "Просмотрено видео: {count} / {limit}",
            "stats_last_video": " (Последнее видео!)",
            "stats_limit_exceeded": " (Лимит превышен!)",
            "limit_reached": "Лимит достигнут! Выполнение действий...",
            "time_expired": "Время истекло! Выполнение действий...",
            "timer_stopped": "Таймер остановлен.",
            "unlimited": "Безлимитно",
            "cancelled": "Отменено",
            "theme_label": "Цветовой режим:",
            "theme_light": "Светлая тема",
            "theme_night": "Ночная тема",
            "theme_system": "Системный по умолчанию"
        }
    }

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Anti-Doomscroll & Timer")
        self.geometry("480x460")
        self.resizable(False, False)

        # Config file path — use the directory of the executable when frozen (PyInstaller),
        # otherwise use the script's directory
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(base_dir, "config.json")

        # App state variables
        self.is_running = False
        self.time_left = 0      # in seconds
        self.total_time = 0     # in seconds
        self.video_count = 0
        self.video_limit = 0
        self.seen_urls = set()

        # Load persisted settings
        self.load_config()
        ctk.set_appearance_mode(self.saved_theme)
        
        # Communication queue between socket thread and GUI main thread
        self.msg_queue = queue.Queue()

        # Check if port 9005 is already in use (another instance running)
        if self._is_port_in_use(9005):
            messagebox.showerror(
                "Anti-Doomscroll",
                "Die App läuft bereits!\nPort 9005 ist bereits belegt.\n\n"
                "Bitte schließe die andere Instanz zuerst."
            )
            self.destroy()
            return

        # Start the background socket server
        self.server = SocketServer(9005, self.msg_queue)
        self.server.start()

        # Setup UI
        self.setup_ui()

        # Start polling the queue for messages from the browser
        self.poll_queue()

        # Global event binding to close the language dropdown when clicking outside
        self.bind_all("<Button-1>", self.check_click_outside)

    @staticmethod
    def _is_port_in_use(port):
        """Check if a port is already in use by trying to connect to it."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(('127.0.0.1', port))
                return True  # Connection succeeded — something is already listening
        except (ConnectionRefusedError, OSError):
            return False  # Port is free

    def load_config(self):
        self.current_lang = "EN"
        self.saved_time_limit = "15"
        self.saved_video_limit = "5"
        self.saved_close_browser = True
        self.saved_standby = False
        self.saved_theme = "dark"
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "language" in config and config["language"] in self.TRANSLATIONS:
                        self.current_lang = config["language"]
                    self.saved_time_limit = str(config.get("time_limit", "15"))
                    self.saved_video_limit = str(config.get("video_limit", "5"))
                    self.saved_close_browser = bool(config.get("close_browser", True))
                    self.saved_standby = bool(config.get("standby", False))
                    self.saved_theme = config.get("theme", "dark")
        except Exception as e:
            print(f"[Config] Error loading config: {e}")

    def save_config(self):
        try:
            config = {
                "language": self.current_lang,
                "time_limit": self.time_entry.get(),
                "video_limit": self.video_entry.get(),
                "close_browser": self.close_browser_var.get(),
                "standby": self.standby_var.get(),
                "theme": self.saved_theme
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def setup_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Anti-Doomscroll & Timer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Schütze deine Zeit vor ablenkenden Videos!", 
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="#888888"
        )
        self.subtitle_label.pack(pady=(0, 15))

        # Language Selector Button (square box)
        self.lang_btn = ctk.CTkButton(
            self,
            text=self.current_lang,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color="#2C2C2C",
            text_color="#AAAAAA",
            border_width=1,
            border_color="#555555",
            corner_radius=4,
            command=self.toggle_lang_dropdown
        )
        self.lang_btn.place(relx=0.0, x=15, y=15, anchor="nw")

        # Custom Language Dropdown Frame
        self.lang_dropdown_frame = ctk.CTkFrame(
            self,
            fg_color="#222222",
            border_color="#3B8ED0",
            border_width=1,
            corner_radius=6
        )
        self.lang_dropdown_visible = False

        # Populate language options
        languages = [
            ("Deutsch", "DE"),
            ("English", "EN"),
            ("Français", "FR"),
            ("中文", "ZH"),
            ("Русский", "RU")
        ]
        for lang_name, lang_code in languages:
            btn = ctk.CTkButton(
                self.lang_dropdown_frame,
                text=lang_name,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#3B8ED0",
                text_color="#FFFFFF",
                anchor="w",
                height=30,
                width=110,
                corner_radius=4,
                command=lambda code=lang_code: self.select_language(code)
            )
            btn.pack(fill="x", padx=4, pady=2)

        # Settings Gear Button
        self.settings_btn = ctk.CTkButton(
            self,
            text="⚙",
            font=ctk.CTkFont(size=22),
            width=32,
            height=32,
            fg_color="transparent",
            hover_color="#2C2C2C",
            text_color="#AAAAAA",
            command=self.show_settings
        )

        # Create frames for views
        self.dashboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")

        # --- DASHBOARD VIEW ---
        # Status / Countdown Section
        self.status_frame = ctk.CTkFrame(self.dashboard_frame, fg_color=("#dbdbdb", "#1E1E1E"), height=120)
        self.status_frame.pack(fill="x", padx=15, pady=(10, 15))
        self.status_frame.pack_propagate(False)

        self.countdown_label = ctk.CTkLabel(
            self.status_frame, 
            text="00:00:00", 
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
            text_color=("#1D4ED8", "#3B8ED0")
        )
        self.countdown_label.pack(pady=(10, 2))

        self.time_progress = ctk.CTkProgressBar(self.status_frame, width=350)
        self.time_progress.set(1.0)
        self.time_progress.pack(pady=5)

        self.info_label = ctk.CTkLabel(
            self.status_frame, 
            text="", 
            font=ctk.CTkFont(size=12),
            text_color=("#555555", "#AAAAAA")
        )
        self.info_label.pack(pady=(2, 5))

        # Controls (Start/Stop button)
        self.btn_start = ctk.CTkButton(
            self.dashboard_frame, 
            text="Timer starten", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.toggle_timer,
            fg_color="#2ECC71",
            hover_color="#27AE60"
        )
        self.btn_start.pack(fill="x", padx=15, pady=(10, 15))

        # --- SETTINGS VIEW ---
        self.settings_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Einstellungen", 
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.settings_label.pack(fill="x", padx=15, pady=(10, 15))

        # Time Limit Row
        self.time_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=15, pady=5)
        self.time_lbl = ctk.CTkLabel(self.time_frame, text="Zeitlimit (Minuten):", width=130, anchor="w")
        self.time_lbl.pack(side="left")
        self.time_entry = ctk.CTkEntry(
            self.time_frame, 
            placeholder_text="z. B. 15",
            width=200
        )
        self.time_entry.insert(0, self.saved_time_limit)
        self.time_entry.pack(side="left", fill="x", expand=True)

        # Video Limit Row
        self.video_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.video_frame.pack(fill="x", padx=15, pady=5)
        self.video_lbl = ctk.CTkLabel(self.video_frame, text="Video-Limit (0 = aus):", width=130, anchor="w")
        self.video_lbl.pack(side="left")
        self.video_entry = ctk.CTkEntry(
            self.video_frame, 
            placeholder_text="z. B. 5",
            width=200
        )
        self.video_entry.insert(0, self.saved_video_limit)
        self.video_entry.pack(side="left", fill="x", expand=True)

        # Color Theme Row
        self.theme_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.theme_frame.pack(fill="x", padx=15, pady=5)
        self.theme_lbl = ctk.CTkLabel(self.theme_frame, text="Farbmodus:", width=130, anchor="w")
        self.theme_lbl.pack(side="left")
        self.theme_optionmenu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Light Mode", "Night Mode", "System Default"],
            width=200,
            command=self.change_theme
        )
        self.theme_optionmenu.pack(side="left", fill="x", expand=True)

        # Actions Label
        self.actions_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Aktionen bei Ablauf", 
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.actions_label.pack(fill="x", padx=15, pady=(15, 5))

        self.close_browser_var = tk.BooleanVar(value=self.saved_close_browser)
        self.close_browser_cb = ctk.CTkCheckBox(
            self.settings_frame, 
            text="Browser nach Ablauf schließen (Chrome, Edge, Firefox)", 
            variable=self.close_browser_var
        )
        self.close_browser_cb.pack(fill="x", padx=15, pady=5)

        self.standby_var = tk.BooleanVar(value=self.saved_standby)
        self.standby_cb = ctk.CTkCheckBox(
            self.settings_frame, 
            text="PC danach in den Energiesparmodus (Standby) versetzen", 
            variable=self.standby_var
        )
        self.standby_cb.pack(fill="x", padx=15, pady=5)

        # Done/Save Button
        self.btn_done = ctk.CTkButton(
            self.settings_frame,
            text="Fertig",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.show_dashboard,
            fg_color="#3B8ED0",
            hover_color="#2D74B3"
        )
        self.btn_done.pack(fill="x", padx=15, pady=(20, 10))

        # Apply translations & show dashboard
        self.apply_language()
        self.show_dashboard()

    def show_dashboard(self):
        self.settings_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.settings_btn.place(relx=1.0, x=-15, y=15, anchor="ne")
        
        # Save config when returning to dashboard (settings might have changed)
        if hasattr(self, "time_entry"):
            self.save_config()

    def show_settings(self):
        if self.is_running:
            return
        self.dashboard_frame.pack_forget()
        self.settings_btn.place_forget()
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def toggle_lang_dropdown(self):
        if self.is_running:
            return
        if self.lang_dropdown_visible:
            self.hide_lang_dropdown()
        else:
            self.show_lang_dropdown()

    def show_lang_dropdown(self):
        # Position right under the language button
        self.lang_dropdown_frame.place(relx=0.0, x=15, y=52, anchor="nw")
        self.lang_dropdown_frame.lift()
        self.lang_dropdown_visible = True

    def hide_lang_dropdown(self):
        self.lang_dropdown_frame.place_forget()
        self.lang_dropdown_visible = False

    def select_language(self, code):
        self.current_lang = code
        self.apply_language()
        self.hide_lang_dropdown()
        self.save_config()

    def change_theme(self, selected_val):
        t = self.TRANSLATIONS[self.current_lang]
        if selected_val == t["theme_light"]:
            theme_key = "light"
        elif selected_val == t["theme_night"]:
            theme_key = "dark"
        else:
            theme_key = "system"
            
        self.saved_theme = theme_key
        ctk.set_appearance_mode(theme_key)
        self.save_config()

    def check_click_outside(self, event):
        if not self.lang_dropdown_visible:
            return
        
        # Get coordinates relative to main window
        x = event.x_root - self.winfo_rootx()
        y = event.y_root - self.winfo_rooty()
        
        try:
            # Check dropdown frame boundaries
            fx = self.lang_dropdown_frame.winfo_x()
            fy = self.lang_dropdown_frame.winfo_y()
            fw = self.lang_dropdown_frame.winfo_width()
            fh = self.lang_dropdown_frame.winfo_height()
            
            # Check language button boundaries
            bx = self.lang_btn.winfo_x()
            by = self.lang_btn.winfo_y()
            bw = self.lang_btn.winfo_width()
            bh = self.lang_btn.winfo_height()
            
            in_dropdown = (fx <= x <= fx + fw) and (fy <= y <= fy + fh)
            in_button = (bx <= x <= bx + bw) and (by <= y <= by + bh)
            
            if not in_dropdown and not in_button:
                self.hide_lang_dropdown()
        except Exception:
            pass

    def apply_language(self):
        t = self.TRANSLATIONS[self.current_lang]
        self.lang_btn.configure(text=self.current_lang)
        self.title_label.configure(text=t["title"])
        self.subtitle_label.configure(text=t["subtitle"])
        self.settings_label.configure(text=t["settings"])
        self.time_lbl.configure(text=t["time_limit"])
        self.time_entry.configure(placeholder_text=t["time_placeholder"])
        self.video_lbl.configure(text=t["video_limit"])
        self.video_entry.configure(placeholder_text=t["video_placeholder"])
        self.theme_lbl.configure(text=t["theme_label"])
        self.actions_label.configure(text=t["actions_label"])
        self.close_browser_cb.configure(text=t["close_browser"])
        self.standby_cb.configure(text=t["standby"])
        self.btn_done.configure(text=t["btn_done"])
        
        # Update theme options and keep selection
        theme_options = [t["theme_light"], t["theme_night"], t["theme_system"]]
        self.theme_optionmenu.configure(values=theme_options)
        if self.saved_theme == "light":
            self.theme_optionmenu.set(t["theme_light"])
        elif self.saved_theme == "dark":
            self.theme_optionmenu.set(t["theme_night"])
        else:
            self.theme_optionmenu.set(t["theme_system"])
        
        if self.is_running:
            self.btn_start.configure(text=t["btn_stop_timer"])
        else:
            self.btn_start.configure(text=t["btn_start_timer"])
            self.countdown_label.configure(text=t["countdown_default"])
            
        self.update_ui_stats()

    def parse_minutes(self, text):
        nums = re.findall(r'\d+', text)
        if nums:
            return int(nums[0])
        return 15  # Fallback Default

    def parse_video_limit(self, text):
        # Match various language terms for off/disabled
        off_terms = ["aus", "kein", "off", "desactive", "关闭", "выкл"]
        text_lower = text.lower()
        if any(term in text_lower for term in off_terms):
            return 0  # No limit
        nums = re.findall(r'\d+', text)
        if nums:
            return int(nums[0])
        return 0

    def toggle_timer(self):
        if not self.is_running:
            self.start_timer()
        else:
            self.stop_timer("Abgebrochen")

    def start_timer(self):
        t = self.TRANSLATIONS[self.current_lang]
        # Parse inputs
        minutes = self.parse_minutes(self.time_entry.get())
        self.total_time = minutes * 60
        self.time_left = self.total_time
        
        self.video_limit = self.parse_video_limit(self.video_entry.get())
        self.video_count = 0
        self.seen_urls.clear()

        # Update UI state
        self.is_running = True
        self.btn_start.configure(text=t["btn_stop_timer"], fg_color="#E74C3C", hover_color="#C0392B")
        self.settings_btn.configure(state="disabled", text_color="#555555")
        self.lang_btn.configure(state="disabled", text_color="#555555")
        self.time_entry.configure(state="disabled")
        self.video_entry.configure(state="disabled")
        self.theme_optionmenu.configure(state="disabled")
        self.close_browser_cb.configure(state="disabled")
        self.standby_cb.configure(state="disabled")
        self.countdown_label.configure(text_color=("#15803D", "#2ECC71"))

        self.update_ui_stats()
        self.run_countdown()
        print(f"[Timer] Started. Time: {minutes}m, Video Limit: {self.video_limit}")

    def stop_timer(self, reason="Abgelaufen"):
        t = self.TRANSLATIONS[self.current_lang]
        self.is_running = False
        self.btn_start.configure(text=t["btn_start_timer"], fg_color="#2ECC71", hover_color="#27AE60")
        self.settings_btn.configure(state="normal", text_color="#AAAAAA")
        self.lang_btn.configure(state="normal", text_color="#AAAAAA")
        self.time_entry.configure(state="normal")
        self.video_entry.configure(state="normal")
        self.theme_optionmenu.configure(state="normal")
        self.close_browser_cb.configure(state="normal")
        self.standby_cb.configure(state="normal")
        self.countdown_label.configure(text_color=("#1D4ED8", "#3B8ED0"))
        
        if reason == "Limit":
            self.countdown_label.configure(text_color=("#B91C1C", "#E74C3C"))
            self.info_label.configure(text=t["limit_reached"], text_color=("#B91C1C", "#E74C3C"))
            self.execute_actions()
        elif reason == "Zeit":
            self.countdown_label.configure(text_color=("#B91C1C", "#E74C3C"))
            self.info_label.configure(text=t["time_expired"], text_color=("#B91C1C", "#E74C3C"))
            self.execute_actions()
        else:
            self.info_label.configure(text=t["timer_stopped"], text_color=("#555555", "#AAAAAA"))
            self.time_progress.set(1.0)
            self.countdown_label.configure(text=t["countdown_default"])

    def run_countdown(self):
        if not self.is_running:
            return

        if self.time_left <= 0:
            self.stop_timer("Zeit")
            return

        # Format and display time
        hours = self.time_left // 3600
        minutes = (self.time_left % 3600) // 60
        seconds = self.time_left % 60
        self.countdown_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update progress bar
        progress = self.time_left / self.total_time
        self.time_progress.set(progress)

        self.time_left -= 1
        self.after(1000, self.run_countdown)

    def update_ui_stats(self):
        t = self.TRANSLATIONS[self.current_lang]
        limit_str = str(self.video_limit) if self.video_limit > 0 else t["unlimited"]
        if self.video_limit > 0 and self.video_count == self.video_limit:
            self.info_label.configure(
                text=t["stats_videos"].format(count=self.video_count, limit=limit_str) + t["stats_last_video"],
                text_color=("#C2410C", "#E67E22")
            )
            self.countdown_label.configure(text_color=("#C2410C", "#E67E22"))
        elif self.video_limit > 0 and self.video_count > self.video_limit:
            self.info_label.configure(
                text=t["stats_videos"].format(count=self.video_count, limit=limit_str) + t["stats_limit_exceeded"],
                text_color=("#B91C1C", "#E74C3C")
            )
            self.countdown_label.configure(text_color=("#B91C1C", "#E74C3C"))
        else:
            self.info_label.configure(
                text=t["stats_videos"].format(count=self.video_count, limit=limit_str),
                text_color=("#555555", "#AAAAAA")
            )
            if self.is_running:
                self.countdown_label.configure(text_color=("#15803D", "#2ECC71"))

    def poll_queue(self):
        # Check if there are new URLs from the browser extension
        try:
            while True:
                url = self.msg_queue.get_nowait()
                self.handle_incoming_url(url)
        except queue.Empty:
            pass
        self.after(100, self.poll_queue)

    def handle_incoming_url(self, url):
        if not self.is_running:
            print(f"[App] Ignored URL (timer not running): {url}")
            return

        if url not in self.seen_urls:
            self.seen_urls.add(url)
            self.video_count += 1
            print(f"[App] New Video detected: {url}. Total: {self.video_count}")
            self.update_ui_stats()

            # Check video limit
            if self.video_limit > 0 and self.video_count > self.video_limit:
                print(f"[App] Video limit exceeded ({self.video_limit} videos allowed, got {self.video_count})!")
                self.stop_timer("Limit")

    def execute_actions(self):
        # 1. Close browsers if checked
        if self.close_browser_var.get():
            print("[App] Closing browsers...")
            self.close_browsers()

        # 2. Put PC to standby if checked
        if self.standby_var.get():
            print("[App] Putting PC to standby...")
            self.put_to_standby()

    def close_browsers(self):
        browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe"]
        for browser in browsers:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", browser], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                print(f"Failed to kill {browser}: {e}")

    def put_to_standby(self):
        # Powershell command for entering sleep mode
        cmd = 'powershell -Command "Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"'
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error putting to standby: {e}")

    def destroy(self):
        # Stop the background socket server when window closes
        self.server.stop()
        super().destroy()


if __name__ == "__main__":
    app = AntiDoomscrollApp()
    app.mainloop()
