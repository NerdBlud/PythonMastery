import cv2
import numpy as np
from collections import deque

CAMERA_INDEX = 0
SMOOTH_FRAMES = 5
MIN_HEAD_SIZE = 50

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Calibration: Sit at three comfortable distances from your monitor.")
print("Press 'S' to capture a position, 'Q' to quit calibration.")

calibration_heights = []

while len(calibration_heights) < 3:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(MIN_HEAD_SIZE, MIN_HEAD_SIZE))
    
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda rect: rect[2]*rect[3])
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(frame, f"Position {len(calibration_heights)+1}: Press S", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Calibration", frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('s') and len(faces) > 0:
        calibration_heights.append(h)
        print(f"Captured position {len(calibration_heights)} with head height {h}")
    elif key == ord('q'):
        break

if len(calibration_heights) < 3:
    print("Calibration incomplete. Exiting...")
    cap.release()
    cv2.destroyAllWindows()
    exit()

calibration_heights.sort()
far_height, perfect_height, close_height = calibration_heights
print(f"Calibration done: Far={far_height}, Perfect={perfect_height}, Close={close_height}")

history = deque(maxlen=SMOOTH_FRAMES)
print("Real-time monitoring started. Press 'Q' to quit.")

def detect_emotion(face_roi, gray_roi):
    eyes = eye_cascade.detectMultiScale(gray_roi, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))
    smiles = smile_cascade.detectMultiScale(gray_roi, scaleFactor=1.8, minNeighbors=20, minSize=(25, 25))
    
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(face_roi, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
    
    emotion = "Neutral"
    emotion_color = (255, 255, 255)
    
    if len(smiles) > 0:
        emotion = "Happy"
        emotion_color = (0, 255, 0)
        for (sx, sy, sw, sh) in smiles:
            cv2.rectangle(face_roi, (sx, sy), (sx+sw, sy+sh), (0, 255, 255), 2)
    elif len(eyes) < 2:
        emotion = "Sad"
        emotion_color = (255, 0, 0)
    else:
        lower_face = gray_roi[int(gray_roi.shape[0]*0.6):, :]
        mouth_region = smile_cascade.detectMultiScale(lower_face, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))
        
        if len(mouth_region) == 0:
            emotion = "Angry"
            emotion_color = (0, 0, 255)
    
    return emotion, emotion_color

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(MIN_HEAD_SIZE, MIN_HEAD_SIZE))
    
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda rect: rect[2]*rect[3])
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        emotion, emotion_color = detect_emotion(roi_color, roi_gray)
        
        if h < perfect_height:
            percent = int((h - far_height) / (perfect_height - far_height) * 100)
            percent = max(0, min(100, percent))
            status = f"Too far ({percent}%)"
            color = (0, 165, 255)
        elif h > perfect_height:
            percent = int((close_height - h) / (close_height - perfect_height) * 100)
            percent = max(0, min(100, percent))
            status = f"Too close ({percent}%)"
            color = (0, 0, 255)
        else:
            status = "Perfect (100%)"
            color = (0, 255, 0)
        
        history.append(h)
        smoothed_h = np.mean(history)
        
        cv2.putText(frame, status, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"Emotion: {emotion}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, emotion_color, 2)
    else:
        history.append(0)
        cv2.putText(frame, "No face detected", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    
    cv2.imshow("Screen Distance Monitor", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()