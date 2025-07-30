import cv2
import mediapipe as mp
import csv
import os
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")
csv_file_path = os.path.join(downloads_path, "pose_data.csv")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

landmark_style = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
connection_style = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)

hand_leg_landmarks = [
    11, 12, 13, 14, 15, 16,     # shoulders, elbows, wrists
    23, 24, 25, 26, 27, 28      # hips, knees, ankles
]
hand_leg_connections = [
    (11,13), (13,15), (12,14), (14,16),    # arms
    (11,12), (23,24),                     # shoulders/hips
    (23,25), (25,27), (24,26), (26,28)    # legs
]

csv_file = open(csv_file_path, mode='w', newline='')
csv_writer = csv.writer(csv_file)
header = ["frame"]
for i in hand_leg_landmarks:
    header.extend([f"landmark_{i}_x", f"landmark_{i}_y", f"landmark_{i}_z", f"landmark_{i}_visibility"])
csv_writer.writerow(header)

def detect_punch_and_kick(landmarks, prev_landmarks):
    punch_detected = False
    kick_detected = False

    if prev_landmarks is None:
        return punch_detected, kick_detected

    for idx in [15, 16]:  # Left and right wrist
        if abs(landmarks[idx][0] - prev_landmarks[idx][0]) > 0.07:
            punch_detected = True

    for idx in [27, 28]:  # Left and right ankle
        if abs(landmarks[idx][1] - prev_landmarks[idx][1]) > 0.08:
            kick_detected = True

    return punch_detected, kick_detected

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_landmarks = None
frame_count = 0

with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = pose.process(rgb_frame)
        rgb_frame.flags.writeable = True
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        landmarks_list = {}
        if results.pose_landmarks:
            # Draw only arm and leg landmarks/connections
            for connection in hand_leg_connections:
                start_idx, end_idx = connection
                start = results.pose_landmarks.landmark[start_idx]
                end = results.pose_landmarks.landmark[end_idx]
                h, w, _ = frame.shape
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(frame, start_point, end_point, (255,0,0), 2)
            for idx in hand_leg_landmarks:
                landmark = results.pose_landmarks.landmark[idx]
                h, w, _ = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)
                landmarks_list[idx] = (landmark.x, landmark.y, landmark.z, landmark.visibility)

            punch, kick = detect_punch_and_kick(landmarks_list, prev_landmarks)
            if punch:
                cv2.putText(frame, 'Punch', (50,80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 5, cv2.LINE_AA)
            if kick:
                cv2.putText(frame, 'Kick', (50,160), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 5, cv2.LINE_AA)

            # Write selected landmark data to CSV
            row = [frame_count]
            for i in hand_leg_landmarks:
                if i in landmarks_list:
                    lm = landmarks_list[i]
                    row.extend([lm[0], lm[1], lm[2], lm[3]])
                else:
                    row.extend([0,0,0,0])
            csv_writer.writerow(row)

            prev_landmarks = landmarks_list
            frame_count += 1

        # Resize display window to HD resolution
        frame = cv2.resize(frame, (1280, 720))

        cv2.imshow("MediaPipe Pose - Press 'q' to Quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
csv_file.close()
cv2.destroyAllWindows()
print(f"Pose data saved to: {csv_file_path}")
