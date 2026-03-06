from collections import Counter
import customtkinter as ctk
import cv2
from PIL import Image
import time


class ScanView(ctk.CTkFrame):
    def __init__(self, parent, analyzer, db, on_navigate, scan_dur, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.analyzer = analyzer
        self.db = db
        self.on_navigate = on_navigate
        self.scan_dur = scan_dur
        self.theme = theme

        self.is_scanning = False
        self.scan_start_time = 0
        self.captured_emotions = []
        self.last_log_id = None  #
        self.emotion_emojis = {
            "happy": "😊", "sad": "😢", "angry": "😠",
            "surprise": "😲", "fear": "😨", "disgust": "🤢",
            "neutral": "😐"
        }

        self.build_start_screen()

    def build_start_screen(self):
        self.clear()
        duration = self.scan_dur["scan_duration"]

        ctk.CTkLabel(self, text="🔍", font=("Arial", 48)).pack(pady=(40, 10))
        ctk.CTkLabel(self, text="Emotion Check-in",
                     font=("Arial", 28, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(self, text=f"The app will scan your expression for {duration} seconds.\nStay still and look at the camera.",
                     font=("Arial", 14), text_color=self.theme["text_dim"],
                     justify="center").pack(pady=(0, 30))

        ctk.CTkButton(self, text="▶ Start Scan", command=self.start_scan,
                      fg_color=self.theme["accent"], hover_color="#5a6ed0",
                      width=200, height=45, corner_radius=12,
                      font=("Arial", 16, "bold")).pack(pady=10)

        ctk.CTkButton(self, text="← Back", command=lambda: self.on_navigate("home"),
                      fg_color="transparent", hover_color=self.theme["border"],
                      width=120, height=35, font=("Arial", 13)).pack(pady=(5, 20))

    def start_scan(self):
        self.clear()
        self.analyzer.start_camera()
        self.active_duration = self.scan_dur["scan_duration"]

        self.status_label = ctk.CTkLabel(self, text="Scanning...",
                                         font=("Arial", 24, "bold"))
        self.status_label.pack(pady=(20, 10))

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True)

        self.progress_bar = ctk.CTkProgressBar(self, width=400,
                                                progress_color=self.theme["accent"])
        self.progress_bar.pack(pady=(10, 20))
        self.progress_bar.set(0)

        self.is_scanning = True
        self.scan_start_time = time.time()
        self.captured_emotions = []
        self.update_scan()

    def update_scan(self):
        if not self.is_scanning:
            return

        ret, frame = self.analyzer.get_frame()
        if ret:
            elapsed = time.time() - self.scan_start_time
            remaining = max(0, int(self.active_duration - elapsed))
            progress = min(elapsed / self.active_duration, 1.0)

            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Scanning... {remaining}s left")

            emotion = self.analyzer.current_emotion
            if emotion and int(elapsed) > len(self.captured_emotions):
                self.captured_emotions.append(emotion)

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ctk_img = ctk.CTkImage(img, size=(640, 480))
            self.video_label.configure(image=ctk_img)
            self.video_label._image = ctk_img

            if elapsed >= self.active_duration:
                self.finish_scan()
                return

        self.after(20, self.update_scan)

    def finish_scan(self):
        self.is_scanning = False
        self.analyzer.release()
        self.clear()

        if self.captured_emotions:
            counts = Counter(self.captured_emotions)
            dominant = counts.most_common(1)[0][0]
            self.last_log_id = self.db.save_emotion(dominant)

            emoji = self.emotion_emojis.get(dominant, "🤔")

            ctk.CTkLabel(self, text=emoji, font=("Arial", 72)).pack(pady=(30, 5))
            if dominant=="fear":
                ctk.CTkLabel(self, text=f"You seem {"scared"}!",
                         font=("Arial", 28, "bold"),
                         text_color=self.theme["accent"]).pack(pady=(0, 10))
            elif dominant=="surprise":
                ctk.CTkLabel(self, text=f"You seem {"surprised"}!",
                             font=("Arial", 28, "bold"),
                             text_color=self.theme["accent"]).pack(pady=(0, 10))
            elif dominant=="disgust":
                ctk.CTkLabel(self, text=f"You seem {"disgused"}!",
                             font=("Arial", 28, "bold"),
                             text_color=self.theme["accent"]).pack(pady=(0, 10))
            else:
                ctk.CTkLabel(self, text=f"You seem {dominant.capitalize()}!",
                             font=("Arial", 28, "bold"),
                             text_color=self.theme["accent"]).pack(pady=(0, 10))
            breakdown_frame = ctk.CTkFrame(self, fg_color=self.theme["bg_card"], corner_radius=12)
            breakdown_frame.pack(pady=(0, 15), padx=60, fill="x")

            ctk.CTkLabel(breakdown_frame, text="Scan Breakdown",
                         font=("Arial", 16, "bold")).pack(pady=(15, 5))

            total = len(self.captured_emotions)
            for emotion, count in counts.most_common():
                percentage = int((count / total) * 100)
                em = self.emotion_emojis.get(emotion, "")
                ctk.CTkLabel(breakdown_frame,
                             text=f"{em} {emotion.capitalize()}: {percentage}% ({count}/{total})",
                             font=("Arial", 13), text_color=self.theme["text_dim"]
                             ).pack(pady=2)
            ctk.CTkLabel(breakdown_frame, text="").pack(pady=5)

            note_frame = ctk.CTkFrame(self, fg_color=self.theme["bg_card"], corner_radius=12)
            note_frame.pack(pady=(0, 15), padx=60, fill="x")

            ctk.CTkLabel(note_frame, text="📝  How are you feeling? (optional)",
                         font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(12, 4))
            ctk.CTkLabel(note_frame, text="Write a few words about your day or what's on your mind.",
                         font=("Arial", 12), text_color=self.theme["text_dim"]).pack(anchor="w", padx=15)

            self.note_entry = ctk.CTkTextbox(note_frame, width=500, height=80,
                                             corner_radius=8, fg_color=self.theme["bg_main"])
            self.note_entry.pack(fill="x", padx=15, pady=(8, 15))

        else:
            self.last_log_id = None
            ctk.CTkLabel(self, text="😕", font=("Arial", 72)).pack(pady=(50, 10))
            ctk.CTkLabel(self, text="No emotion detected",
                         font=("Arial", 24, "bold"), text_color="red").pack(pady=10)
            ctk.CTkLabel(self, text="Make sure your face is visible and well-lit.",
                         font=("Arial", 14), text_color=self.theme["text_dim"]).pack(pady=5)

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="🔄  Scan Again",
                      command=lambda: self.save_note_and_go("scan"),
                      fg_color=self.theme["accent"], hover_color="#5a6ed0",
                      width=160, height=40, font=("Arial", 14, "bold")).pack(side="left", padx=10)

        ctk.CTkButton(buttons_frame, text="🏠  Home",
                      command=lambda: self.save_note_and_go("home"),
                      fg_color=self.theme["border"], hover_color="#444444",
                      width=160, height=40, font=("Arial", 14, "bold")).pack(side="left", padx=10)

    def save_note_and_go(self, destination):
        if self.last_log_id is not None and hasattr(self, "note_entry"):
            note = self.note_entry.get("1.0", "end").strip()
            if note:
                self.db.save_note(self.last_log_id, note)

        if destination == "scan":
            self.build_start_screen()
        else:
            self.on_navigate("home")

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def destroy(self):
        self.is_scanning = False
        self.analyzer.release()
        super().destroy()