import customtkinter as ctk
from datetime import datetime, timedelta
import calendar


class CalendarView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.theme = theme

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        self.emotion_colors = {
            "happy": "#4CAF50", "sad": "#2196F3", "angry": "#F44336",
            "surprise": "#FF9800", "fear": "#9C27B0", "disgust": "#795548",
            "neutral": "#607D8B"
        }
        self.emotion_emojis = {
            "happy": "😊", "sad": "😢", "angry": "😠",
            "surprise": "😲", "fear": "😨", "disgust": "🤢",
            "neutral": "😐"
        }

        self.build_ui()

    def build_ui(self):
        self.clear()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkButton(header, text="◀", command=self.prev_month,
                      fg_color=self.theme["border"], hover_color="#444444",
                      width=40, height=40, font=("Arial", 18)).pack(side="left")

        month_name = calendar.month_name[self.current_month]
        self.month_label = ctk.CTkLabel(header,
                                        text=f"📅  {month_name} {self.current_year}",
                                        font=("Arial", 26, "bold"))
        self.month_label.pack(side="left", expand=True)

        ctk.CTkButton(header, text="▶", command=self.next_month,
                      fg_color=self.theme["border"], hover_color="#444444",
                      width=40, height=40, font=("Arial", 18)).pack(side="right")

        legend_frame = ctk.CTkFrame(self, fg_color=self.theme["bg_card"], corner_radius=10)
        legend_frame.pack(fill="x", padx=30, pady=10)

        for emotion, emoji in self.emotion_emojis.items():
            color = self.emotion_colors[emotion]
            item = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item.pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(item, text=f"{emoji} {emotion.capitalize()}",
                         font=("Arial", 14), text_color=color).pack()


        days_header = ctk.CTkFrame(self, fg_color="transparent")
        days_header.pack(fill="x", padx=30, pady=(15, 5))
        for i in range(7):
            days_header.grid_columnconfigure(i, weight=1)

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, name in enumerate(day_names):
            ctk.CTkLabel(days_header, text=name, font=("Arial", 17, "bold"),
                         text_color=self.theme["text_dim"]).grid(row=0, column=i)


        self.calendar_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_grid.pack(expand=True, fill="both", padx=30, pady=(5, 20))
        for i in range(7):
            self.calendar_grid.grid_columnconfigure(i, weight=1)

        self.render_calendar()

    def render_calendar(self):
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        month_data = self.db.get_emotions_for_month(self.current_year, self.current_month)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()

        for row_idx, week in enumerate(cal):
            self.calendar_grid.grid_rowconfigure(row_idx, weight=1)
            for col_idx, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.calendar_grid, text="").grid(
                        row=row_idx, column=col_idx, padx=3, pady=3)
                    continue

                date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                emotion = month_data.get(date_str)

                is_today = (day == today.day and self.current_month == today.month
                            and self.current_year == today.year)

                if emotion:
                    bg_color = self.emotion_colors.get(emotion, "#333333")
                    emoji = self.emotion_emojis.get(emotion, "")
                    display_text = f"{emoji}\n{day}"
                    text_color = "white"
                elif is_today:
                    bg_color = self.theme["accent"]
                    display_text = f"📍\n{day}"
                    text_color = "white"
                else:
                    bg_color = self.theme["bg_card"]
                    display_text = str(day)
                    text_color = self.theme["text_dim"]

                cell = ctk.CTkFrame(self.calendar_grid, fg_color=bg_color,
                                    corner_radius=10, height=65)
                cell.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
                cell.grid_propagate(False)

                ctk.CTkLabel(cell, text=display_text, font=("Arial", 17, "bold"),
                             text_color=text_color).place(relx=0.5, rely=0.5, anchor="center")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.build_ui()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.build_ui()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()