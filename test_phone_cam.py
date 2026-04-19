import cv2

URL = "http://192.168.0.101:8080/video"
cap = cv2.VideoCapture(URL)

while True:
    ret, frame = cap.read()
    if not ret:
        print(" Cannot read frame from phone camera")
        break

    cv2.imshow("Phone Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
