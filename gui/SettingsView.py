import customtkinter as ctk

from gui.SettingsManager import SettingsManager


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate, scan_duration, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.scan_duration = scan_duration
        self.theme = theme
        self.settings_manager=SettingsManager()
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="⚙ Settings",
                     font=("Arial", 28, "bold")).pack(pady=(30, 20))

        settings_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        settings_container.pack(expand=True, fill="both", padx=30, pady=(0, 20))

        self.create_section(settings_container, "Scan Configuration")

        scan_frame = ctk.CTkFrame(settings_container, fg_color=self.theme["bg_card"], corner_radius=12)
        scan_frame.pack(fill="x", pady=(0, 15), padx=5)

        dur_row = ctk.CTkFrame(scan_frame, fg_color="transparent")
        dur_row.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(dur_row, text="Scan Duration (seconds)",
                     font=("Arial", 14)).pack(side="left")

        current_dur = self.scan_duration["scan_duration"]
        self.duration_var = ctk.IntVar(value=current_dur)

        self.duration_slider = ctk.CTkSlider(dur_row, from_=5, to=30,
                                             number_of_steps=25,
                                             variable=self.duration_var,
                                             progress_color=self.theme["accent"],
                                             command=self.on_duration_change)
        self.duration_slider.pack(side="right", padx=(20, 10))

        self.duration_display = ctk.CTkLabel(dur_row, text=f"{current_dur}s",
                                             font=("Arial", 14, "bold"),
                                             text_color=self.theme["accent"])
        self.duration_display.pack(side="right")

        self.duration_slider.configure(
            command=self.on_duration_change
        )

        self.create_section(settings_container, "Appearance")

        appearance_frame = ctk.CTkFrame(settings_container, fg_color=self.theme["bg_card"], corner_radius=12)
        appearance_frame.pack(fill="x", pady=(0, 15), padx=5)

        theme_row = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_row.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(theme_row, text="Theme",
                     font=("Arial", 14)).pack(side="left")

        current_theme_saved = self.settings_manager.get("theme_mode").capitalize()

        self.theme_menu = ctk.CTkOptionMenu(theme_row,
                                            values=["Dark", "Light"],
                                            command=self.change_theme,
                                            button_color=self.theme["accent"])
        self.theme_menu.pack(side="right")
        self.theme_menu.set(current_theme_saved)
        self.theme_menu.pack(side="right", padx=20)

        self.create_section(settings_container, "Data Management")

        data_frame = ctk.CTkFrame(settings_container, fg_color=self.theme["bg_card"], corner_radius=12)
        data_frame.pack(fill="x", pady=(0, 15), padx=5)

        export_row = ctk.CTkFrame(data_frame, fg_color="transparent")
        export_row.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(export_row, text="Export your data as CSV",
                     font=("Arial", 14)).pack(side="left")

        ctk.CTkButton(export_row, text="📁  Export", command=self.export_data,
                      fg_color=self.theme["accent"], hover_color="#5a6ed0",
                      width=120, height=35).pack(side="right")

        clear_row = ctk.CTkFrame(data_frame, fg_color="transparent")
        clear_row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(clear_row, text="Delete all stored data",
                     font=("Arial", 14)).pack(side="left")

        ctk.CTkButton(clear_row, text="🗑  Clear All", command=self.confirm_clear,
                      fg_color="#F44336", hover_color="#D32F2F",
                      width=120, height=35).pack(side="right")

        self.create_section(settings_container, "About")

        about_frame = ctk.CTkFrame(settings_container, fg_color=self.theme["bg_card"], corner_radius=12)
        about_frame.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(about_frame, text="Emotion Journal v1.0",
                     font=("Arial", 14, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(about_frame, text="Built with Python, CustomTkinter, DeepFace & OpenCV",
                     font=("Arial", 12), text_color=self.theme["text_dim"]).pack(pady=(0, 15))




    def create_section(self, parent, title):
        ctk.CTkLabel(parent, text=title, font=("Arial", 18, "bold"),
                     text_color=self.theme["accent"]).pack(anchor="w", padx=5, pady=(15, 8))

    def change_theme(self, value):
        new_mode=value.lower()
        ctk.set_appearance_mode(new_mode)
        self.settings_manager.set("theme_mode", new_mode)

    def export_data(self):
        print("Export data - to be implemented")

    def confirm_clear(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.configure(fg_color=self.theme["bg_main"])

        ctk.CTkLabel(dialog, text="⚠️  Are you sure?",
                     font=("Arial", 18, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="This will permanently delete all your data.",
                     font=("Arial", 13), text_color=self.theme["text_dim"]).pack(pady=5)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                      fg_color=self.theme["border"], width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Delete", command=lambda: self.clear_data(dialog),
                      fg_color="#F44336", hover_color="#D32F2F",
                      width=100).pack(side="left", padx=10)

    def on_duration_change(self, value):
        seconds = int(float(value))
        self.duration_display.configure(text=f"{seconds}s")
        self.settings_manager.set("scan_duration", seconds)
        self.scan_duration["scan_duration"] = seconds

    def clear_data(self, dialog):
        self.db.clear_all()
        dialog.destroy()
        print("Data cleared - to be implemented")
