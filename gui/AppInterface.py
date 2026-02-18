import customtkinter as ctk
from analyzer.EmotionAnalyzer import EmotionAnalyzer
from database.DatabaseManager import DatabaseManager
from gui.HomeView import HomeView
from gui.ScanView import ScanView
from gui.CalendarView import CalendarView
from gui.AlertsView import AlertsView
from gui.SettingsView import SettingsView


class AppInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.analyzer = EmotionAnalyzer()
        self.db = DatabaseManager()
        self.scan_duration={"scan_duration": 10}

        self.title("Emotion Journal")
        self.geometry("1280x720")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.activity_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a", width=80)
        self.activity_bar.grid(row=0, column=0, sticky="nsew")
        self.activity_bar.grid_propagate(False)

        btn_style = {"width": 50, "height": 50, "corner_radius": 12,
                     "font": ("Arial", 22), "fg_color": "#6c82f0", "hover_color": "#5a6ed0"}

        ctk.CTkButton(self.activity_bar, text="🏠",
                      command=lambda: self.navigate("home"), **btn_style).pack(pady=(30, 15), padx=10)
        ctk.CTkButton(self.activity_bar, text="📅",
                      command=lambda: self.navigate("calendar"), **btn_style).pack(pady=15, padx=10)
        ctk.CTkButton(self.activity_bar, text="🔔",
                      command=lambda: self.navigate("alerts"), **btn_style).pack(pady=15, padx=10)
        ctk.CTkButton(self.activity_bar, text="⚙️",
                      command=lambda: self.navigate("settings"), **btn_style).pack(side="bottom", pady=20, padx=10)

        self.theme = {
            "bg_main": ("#ebebeb", "#242424"),
            "bg_card": ("#ffffff", "#2b2b2b"),
            "text_main": ("#1a1a1a", "#ffffff"),
            "text_dim": ("#555555", "#aaaaaa"),
            "border": ("#cccccc", "#3d3d3d"),
            "accent": ("#6c82f0", "#6c82f0")
        }

        self.content_area = ctk.CTkFrame(self, corner_radius=15, fg_color="#242424")
        self.content_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.current_view = None
        self.navigate("home")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def navigate(self, page):
        if self.current_view:
            self.current_view.destroy()

        views = {
            "home": lambda: HomeView(self.content_area, self.db, self.navigate),
            "scan": lambda: ScanView(self.content_area, self.analyzer, self.db, self.navigate, self.scan_duration),
            "calendar": lambda: CalendarView(self.content_area, self.db, self.navigate),
            "alerts": lambda: AlertsView(self.content_area, self.db, self.navigate),
            "settings": lambda: SettingsView(self.content_area, self.db, self.navigate, self.scan_duration),
        }

        self.current_view = views[page]()
        self.current_view.pack(expand=True, fill="both")

    def on_close(self):
        self.analyzer.release()
        self.destroy()