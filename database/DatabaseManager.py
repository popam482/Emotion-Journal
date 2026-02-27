import sqlite3
from datetime import datetime, timedelta
from collections import Counter


class DatabaseManager:
    def __init__(self, db_path="data/journal.db"):
        self.db_path = db_path
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emotion_logs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    emotion TEXT,
                    confidence REAL
                );
            """)
            conn.commit()

    def save_emotion(self, emotion, confidence=1.0):
        with self.get_connection() as conn:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO emotion_logs (timestamp, emotion, confidence) VALUES (?, ?, ?)",
                (date, emotion, confidence)
            )
            conn.commit()

    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM emotion_logs")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT emotion FROM emotion_logs ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            last_emotion = row[0] if row else "N/A"

            return {"total": total, "last_emotion": last_emotion}

    def get_emotions_for_month(self, year, month):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(timestamp) as day, emotion
                FROM emotion_logs
                WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
                ORDER BY timestamp
            """, (str(year), f"{month:02d}"))

            rows = cursor.fetchall()

        days = {}
        for day_str, emotion in rows:
            if day_str not in days:
                days[day_str] = []
            days[day_str].append(emotion)

        result = {}
        for day_str, emotions in days.items():
            counts = Counter(emotions)
            result[day_str] = counts.most_common(1)[0][0]

        return result

    def get_streak(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(timestamp) as day, emotion
                FROM emotion_logs
                ORDER BY timestamp DESC
            """)
            rows = cursor.fetchall()

        if not rows:
            return {"emotion": None, "count": 0}

        daily = {}
        for day_str, emotion in rows:
            if day_str not in daily:
                daily[day_str] = []
            daily[day_str].append(emotion)

        sorted_days = sorted(daily.keys(), reverse=True)

        first_day_emotions = Counter(daily[sorted_days[0]])
        current_emotion = first_day_emotions.most_common(1)[0][0]

        streak_count = 0
        for day_str in sorted_days:
            day_dominant = Counter(daily[day_str]).most_common(1)[0][0]
            if day_dominant == current_emotion:
                streak_count += 1
            else:
                break

        return {"emotion": current_emotion, "count": streak_count}

    def get_weekly_summary(self):

        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        last_week_start = week_start - timedelta(days=7)

        def happy_percent(start, end):
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT emotion FROM emotion_logs
                    WHERE DATE(timestamp) >= ? AND DATE(timestamp) < ?
                """, (str(start), str(end)))
                emotions = [row[0] for row in cursor.fetchall()]
            if not emotions:
                return None
            return int((emotions.count("happy") / len(emotions)) * 100)

        current_happy = happy_percent(week_start, today + timedelta(days=1))
        last_happy = happy_percent(last_week_start, week_start)

        if current_happy is not None and last_happy is not None:
            return {"change": current_happy - last_happy}
        return {"change": None}

    def has_checkin_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM emotion_logs WHERE DATE(timestamp) = ?",
                (today,)
            )
            return cursor.fetchone()[0] > 0

    def export_to_csv(self, filepath):
        import csv
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, emotion, confidence FROM emotion_logs ORDER BY timestamp"
            )
            rows = cursor.fetchall()

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Timestamp", "Emotion", "Confidence"])
            writer.writerows(rows)

    def clear_all(self):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM emotion_logs")
            conn.commit()