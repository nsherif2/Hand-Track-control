import cv2
import mediapipe as mp
from math import hypot
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import pyautogui
import os
import time

# Initialize Mediapipe and pycaw for volume control
cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(min_detection_confidence=0.75)
mpDraw = mp.solutions.drawing_utils

# Volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volMin, volMax = volume.GetVolumeRange()[:2]

# Cooldown for screenshot to prevent multiple triggers
screenshot_cooldown = 2  # seconds
last_screenshot_time = 0

def is_fist(lmList):
    """Check if the hand is a fist by comparing distances between fingertips and corresponding palm base."""
    if len(lmList) < 21:
        return False
    fingers = [8, 12, 16, 20]  # Tips of index, middle, ring, pinky fingers
    for finger in fingers:
        tip = lmList[finger]
        base = lmList[finger - 2]
        distance = hypot(tip[0] - base[0], tip[1] - base[1])
        if distance > 40:
            return False
    return True

def is_triangle(lmList):
    """Detect if a hand forms a triangle using the thumb and index finger."""
    if len(lmList) < 21:
        return False
    # Index finger and thumb tip
    index_finger = lmList[8]
    thumb = lmList[4]

    # Calculate the distance between thumb and index finger
    distance = hypot(index_finger[0] - thumb[0], index_finger[1] - thumb[1])
    # Debugging
    print(f"Thumb-Index Distance: {distance}")

    # Triangle gesture: distance should be within a reasonable range
    return 30 < distance < 200

def is_thumb_pinky_squeeze(lmList):
    """Detect if the left hand's thumb and pinky finger tips are squeezed together."""
    if len(lmList) < 21:
        return False

    # Thumb and pinky finger tips
    thumb_tip = lmList[4]
    pinky_tip = lmList[20]

    # Calculate the distance between thumb and pinky finger
    thumb_pinky_dist = hypot(thumb_tip[0] - pinky_tip[0], thumb_tip[1] - pinky_tip[1])

    # Debugging output for distance
    print(f"Thumb-Pinky Distance: {thumb_pinky_dist}")

    # If the distance is small, it's considered a squeeze
    return thumb_pinky_dist < 40  # Adjust the threshold if necessary

def is_screenshot_gesture(left_lmList, right_lmList):
    """Detect if both hands form a triangle by touching index fingers and thumbs."""
    if len(left_lmList) < 21 or len(right_lmList) < 21:
        return False

    # Left hand landmarks
    left_index = left_lmList[8]  # Left index finger tip
    left_thumb = left_lmList[4]  # Left thumb tip

    # Right hand landmarks
    right_index = right_lmList[8]  # Right index finger tip
    right_thumb = right_lmList[4]  # Right thumb tip

    # Calculate distances
    index_to_index = hypot(left_index[0] - right_index[0], left_index[1] - right_index[1])
    thumb_to_thumb = hypot(left_thumb[0] - right_thumb[0], left_thumb[1] - right_thumb[1])

    # Debugging printout to check distances
    print(f"Index to Index Distance: {index_to_index}, Thumb to Thumb Distance: {thumb_to_thumb}")

    # If both distances are small enough, consider it a triangle gesture
    threshold = 50  # Adjust this threshold as needed
    if index_to_index < threshold and thumb_to_thumb < threshold:
        return True
    return False

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    left_lmList, right_lmList = [], []
    h, w, _ = img.shape

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label  # 'Left' or 'Right'
            lmList = []
            for lm in hand_landmarks.landmark:
                lmList.append([int(lm.x * w), int(lm.y * h)])
            if label == 'Left':
                left_lmList = lmList
            elif label == 'Right':
                right_lmList = lmList
            mpDraw.draw_landmarks(img, hand_landmarks, mpHands.HAND_CONNECTIONS)

    # Control Brightness with Left Hand (Triangle Gesture)
    if is_triangle(left_lmList):
        print("Left Hand Triangle Detected: Adjusting Brightness")
        # Adjust brightness based on the thumb-index distance
        x1, y1 = left_lmList[4][0], left_lmList[4][1]  # Thumb tip
        x2, y2 = left_lmList[8][0], left_lmList[8][1]  # Index finger tip
        length = hypot(x2 - x1, y2 - y1)
        bright = np.interp(length, [30, 200], [0, 100])  # Map distance to brightness
        print(f"Brightness: {bright}, Length: {length}")
        sbc.set_brightness(int(bright))
        cv2.putText(img, f'Brightness: {int(bright)}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Control Volume with Right Hand (Triangle Gesture)
    if is_triangle(right_lmList):
        print("Right Hand Triangle Detected: Adjusting Volume")
        # Adjust volume based on the thumb-index distance
        x1, y1 = right_lmList[4][0], right_lmList[4][1]  # Thumb tip
        x2, y2 = right_lmList[8][0], right_lmList[8][1]  # Index finger tip
        length = hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [30, 200], [volMin, volMax])  # Map distance to volume level
        print(f"Volume: {vol}, Length: {length}")
        volume.SetMasterVolumeLevel(vol, None)
        # Optionally, display volume level as percentage
        vol_percent = np.interp(length, [30, 200], [0, 100])
        cv2.putText(img, f'Volume: {int(vol_percent)}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if is_thumb_pinky_squeeze(left_lmList):
        print("Left hand thumb-pinky squeeze detected: Minimizing all windows.")
        pyautogui.hotkey('win', 'd')  # Minimize all windows (show desktop)
        
    # Check for both fists closed (logout)
    if is_fist(left_lmList) and is_fist(right_lmList):
        print("Both fists detected! Logging out the user...")
        cv2.putText(img, 'Both Fists Detected! Logging out...', (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        os.system("shutdown /l")  # Logs off the user
        break

    # Check for screenshot gesture
    current_time = time.time()
    if is_screenshot_gesture(left_lmList, right_lmList):
        if current_time - last_screenshot_time > screenshot_cooldown:
            print("Triangle Gesture Detected! Taking screenshot...")
            pyautogui.screenshot('screenshot.png')
            cv2.putText(img, 'WORKSSSSS!', (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_screenshot_time = current_time

    # Show the video feed
    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
