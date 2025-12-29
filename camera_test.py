import cv2

# Open default camera (index 0)
cap = cv2.VideoCapture(0)

# Check if camera opened
if not cap.isOpened():
    print("❌ Camera not opening")
    exit()
else:
    print("✅ Camera opened successfully")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    cv2.imshow("Camera Test", frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
