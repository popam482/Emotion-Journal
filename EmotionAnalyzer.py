import time

from deepface import DeepFace
import cv2

class EmotionAnalyzer:

    def __init__(self):
        self.cap=cv2.VideoCapture(0)

    def get_frame(self):
        ret, frame=self.cap.read()
        return ret, frame

    def analyze_emotion(self, frame):
            try:
                resized_frame=cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
                results=DeepFace.analyze(resized_frame, actions=['emotion'], enforce_detection=False)
                emotion=results[0]['dominant_emotion']
                return emotion
            except Exception as e:
                print(f"Analysis error: {e}")
                return None

    def release(self):
        self.cap.release()
