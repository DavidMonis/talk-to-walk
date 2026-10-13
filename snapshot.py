import cv2
import os

OUTPUT_DIR = "/home/unitree/monis4"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for i in range(8):
    device = f"/dev/video{i}"

    print(f"Testing {device}...")

    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("  Cannot open")
        continue

    # Pokúsime sa nastaviť rozumné rozlíšenie.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = cap.read()

    if ret:
        filename = os.path.join(
            OUTPUT_DIR,
            f"snapshot_video{i}.jpg"
        )

        cv2.imwrite(filename, frame)

        height, width = frame.shape[:2]

        print(f"  SUCCESS")
        print(f"  Resolution: {width}x{height}")
        print(f"  Saved: {filename}")
    else:
        print("  Opened, but could not read frame")

    cap.release()