import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui

##########################
wCam, hCam = 1240, 720
frameR = 15  # Reduced frame for stability (keep this)
smoothening = 5
click_hold_time = 1.1
freeze_hold_duration = 5.0
eshapp_click_time = 1.5
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

click_timer = 0
eshapp_timer = 0  
cursor_frozen = False
frozen_x, frozen_y = autopy.mouse.location()
freeze_hold_start = None

while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)  
    
    # ✅ Robust finger detection: only proceed if we have enough landmarks
    fingers = []
    valid_hand = False
    if len(lmList) >= 9:  # At least up to pinky base (landmark 17)
        try:
            fingers = detector.fingersUp()
            valid_hand = True
        except Exception as e:
            valid_hand = False
            fingers = []

    current_time = time.time()

    # -------------------------------
    # Freeze Logic (only with valid hand)
    # -------------------------------
    if valid_hand and fingers == [1, 1, 1, 1, 1]:
        if freeze_hold_start is None:
            freeze_hold_start = current_time
        else:
            elapsed = current_time - freeze_hold_start
            if elapsed >= freeze_hold_duration:
                cursor_frozen = not cursor_frozen
                if cursor_frozen:
                    frozen_x, frozen_y = autopy.mouse.location()
                    print("✅ Cursor FROZEN")
                else:
                    print("✅ Cursor UNFROZEN")
                freeze_hold_start = None
    else:
        if freeze_hold_start is not None:
            print(f"⚠️ Freeze canceled ({current_time - freeze_hold_start:.1f}s)")
            freeze_hold_start = None

    # -------------------------------
    # Movement & Gestures
    # -------------------------------
    if valid_hand:
        # Draw bounding box only when hand is valid
        if bbox:
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 255), 2)
        else:
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        if cursor_frozen:
            autopy.mouse.move(frozen_x, frozen_y)
            cv2.putText(img, "FROZEN", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.circle(img, (wCam // 2, hCam // 2), 25, (0, 0, 255), cv2.FILLED)
        else:
            # ✅ Allow movement even if hand is partially off-screen
            if len(lmList) > 8:  # Index tip (8) exists
                x1, y1 = lmList[8][1], lmList[8][2]

                # Map full camera frame to screen (but keep frameR for stability)
                xScreen = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                yScreen = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                clocX = plocX + (xScreen - plocX) / smoothening
                clocY = plocY + (yScreen - plocY) / smoothening

                clocX = np.clip(clocX, 0, wScr - 1)
                clocY = np.clip(clocY, 0, hScr - 1)

                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                plocX, plocY = clocX, clocY

        # Click: Index + Middle
        if not cursor_frozen and len(fingers) == 5 and fingers == [0, 1, 1, 0, 0]:
            if click_timer == 0:
                click_timer = time.time()
            elif time.time() - click_timer >= click_hold_time:
                autopy.mouse.click()
                click_timer = 0
                print("🖱️ CLICK")
        else:
            click_timer = 0

        # ESC: Index + Pinky
        if not cursor_frozen and len(fingers) == 5 and fingers == [0, 1, 0, 0, 1]:
            if eshapp_timer == 0:
                eshapp_timer = time.time()
                cv2.putText(img, "HOLD FOR ESC...", (wCam//2 - 120, hCam - 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 0), 2)
            elif time.time() - eshapp_timer >= eshapp_click_time:
                pyautogui.press('esc')
                print("⌨️ ESC SENT!")
                eshapp_timer = 0
                cv2.putText(img, "ESC SENT!", (wCam//2 - 80, hCam - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
        else:
            eshapp_timer = 0

        # Freeze countdown
        if freeze_hold_start is not None:
            held = current_time - freeze_hold_start
            remaining = max(0, freeze_hold_duration - held)
            cv2.putText(img, f"Freeze: {remaining:.1f}s", (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()