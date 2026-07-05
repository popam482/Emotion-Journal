import customtkinter as ctk
from analyzer.EmotionAnalyzer import EmotionAnalyzer
from database.DatabaseManager import DatabaseManager
from gui.HomeView import HomeView
from gui.ScanView import ScanView
from gui.CalendarView import CalendarView
from gui.AlertsView import AlertsView
from gui.SettingsManager import SettingsManager
from gui.SettingsView import SettingsView
from gui.StatsView import StatsView
from gui.ChatView import ChatView


class AppInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.analyzer = EmotionAnalyzer()
        self.db = DatabaseManager()
        self.settings_manager = SettingsManager()
        self.scan_duration = {"scan_duration": self.settings_manager.get("scan_duration")}

        saved_theme = self.settings_manager.get("theme_mode")

        self.theme = {
            "sidebar": ("#d1d1d1", "#1a1a1a"),
            "bg_main": ("#ebebeb", "#242424"),
            "bg_card": ("#ffffff", "#2b2b2b"),
            "text_main": ("#1a1a1a", "#ffffff"),
            "text_dim": ("#555555", "#aaaaaa"),
            "border": ("#cccccc", "#3d3d3d"),
            "accent": ("#6c82f0", "#6c82f0")
        }

        self.title("Emotion Journal")
        self.geometry("1280x720")
        ctk.set_appearance_mode(saved_theme)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.activity_bar = ctk.CTkFrame(self, corner_radius=0, fg_color=self.theme["sidebar"], width=80)
        self.activity_bar.grid(row=0, column=0, sticky="nsew")
        self.activity_bar.grid_propagate(False)

        btn_style = {
            "width": 50,
            "height": 50,
            "corner_radius": 12,
            "font": ("Arial", 22),
            "fg_color": self.theme["accent"],
            "hover_color": "#5a6ed0"
        }

        ctk.CTkButton(self.activity_bar, text="🏠", command=lambda: self.navigate("home"), **btn_style).pack(
            pady=(30, 15), padx=10)

        ctk.CTkButton(self.activity_bar, text="📅", command=lambda: self.navigate("calendar"), **btn_style).pack(pady=15,
                                                                                                                padx=10)
        ctk.CTkButton(self.activity_bar, text="🔔", command=lambda: self.navigate("alerts"), **btn_style).pack(pady=15, padx=10)

        ctk.CTkButton(self.activity_bar, text="📊", command=lambda: self.navigate("stats"), **btn_style).pack(pady=15, padx=10)

        ctk.CTkButton(self.activity_bar, text="💬", command=lambda: self.navigate("chat"), **btn_style).pack(pady=15, padx=10)

        ctk.CTkButton(self.activity_bar, text="⚙️", command=lambda: self.navigate("settings"), **btn_style).pack(
            side="bottom", pady=20, padx=10)

        self.content_area = ctk.CTkFrame(self, corner_radius=15, fg_color=self.theme["bg_main"])
        self.content_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.current_view = None
        self.navigate("home")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def navigate(self, page):
        if self.current_view:
            self.current_view.destroy()

        if page == "home":
            self.current_view = HomeView(self.content_area, self.db, self.navigate, self.theme)
        elif page == "scan":
            self.current_view = ScanView(self.content_area, self.analyzer, self.db, self.navigate, self.scan_duration,
                                         self.theme)
        elif page == "calendar":
            self.current_view = CalendarView(self.content_area, self.db, self.navigate, self.theme)
        elif page == "alerts":
            self.current_view = AlertsView(self.content_area, self.db, self.navigate, self.theme)
        elif page=="stats":
            self.current_view = StatsView(self.content_area, self.db, self.navigate, self.theme)
        elif page=="chat":
            self.current_view = ChatView(self.content_area, self.db, self.navigate, self.theme)

        elif page == "settings":
            self.current_view = SettingsView(self.content_area, self.db, self.navigate, self.scan_duration, self.theme, self.settings_manager)

        self.current_view.pack(expand=True, fill="both")

    def on_close(self):
        self.analyzer.release()
        self.destroy()