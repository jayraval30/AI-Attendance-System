import cv2

PHONE_CAM_URL = "http://192.168.0.101:8080/video"

cap = cv2.VideoCapture(PHONE_CAM_URL)

def get_frame():
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    if not ret:
        return None
    return frame
