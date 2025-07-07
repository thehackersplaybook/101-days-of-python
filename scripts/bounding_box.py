import cv2 
from ultralytics import YOLO
import numpy as np
import os
import datetime
import random

model = YOLO("yolov8n-pose.pt")

cap = cv2.VideoCapture(r'C:\Users\SHAMBHAVI\Desktop\shantanu_files\code_projects\random_projects\bounding_box\cool_video.MP4')

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

if width == 0 or height == 0 or fps == 0:
    print("Error: Could not read video properties (width, height, fps).")
    exit()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('video_output.mp4', fourcc, fps, (width, height))

frame_count = 0
prev_frame = None

ret, frame = cap.read()
if not ret:
    print("Error: Could not read the first frame.")
    exit()

trail_overlay = np.zeros_like(frame, dtype=np.uint8)

# Define skeleton connections (COCO)
skeleton = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16)
]

while True: 
    if frame_count == 0:
        current_frame = frame
    else:
        ret, current_frame = cap.read()
        if not ret:
            print("Warning: Skipping a bad frame.")
            break

    frame = current_frame

    # Trail fade
    if prev_frame is not None:
        alpha = 0.5
        frame = cv2.addWeighted(frame, 1 - alpha, prev_frame, alpha, 0)
    prev_frame = frame.copy()

    # Text overlays
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, timestamp, (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_8)
    if (frame_count // 2) % 2 == 0:
        cv2.putText(frame, "COPYRIGHTING", (10, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_8)

    frame_count += 1

    results = model(frame)[0]

    neon_box_color = (100, 255, 100)  # Soft neon green

    joint_colors = [(255, 0, 0), (0, 0, 255)]  # Red & Blue

    trail_overlay = cv2.addWeighted(trail_overlay, 0.75, np.zeros_like(trail_overlay), 0.25, 0)

    for box, kp in zip(results.boxes, results.keypoints):
        conf = float(box.conf[0])
        if conf < 0.5:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label = model.names[cls]
        
        # --- Draw bounding box ---
        cv2.rectangle(frame, (x1, y1), (x2, y2), neon_box_color, 2, cv2.LINE_8)
        cv2.rectangle(trail_overlay, (x1, y1), (x2, y2), neon_box_color, 1, cv2.LINE_8)

        # --- Label text ---
        text = f"{label} {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), neon_box_color, -1)
        cv2.putText(frame, text, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2, cv2.LINE_8)
        cv2.putText(frame, text, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_8)

        # --- Stick figure ---
        keypoints = kp.xy.cpu().numpy()[0]
        for idx, (x, y) in enumerate(keypoints):
            if x > 0 and y > 0:
                joint_color = joint_colors[idx % 2]
                cv2.circle(frame, (int(x), int(y)), 4, joint_color, -1)

        for a, b in skeleton:
            x1, y1 = keypoints[a]
            x2, y2 = keypoints[b]
            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                cv2.line(trail_overlay, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 1)


    # Apply trail
    frame = cv2.addWeighted(frame, 1.0, trail_overlay, 0.38, 0)


    out.write(frame)

# Done
cap.release()
out.release()

print("✅ Final video with boxes + labels + stick figures saved: video_output.mp4")
