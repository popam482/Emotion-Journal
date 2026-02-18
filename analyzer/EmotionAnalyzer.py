from deepface import DeepFace
import cv2


class EmotionAnalyzer:
    def __init__(self):
        self.cap = None

    def start_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("ERROR: Could not open camera")
                return False
        return True

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            return self.cap.read()
        return False, None

    def analyze_emotion(self, frame):
        try:
            results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = results[0]['dominant_emotion']
            return emotion
        except Exception as e:
            print(f"Analysis error: {e}")
            return None

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None