import sqlite3
from datetime import datetime, timedelta
from collections import Counter, defaultdict

emotion_score = {
    "happy": 5,
    "surprise": 4,
    "neutral": 3,
    "sad": 2,
    "fear": 2,
    "angry": 1,
    "disgust": 1
}

periods = {
    "morning": [],
    "afternoon": [],
    "evening": [],
    "night": []
}

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
                    confidence REAL,
                    notes TEXT DEFAULT ''
                );
            """)
            try:
                conn.execute("ALTER TABLE emotion_logs ADD COLUMN notes TEXT DEFAULT ''")
            except Exception:
                pass
            conn.commit()

    def save_emotion(self, emotion, confidence=1.0):
        with self.get_connection() as conn:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = conn.execute(
                "INSERT INTO emotion_logs (timestamp, emotion, confidence) VALUES (?, ?, ?)",
                (date, emotion, confidence)
            )
            conn.commit()
            return cursor.lastrowid

    def save_note(self, log_id, note):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE emotion_logs SET notes = ? WHERE id = ?",
                (note, log_id)
            )
            conn.commit()

    def get_note_for_date(self, date_str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT notes FROM emotion_logs WHERE DATE(timestamp) = ? AND notes != '' ORDER BY timestamp DESC LIMIT 1",
                (date_str,)
            )
            row = cursor.fetchone()
            return row[0] if row else ""

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

    def get_best_and_worst_day(self):
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        SELECT DATE(timestamp), emotion
                        FROM emotion_logs
                        WHERE DATE(timestamp) >= ?
                    """, (str(week_start),))
            rows = cursor.fetchall()

        if not rows:
            return None

        days = defaultdict(list)

        for day, emotion in rows:
            if emotion in emotion_score:
                days[day].append(emotion_score[emotion])

        if not days:
            return None

        day_scores = {
            day: sum(scores) / len(scores)
            for day, scores in days.items()
        }

        best_day = max(day_scores, key=day_scores.get)
        worst_day = min(day_scores, key=day_scores.get)

        return {
            "best_day": best_day,
            "worst_day": worst_day
        }

    def get_mood_variability(self):
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT emotion FROM emotion_logs
                WHERE DATE(timestamp) >= ?
            """, (str(week_start),))

            emotions = [row[0] for row in cursor.fetchall()]

        if len(emotions) < 4:
            return None

        unique = len(set(emotions))

        if unique <= 2:
            return "stable"
        else:
            return "variable"

    def get_time_of_the_day_mood(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT strftime('%H', timestamp), emotion
                FROM emotion_logs
            """)
            rows = cursor.fetchall()

        if not rows:
            return None

        for hour, emotion in rows:
            if emotion not in emotion_score:
                continue
            hour = int(hour)
            score = emotion_score[emotion]

            if 5<=hour<=11:
                periods["morning"].append(score)
            elif 12<=hour<=17:
                periods["afternoon"].append(score)
            elif 18<=hour<=21:
                periods["evening"].append(score)
            else:
                periods["night"].append(score)

        averages = {}

        for period, scores in periods.items():
            if scores:
                averages[period] = sum(scores) / len(scores)

        if not averages:
            return None
        best_period = max(averages, key = averages.get)
        worst_period = min(averages, key = averages.get)

        return{
            "best": best_period,
            "worst": worst_period
        }

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
                "SELECT id, timestamp, emotion, confidence, notes FROM emotion_logs ORDER BY timestamp"
            )
            rows = cursor.fetchall()

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            f.write("sep=,\n")
            writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["ID", "Timestamp", "Emotion", "Confidence", "Notes"])
            writer.writerows(rows)

    def get_dominant_emotion_for_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT emotion FROM emotion_logs
                WHERE DATE(timestamp) = ?
            """, (today,))

            rows = cursor.fetchall()

        if not rows:
            return None

        emotions = [row[0] for row in rows]

        counts = Counter(emotions)
        return counts.most_common(1)[0][0]

    def get_mood_graph_data(self, days=30):
        MOOD_SCORE = {
            "happy": 6, "surprise": 5, "neutral": 4,
            "fear": 3, "disgust": 2, "sad": 1, "angry": 0
        }
        since = (datetime.now().date() - timedelta(days=days)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(timestamp) as day, emotion
                FROM emotion_logs
                WHERE DATE(timestamp) >= ?
                ORDER BY timestamp
            """, (since,))
            rows = cursor.fetchall()

        daily = {}
        for day_str, emotion in rows:
            if day_str not in daily:
                daily[day_str] = []
            daily[day_str].append(emotion)

        result = []
        for day_str in sorted(daily.keys()):
            counts = Counter(daily[day_str])
            dominant = counts.most_common(1)[0][0]
            score = MOOD_SCORE.get(dominant, 3)
            result.append((day_str, dominant, score))

        return result


    def clear_all(self):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM emotion_logs")
            conn.commit()