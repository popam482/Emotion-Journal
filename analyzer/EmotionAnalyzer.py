from deepface import DeepFace
import cv2
import threading


class EmotionAnalyzer:
    def __init__(self):
        self.cap = None
        self.current_emotion = None
        self.analyzing = False
        self.frame_count = 0

    def start_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("ERROR: Could not open camera")
                return False

        return True

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                return False, None
            self.frame_count += 1
            if self.frame_count % 15 == 0 and not self.analyzing:
                self.start_analysis_thread(frame.copy())

            return True, frame

        return False, None

    def start_analysis_thread(self, frame):
        thread = threading.Thread(target=self.analyze_emotion, args=(frame,), daemon=True)
        thread.start()

    def analyze_emotion(self, frame):
        self.analyzing = True

        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False
            )

            self.current_emotion = result[0]['dominant_emotion']

        except Exception as e:
            print(f"Analysis error: {e}")

        finally:
            self.analyzing = False

    def get_current_emotion(self):
        return self.current_emotion

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.current_emotion = None
            self.analyzing = False
            self.frame_count = 0
            self.cap = None