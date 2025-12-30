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

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ---------------- SENTENCE BUILDER ----------------
sentence = []
last_added_word = ""

# ---------------- CONFIRM GESTURE ----------------
confirm_start_time = None
CONFIRM_HOLD_TIME = 2.0  # seconds (fist hold)

# ---------------- EMOTION VARIABLES ----------------
prev_y = None
prev_time = time.time()
emotion = "CALM"

# ---------------- FILE SAVE ----------------
output_file = open("output.txt", "a")

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
            elif index_up and middle_up and not ring_up and not pinky_up:
                current_word = "PEACE"
            elif index_up and not middle_up and not ring_up and not pinky_up:
                current_word = "WAIT"
            elif not index_up and not middle_up and not ring_up and not pinky_up:
                current_word = "NO"

            # -------- ADD WORD TO SENTENCE --------
            if current_word != "" and current_word != last_added_word:
                sentence.append(current_word)
                last_added_word = current_word
                output_file.write(current_word + " ")
                output_file.flush()

            # -------- EMOTION DETECTION --------
            current_time = time.time()
            current_y = hand.landmark[0].y  # wrist

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

            # -------- CONFIRM GESTURE (FIST HOLD) --------
            if not index_up and not middle_up and not ring_up and not pinky_up:
                if confirm_start_time is None:
                    confirm_start_time = time.time()
                elif time.time() - confirm_start_time >= CONFIRM_HOLD_TIME:
                    full_sentence = " ".join(sentence)
                    if full_sentence != "":
                        threading.Thread(
                            target=speak,
                            args=(full_sentence,),
                            daemon=True
                        ).start()

                        output_file.write("\n")
                        output_file.flush()

                    sentence.clear()
                    last_added_word = ""
                    confirm_start_time = None
            else:
                confirm_start_time = None

    # -------- DISPLAY --------
    cv2.putText(frame, "Sentence:", (30, 260),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 255, 255), 2)

    cv2.putText(frame, " ".join(sentence), (30, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 255), 2)

    cv2.putText(frame, f"Emotion: {emotion}", (30, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 0, 0), 2)

    cv2.imshow("Sentence Builder - Confirm to Speak", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
output_file.close()
cv2.destroyAllWindows()
