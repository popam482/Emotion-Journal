from datetime import datetime
from .constants import emotion_emojis, emotion_colors
import customtkinter as ctk
import random
import json
import os


class AlertsView(ctk.CTkFrame):

    def __init__(self, parent, db, on_navigate, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.theme = theme

        tips_path = os.path.join("data", "emotion_tips.json")
        with open(tips_path, "r", encoding="utf-8") as f:
            self.emotion_tips = json.load(f)

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="🔔  Notifications & Insights",
                     font=("Arial", 28, "bold")).pack(pady=(30, 20))

        alerts_container = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                  corner_radius=10)
        alerts_container.pack(expand=True, fill="both", padx=30, pady=(0, 20))

        alerts = self.generate_alerts()

        if not alerts:
            ctk.CTkLabel(alerts_container, text="✅  No alerts right now!",
                         font=("Arial", 18), text_color="#4CAF50").pack(pady=40)
            ctk.CTkLabel(alerts_container,
                         text="Keep doing check-ins to receive personalized insights.",
                         font=("Arial", 14), text_color=self.theme["text_dim"]).pack()
        else:
            for alert in alerts:
                self.create_alert_card(alerts_container, alert)

    def generate_alerts(self):
        alerts = []
        alerts += self._build_emotion_tip()
        alerts += self._build_journal_insight()
        alerts += self._build_streak_alert()
        alerts += self._build_weekly_insights()
        alerts += self._build_time_pattern()
        alerts += self._build_reminders()
        return alerts

    # --- metode private ---

    def _build_emotion_tip(self):
        alerts = []
        dominant_emotion = self.db.get_dominant_emotion_for_today()
        if dominant_emotion:
            dominant_emotion = dominant_emotion.lower()
            if dominant_emotion in self.emotion_tips:
                tip = random.choice(self.emotion_tips[dominant_emotion])
                tip_color = {
                    "happy": "#4CAF50", "sad": "#2196F3", "angry": "#F44336",
                    "surprise": "#FF9800", "fear": "#9C27B0",
                    "disgust": "#795548", "neutral": "#607D8B"
                }.get(dominant_emotion, "#6c82f0")
                alerts.append({
                    "type": "tip",
                    "icon": tip["icon"],
                    "title": tip["title"],
                    "message": tip["message"],
                    "color": tip_color
                })
        return alerts

    def _build_journal_insight(self):
        alerts = []
        today_str = datetime.today().strftime("%Y-%m-%d")
        journal_entry = self.db.get_note_for_date(today_str)

        if journal_entry:
            alerts.append({
                "type": "insight",
                "icon": "✍️",
                "title": "Reflection Benefit",
                "message": "Nice job taking a moment to check in with yourself today. You tend to feel happier on days when you write things down, and keeping this habit going can really support your well-being.",
                "color": "#ca03fc"
            })
        else:
            alerts.append({
                "type": "insight",
                "icon": "✍️",
                "title": "Reflection Benefit",
                "message": "You tend to feel happier on days when you journal. Want to take a minute to write how you're feeling today? Even a few words can help.",
                "color": "#ca03fc"
            })
        return alerts

    def _build_streak_alert(self):
        alerts = []
        streak = self.db.get_streak()
        emoji = emotion_emojis.get(streak["emotion"], "🤔")

        if streak["count"] >= 3:
            alerts.append({
                "type": "warning" if streak["emotion"] in ["sad", "angry", "fear"] else "info",
                "icon": emoji,
                "title": f"{streak['count']}-Day {streak['emotion'].capitalize()} Streak",
                "message": f"You've been feeling {streak['emotion']} for {streak['count']} consecutive days.",
                "color": "#F44336" if streak["emotion"] in ["sad", "angry", "fear"] else "#FF9800"
            })
        else:
            alerts.append({
                "type": "insights",
                "icon": emoji,
                "title": "Build a 3-day journaling streak",
                "message": "Try journaling 3 days in a row to unlock new insights and you will get personalised insights based on your emotions.",
                "color": "#ff5c5c"
            })
        return alerts

    def _build_weekly_insights(self):
        alerts = []
        weekly = self.db.get_weekly_summary()
        weekly_days = self.db.get_best_and_worst_day()
        mood_variability = self.db.get_mood_variability()

        if weekly_days:
            alerts.append({
                "type": "insight",
                "icon": "🌟",
                "title": "Best day this week",
                "message": f"Your best emotional day this week was {weekly_days['best_day']}",
                "color": "#f5e10a"
            })
            alerts.append({
                "type": "insight",
                "icon": "⚠️",
                "title": "Toughest Day This Week",
                "message": f"You struggled the most emotionally on {weekly_days['worst_day']}.",
                "color": "#FF9800"
            })

        if mood_variability == "stable":
            alerts.append({
                "type": "insight",
                "icon": "🧘",
                "title": "Stable mood",
                "message": "Your emotional state has been stable this week.",
                "color": "#6be3e1"
            })
        else:
            alerts.append({
                "type": "insight",
                "icon": "↘️",
                "title": "Mood variability",
                "message": "Your emotions fluctuated this week.",
                "color": "#ffad1f"
            })

        if weekly.get("change") is not None:
            if weekly["change"] > 0:
                alerts.append({
                    "type": "positive",
                    "icon": "📈",
                    "title": "Mood Improvement!",
                    "message": f"You've been {weekly['change']}% happier this week compared to last week!",
                    "color": "#4CAF50"
                })
            elif weekly["change"] < -15:
                alerts.append({
                    "type": "warning",
                    "icon": "📉",
                    "title": "Mood Decline Detected",
                    "message": f"Your happiness decreased by {abs(weekly['change'])}% compared to last week.",
                    "color": "#FF9800"
                })

        return alerts

    def _build_time_pattern(self):
        alerts = []
        pattern = self.db.get_time_of_the_day_mood()
        if pattern:
            best = pattern["best"]
            worst = pattern["worst"]
            text = {
                "morning": "in the morning",
                "afternoon": "in the afternoon",
                "evening": "in the evening",
                "night": "in the night"
            }
            alerts.append({
                "type": "insight",
                "icon": "⏰",
                "title": "Mood pattern detected",
                "message": f"You tend to feel better {text[best]}.",
                "color": "#1fff3d"
            })
            alerts.append({
                "type": "insight",
                "icon": "⏰",
                "title": "Mood pattern detected",
                "message": f"You tend to feel worse {text[worst]}.",
                "color": "#ff1f1f"
            })
        return alerts

    def _build_reminders(self):
        alerts = []
        stats = self.db.get_stats()

        if not self.db.has_checkin_today():
            alerts.append({
                "type": "reminder",
                "icon": "⏰",
                "title": "Daily Reminder",
                "message": "You haven't done a check-in today. Take a moment to reflect!",
                "color": "#6c82f0"
            })

        if stats["total"] > 0 and stats["total"] % 10 == 0:
            alerts.append({
                "type": "achievement",
                "icon": "🏆",
                "title": f"Milestone: {stats['total']} Check-ins!",
                "message": "Great job staying consistent with your emotional tracking!",
                "color": "#FFD700"
            })

        return alerts

    def create_alert_card(self, parent, alert):
        card = ctk.CTkFrame(parent, fg_color=self.theme["bg_card"], corner_radius=12,
                            border_width=1, border_color=alert["color"])
        card.pack(fill="x", pady=8, padx=5)

        accent = ctk.CTkFrame(card, fg_color=alert["color"], width=4, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(10, 0), pady=10)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(header, text=f"{alert['icon']}  {alert['title']}",
                     font=("Arial", 16, "bold"),
                     text_color=alert["color"]).pack(side="left")

        ctk.CTkLabel(content, text=alert["message"],
                     font=("Arial", 13), text_color=self.theme["text_dim"],
                     wraplength=1000, justify="left").pack(anchor="w", pady=(5, 0))
