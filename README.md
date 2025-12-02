# 🖱️ AI Virtual Mouse

Control your computer cursor **using hand gestures** — no mouse required!  
This project uses **computer vision** (OpenCV + MediaPipe) to detect hand landmarks and translate them into **mouse movements**, **clicks**, and a unique **cursor freeze** feature.

Perfect for **touchless computing**, accessibility, presentations, or just a cool demo!

> 🔒 **100% local & privacy-friendly** — no data leaves your machine.

---

## ✨ Features

- ✅ **Cursor movement** using your index finger
- ✅ **Left-click** by holding **index + pinky** for **1.1 seconds**
- ✅ **Freeze/Unfreeze cursor** by holding **all five fingers up for 5 seconds**
- ✅ **Smooth cursor motion** with configurable smoothing
- ✅ **Real-time visual feedback**: freeze status, countdown timer, and FPS
- ✅ **Mirror-corrected movement** for natural left-right control

---

## 🛠️ Requirements

- **Python 3.7+**
- A working **webcam**
- **Operating System**: Windows, macOS, or Linux  
  _(Note: `autopy` works best on Windows and macOS)_

### Install Dependencies

We recommend using a virtual environment:

```bash
# Create and activate a virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

Then install the required packages:
pip install -r requirements.txt

```

### 🚀 How to Use

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install opencv-python mediapipe autopy numpy
   ```

### 🖐️ Gesture Guide

| Gesture            | Fingers Up (Thumb → Pinky) | Action                                      |
| ------------------ | -------------------------- | ------------------------------------------- |
| 👆 Point           | `[0, 1, 0, 0, 0]`          | Move cursor                                 |
| ✌️ Click           | `[0, 1, 0, 0, 1]`          | Left-click (after 1.1 seconds hold)         |
| ✋ Freeze/Unfreeze | `[1, 1, 1, 1, 1]`          | Toggle cursor freeze (after 5 seconds hold) |

⚙️ Configuration
You can customize the behavior by modifying these parameters at the top of virtual_mouse.py:

wCam, hCam = 640, 480 # Camera resolution (width, height)
frameR = 100 # Reduced tracking area (pixels from each edge)
smoothening = 5 # Cursor smoothing (higher = smoother but less responsive)
click_hold_time = 1.1 # Seconds to hold index + pinky for a click
freeze_hold_duration = 5.0 # Seconds to hold all fingers for freeze/unfreeze

```

```
