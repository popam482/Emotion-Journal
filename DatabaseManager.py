import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/journal.db"):
        self.db_path=db_path
        self.create_table()

    def get_connection(self):
         return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as conn:
            query="""
            CREATE TABLE IF NOT EXISTS emotion_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            emotion TEXT,
            confidence REAL
            );"""
            conn.execute(query)
            conn.commit()

    def save_emotion(self, emotion, confidence=1.0):
        with self.get_connection() as conn:
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query="INSERT INTO emotion_logs (timestamp, emotion, confidence) VALUES (?, ?, ?)"
            conn.execute(query, (date, emotion, confidence))
            conn.commit()
            print(f"DEBUG: Saved {emotion} to db")