import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Settings
wCam, hCam = 1280, 1080  # Webcam resolution
click_delay = 0.1
sensitivity = 1.0
deadzone = 0
scroll_speed = 5

# Init webcam and pyautogui
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
screenW, screenH = pyautogui.size()

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Variables
last_click_time = 0
is_clicking = False
mouse_control = False
prev_index_pos = None

# Gesture handling
gesture_state = None
gesture_cooldown_time = 0.3  # seconds
last_gesture_time = 0

# FPS
prev_frame_time = 0

# Variables for swipe detection
prev_index_x = None
swipe_threshold = 150  # Set a threshold for swipe distance

# Utility functions
def fingers_up(lm):
    tips = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(1 if lm[tips[0]].x < lm[tips[0] - 1].x else 0)
    for i in range(1, 5):
        fingers.append(1 if lm[tips[i]].y < lm[tips[i] - 2].y else 0)
    return fingers

def get_distance(p1, p2):
    return np.hypot(p1.x - p2.x, p1.y - p2.y)

def draw_cursor_feedback(img, x, y, radius=30):
    cv2.circle(img, (x, y), radius, (0, 255, 255), 3)
    cv2.circle(img, (x, y), radius // 2, (0, 255, 0), 3)

def draw_click_feedback(img, x, y, radius=50):
    cv2.circle(img, (x, y), radius, (255, 0, 0), 2)
    cv2.circle(img, (x, y), radius // 2, (0, 0, 255), 2)

def draw_scroll_feedback(img, x, y, direction, radius=100):
    color = (0, 255, 0) if direction == 1 else (0, 0, 255)
    cv2.arrowedLine(img, (x, y), (x, y - radius if direction == 1 else y + radius), color, 4, tipLength=0.1)

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    h, w, _ = img.shape

    # FPS display
    current_time = time.time()
    fps = 1 / (current_time - prev_frame_time) if prev_frame_time else 0
    prev_frame_time = current_time
    cv2.putText(img, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm = handLms.landmark
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            finger_state = fingers_up(lm)
            index_x, index_y = int(lm[8].x * w), int(lm[8].y * h)
            thumb_x, thumb_y = int(lm[4].x * w), int(lm[4].y * h)

            # Activate or deactivate mouse control
            if finger_state == [0, 1, 1, 0, 0]:
                mouse_control = True
                cv2.putText(img, "Mouse Control ON ✌️", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif sum(finger_state) == 5:
                mouse_control = False
                gesture_state = None
                cv2.putText(img, "Mouse Control OFF 🖐️", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if mouse_control:
                # Detect current gesture
                gesture_detected = None

                if finger_state == [0, 1, 0, 0, 0]:
                    gesture_detected = "move"
                elif get_distance(lm[4], lm[8]) < 0.04:
                    gesture_detected = "left_click"
                elif get_distance(lm[8], lm[12]) < 0.03:
                    gesture_detected = "right_click"
                elif finger_state == [0, 1, 1, 1, 0]:
                    gesture_detected = "scroll"
                else:
                    gesture_detected = None

                # Detect swipe gestures (left and right)
                if prev_index_x is not None and abs(index_x - prev_index_x) > swipe_threshold:
                    if index_x < prev_index_x:  # Left swipe (Back)
                        pyautogui.hotkey('alt', 'left')  # Simulate pressing 'Alt + Left Arrow' for back action
                        cv2.putText(img, "Swipe Left: Back ⬅️", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    elif index_x > prev_index_x:  # Right swipe (Next)
                        pyautogui.hotkey('alt', 'right')  # Simulate pressing 'Alt + Right Arrow' for next action
                        cv2.putText(img, "Swipe Right: Next ➡️", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Update the previous position for next comparison
                prev_index_x = index_x

                # Apply gesture if cooldown passed or it's continuing
                if (gesture_detected != gesture_state and current_time - last_gesture_time > gesture_cooldown_time) or (gesture_detected == gesture_state):
                    gesture_state = gesture_detected
                    last_gesture_time = current_time

                    if gesture_state == "move" and not is_clicking:
                        pyautogui.moveTo(screenW * (index_x / w), screenH * (index_y / h))
                        draw_cursor_feedback(img, index_x, index_y)

                    elif gesture_state == "left_click" and not is_clicking and current_time - last_click_time > click_delay:
                        pyautogui.click()
                        last_click_time = current_time
                        is_clicking = True
                        draw_click_feedback(img, index_x, index_y)
                        cv2.putText(img, "Left Click 🖱️", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    elif gesture_state == "right_click" and current_time - last_click_time > click_delay:
                        pyautogui.rightClick()
                        last_click_time = current_time
                        cv2.putText(img, "Right Click 🤞", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)

                    elif gesture_state == "scroll":
                        dy = index_y - prev_index_pos[1] if prev_index_pos else 0
                        if abs(dy) > 5:
                            kinetic_speed = int(np.clip(dy * 2, -50, 50))
                            pyautogui.scroll(-kinetic_speed)
                            draw_scroll_feedback(img, index_x, index_y, 1 if dy < 0 else -1)
                            cv2.putText(img, f"Scroll {'Up' if dy < 0 else 'Down'} ⬆️⬇️", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 50), 2)

            if is_clicking and time.time() - last_click_time > click_delay:
                is_clicking = False

            prev_index_pos = (index_x, index_y)

    else:
        prev_index_pos = None
        gesture_state = None

    cv2.imshow("Virtual Mouse (Stable)", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
