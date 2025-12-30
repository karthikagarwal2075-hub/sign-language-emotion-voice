import cv2
import mediapipe as mp
import time
import pyttsx3
import threading

# ---------------- SPEECH ENGINE ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
speaking = False

def speak(text):
    global speaking
    if speaking:
        return
    speaking = True
    engine.say(text)
    engine.runAndWait()
    speaking = False

# ---------------- MEDIAPIPE ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

# ---------------- SENTENCE BUILDER ----------------
sentence = []
last_word = ""
confidence = 0
CONF_THRESHOLD = 60

# ---------------- CONFIRM GESTURE ----------------
confirm_start = None
CONFIRM_TIME = 2.0

# ---------------- EMOTION ----------------
prev_y = None
prev_time = time.time()
emotion = "CALM"

# ---------------- OUTPUT FILE ----------------
open("output.txt", "w").close()  # clear file on start

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

            # Finger states
            index_up = hand.landmark[8].y < hand.landmark[6].y
            middle_up = hand.landmark[12].y < hand.landmark[10].y
            ring_up = hand.landmark[16].y < hand.landmark[14].y
            pinky_up = hand.landmark[20].y < hand.landmark[18].y
            thumb_up = hand.landmark[4].x > hand.landmark[3].x

            # ---------------- WORD DETECTION ----------------
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

            # ---------------- CONFIDENCE ----------------
            if current_word == last_word and current_word != "":
                confidence = min(confidence + 5, 100)
            else:
                confidence = 5
                last_word = current_word

            # ---------------- ADD WORD ----------------
            if confidence >= CONF_THRESHOLD and current_word not in sentence:
                sentence.append(current_word)

            # ---------------- CONFIRM GESTURE (FIST HOLD) ----------------
            if not index_up and not middle_up and not ring_up and not pinky_up:
                if confirm_start is None:
                    confirm_start = time.time()
                elif time.time() - confirm_start >= CONFIRM_TIME:
                    full_sentence = " ".join(sentence)
                    if full_sentence != "":
                        threading.Thread(
                            target=speak,
                            args=(full_sentence,),
                            daemon=True
                        ).start()

                        with open("output.txt", "a") as f:
                            f.write(full_sentence + "\n")

                    sentence.clear()
                    confidence = 0
                    last_word = ""
                    confirm_start = None
            else:
                confirm_start = None

            # ---------------- EMOTION DETECTION ----------------
            wrist_y = hand.landmark[0].y
            current_time = time.time()
            speed = abs(wrist_y - prev_y) / (current_time - prev_time) if prev_y else 0

            if speed > 3:
                emotion = "EXCITED"
            elif not index_up and not middle_up and not ring_up and not pinky_up:
                emotion = "ANGRY"
            else:
                emotion = "CALM"

            prev_y = wrist_y
            prev_time = current_time

    # ---------------- DISPLAY ----------------
    cv2.putText(frame, f"Sentence: {' '.join(sentence)}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.putText(frame, f"Confidence: {confidence}%", (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.putText(frame, f"Emotion: {emotion}", (30, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Sign Language Sentence Builder", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
