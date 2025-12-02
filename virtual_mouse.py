import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

##########################
wCam, hCam = 640, 480
frameR = 100
smoothening = 5
click_hold_time = 1.1
freeze_hold_duration = 5.0  # seconds to hold all fingers up
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
cursor_frozen = False
frozen_x, frozen_y = autopy.mouse.location()

# For freeze toggle logic
freeze_hold_start = None  # time when 5-finger gesture started

while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    fingers = detector.fingersUp() if len(lmList) > 0 else []

    current_time = time.time()

    # -------------------------------
    # 5-FINGER HOLD TO TOGGLE FREEZE
    # -------------------------------
    if fingers == [1, 1, 1, 1, 1]:
        if freeze_hold_start is None:
            # Start the timer
            freeze_hold_start = current_time
        else:
            # Check if 5 seconds have passed
            elapsed = current_time - freeze_hold_start
            if elapsed >= freeze_hold_duration:
                # Toggle freeze state
                cursor_frozen = not cursor_frozen
                if cursor_frozen:
                    frozen_x, frozen_y = autopy.mouse.location()
                    print("✅ Cursor FROZEN (after 5s hold)")
                else:
                    print("✅ Cursor UNFROZEN (after 5s hold)")
                # Reset to avoid repeated toggling
                freeze_hold_start = None
    else:
        # Gesture broken — reset timer
        if freeze_hold_start is not None:
            print(f"⚠️ Freeze hold canceled ({current_time - freeze_hold_start:.1f}s held)")
            freeze_hold_start = None

    # -------------------------------
    # Handle cursor: frozen or moving
    # -------------------------------
    if len(lmList) > 0:
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        if cursor_frozen:
            autopy.mouse.move(frozen_x, frozen_y)
            # Show countdown or status
            cv2.putText(img, "FROZEN", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.circle(img, (wCam // 2, hCam // 2), 25, (0, 0, 255), cv2.FILLED)
        else:
            if fingers[1] == 1:  # Index up → move
                x1, y1 = lmList[8][1:]
                xScreen = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                yScreen = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                clocX = plocX + (xScreen - plocX) / smoothening
                clocY = plocY + (yScreen - plocY) / smoothening

                clocX = np.clip(clocX, 0, wScr - 1)
                clocY = np.clip(clocY, 0, hScr - 1)

                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                plocX, plocY = clocX, clocY

        # -----------------------
        # Click: Index + Pinky
        # -----------------------
        if not cursor_frozen and fingers == [0, 1, 0, 0, 1]:
            if click_timer == 0:
                click_timer = time.time()
            elif time.time() - click_timer >= click_hold_time:
                autopy.mouse.click()
                click_timer = 0
                print("🖱️ CLICK")
        else:
            click_timer = 0

        # -----------------------
        # Show freeze hold countdown
        # -----------------------
        if freeze_hold_start is not None:
            held = current_time - freeze_hold_start
            remaining = max(0, freeze_hold_duration - held)
            cv2.putText(img, f"Freeze in: {remaining:.1f}s", (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # -----------------------
    # FPS Display
    # -----------------------
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()