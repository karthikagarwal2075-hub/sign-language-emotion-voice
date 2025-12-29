import cv2
import mediapipe as mp
import time
import pyttsx3
import threading

# ---------------- SPEECH FUNCTION ----------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ---------------- VOICE CONTROL ----------------
last_spoken = ""
last_voice_time = 0
voice_delay = 2.5

# ---------------- EMOTION VARIABLES ----------------
prev_y = None
prev_time = time.time()
emotion = "CALM"

# ---------------- PASSWORD SETUP ----------------
password = ["HELLO", "YES", "NO"]
input_sequence = []

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_word = ""

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # -------- Finger States --------
            thumb_up  = hand.landmark[4].x > hand.landmark[3].x
            index_up  = hand.landmark[8].y < hand.landmark[6].y
            middle_up = hand.landmark[12].y < hand.landmark[10].y
            ring_up   = hand.landmark[16].y < hand.landmark[14].y
            pinky_up  = hand.landmark[20].y < hand.landmark[18].y

            # -------- WORD DETECTION --------
            if index_up and middle_up and ring_up and pinky_up:
                current_word = "HELLO"
            elif thumb_up and not index_up:
                current_word = "YES"
            elif not index_up and not middle_up and not ring_up and not pinky_up:
                current_word = "NO"
            elif index_up and middle_up and not ring_up and not pinky_up:
                current_word = "PEACE"
            elif index_up and not middle_up and not ring_up and not pinky_up:
                current_word = "WAIT"

            # -------- EMOTION DETECTION (FIXED) --------
            current_time = time.time()
            current_y = hand.landmark[0].y   # ✅ FIXED HERE

            if prev_y is not None:
                speed = abs(current_y - prev_y) / (current_time - prev_time)
                if speed > 1.5:
                    emotion = "EXCITED"
                elif not index_up and not middle_up:
                    emotion = "ANGRY"
                else:
                    emotion = "CALM"

            prev_y = current_y
            prev_time = current_time

    # -------- VOICE OUTPUT (THREAD SAFE) --------
    now = time.time()
    if current_word != "":
        if (current_word != last_spoken) or (now - last_voice_time > voice_delay):
            threading.Thread(
                target=speak,
                args=(current_word,),
                daemon=True
            ).start()

            last_spoken = current_word
            last_voice_time = now

            # -------- PASSWORD TRACKING --------
            input_sequence.append(current_word)
            if len(input_sequence) > len(password):
                input_sequence.pop(0)

    # -------- DISPLAY --------
    if current_word != "":
        cv2.putText(frame, current_word, (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (0, 255, 0), 4)

    cv2.putText(frame, f"Emotion: {emotion}", (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 0, 0), 2)

    if input_sequence == password:
        cv2.putText(frame, "ACCESS GRANTED", (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.8,
                    (0, 255, 255), 4)

    cv2.imshow("Emotion + Voice + Gesture Password", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
