import cv2
import mediapipe as mp
import csv
import os

label = input("Enter label (HELLO / YES / NO): ")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

cap = cv2.VideoCapture(0)

file_exists = os.path.isfile("data.csv")

with open("data.csv", "a", newline="") as f:
    writer = csv.writer(f)

    if not file_exists:
        header = []
        for i in range(21):
            header += [f"x{i}", f"y{i}"]
        header.append("label")
        writer.writerow(header)

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                landmarks = []
                for lm in hand.landmark:
                    landmarks.extend([lm.x, lm.y])

                landmarks.append(label)
                writer.writerow(landmarks)

                print("Saved one sample")

        cv2.imshow("Data Collection", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

cap.release()
cv2.destroyAllWindows()
