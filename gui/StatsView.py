import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime


MOOD_SCORE = {
    "happy": 6, "surprise": 5, "neutral": 4,
    "fear": 3, "disgust": 2, "sad": 1, "angry": 0
}

EMOTION_COLORS = {
    "happy": "#4CAF50", "surprise": "#FF9800", "neutral": "#607D8B",
    "fear": "#9C27B0", "disgust": "#795548", "sad": "#2196F3", "angry": "#F44336"
}


class StatsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.theme = theme
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="📊  Mood Overview",
                     font=("Arial", 28, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self, text="Your emotional trend over the last 30 days",
                     font=("Arial", 14), text_color=self.theme["text_dim"]).pack(pady=(0, 20))

        data = self.db.get_mood_graph_data(days=30)

        if not data:
            ctk.CTkLabel(self, text="📭  Not enough data yet.",
                         font=("Arial", 18), text_color=self.theme["text_dim"]).pack(pady=60)
            ctk.CTkLabel(self, text="Complete a few check-ins to see your mood graph.",
                         font=("Arial", 13), text_color=self.theme["text_dim"]).pack()
            return

        dates = [datetime.strptime(d[0], "%Y-%m-%d") for d in data]
        scores = [d[2] for d in data]
        emotions = [d[1] for d in data]
        colors = [EMOTION_COLORS.get(e, "#6c82f0") for e in emotions]

        is_dark = ctk.get_appearance_mode() == "Dark"
        bg = "#242424" if is_dark else "#ebebeb"
        card_bg = "#2b2b2b" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#1a1a1a"
        dim_color = "#aaaaaa" if is_dark else "#555555"
        grid_color = "#3d3d3d" if is_dark else "#cccccc"

        fig = Figure(figsize=(8, 3.5), dpi=100, facecolor=card_bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(card_bg)

        ax.fill_between(dates, scores, alpha=0.15, color="#6c82f0")
        ax.plot(dates, scores, color="#6c82f0", linewidth=2.5, zorder=2)
        ax.scatter(dates, scores, c=colors, s=60, zorder=3, edgecolors=card_bg, linewidths=1.5)

        ax.set_ylim(-0.5, 6.5)
        ax.set_yticks(list(MOOD_SCORE.values()))
        ax.set_yticklabels(
            ["😊 Happy", "😲 Surprise", "😐 Neutral", "😨 Fear", "😣 Disgust", "😢 Sad", "😠 Angry"],
            fontsize=12, color=text_color
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=30)
        ax.tick_params(axis="x", colors=dim_color, labelsize=12)
        ax.tick_params(axis="y", colors=dim_color)
        for spine in ax.spines.values():
            spine.set_edgecolor(grid_color)
        ax.yaxis.grid(True, color=grid_color, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        fig.tight_layout(pad=1.5)

        graph_frame = ctk.CTkFrame(self, fg_color=card_bg, corner_radius=12)
        graph_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30, pady=(0, 20))

        from collections import Counter
        most_common = Counter(emotions).most_common(1)[0][0]
        avg_score = round(sum(scores) / len(scores), 1)
        avg_label = ["Angry", "Sad", "Disgust", "Fear", "Neutral", "Surprise", "Happy"][round(avg_score)]

        for label, value in [
            ("📅  Days tracked", str(len(data))),
            ("😊  Most frequent", most_common.capitalize()),
            ("📈  Average mood", avg_label),
        ]:
            card = ctk.CTkFrame(summary_frame, fg_color=card_bg, corner_radius=10)
            card.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"),
                         text_color="#6c82f0").pack(pady=(10, 2))
            ctk.CTkLabel(card, text=label, font=("Arial", 14),
                         text_color=dim_color).pack(pady=(0, 10))