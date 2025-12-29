import cv2
import mediapipe as mp

# -------- FILE OPEN --------
file = open("output.txt", "a")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_word = ""

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # -------- Finger states --------
            index_up  = hand.landmark[8].y  < hand.landmark[6].y
            middle_up = hand.landmark[12].y < hand.landmark[10].y
            ring_up   = hand.landmark[16].y < hand.landmark[14].y
            pinky_up  = hand.landmark[20].y < hand.landmark[18].y
            thumb_up  = hand.landmark[4].x  > hand.landmark[3].x

            # -------- Expression-based words --------
            if index_up and middle_up and ring_up and pinky_up:
                current_word = "HELLO"

            elif thumb_up and not index_up:
                current_word = "YES"

            elif not index_up and not middle_up and not ring_up and not pinky_up:
                current_word = "NO"

            elif index_up and middle_up and not ring_up:
                current_word = "PEACE"

            elif index_up and not middle_up:
                current_word = "WAIT"

            elif index_up and middle_up and ring_up and not pinky_up:
                current_word = "THANK YOU"

    # -------- Display & Save --------
    if current_word != "":
        file.write(current_word + "\n")
        file.flush()

        cv2.putText(frame, current_word, (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                    (0, 255, 0), 3)

    cv2.imshow("Simple Sign to Text Demo", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
file.close()
cv2.destroyAllWindows()
