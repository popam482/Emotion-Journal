import cv2
import time

from EmotionAnalyzer import EmotionAnalyzer
from DatabaseManager import DatabaseManager

def main():
    analyzer=EmotionAnalyzer()
    db=DatabaseManager()

    last_analysis_time=0

    while True:
        ret, frame=analyzer.get_frame()
        if not ret:
            break

        current_time=time.time()
        if current_time-last_analysis_time>5:
            emotion= analyzer.analyze_emotion(frame)
            if emotion:
                db.save_emotion(emotion)
                last_analysis_time=current_time

        cv2.imshow("Image Test", frame)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

    analyzer.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
