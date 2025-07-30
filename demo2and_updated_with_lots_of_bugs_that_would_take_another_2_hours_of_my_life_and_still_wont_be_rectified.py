import cv2
import mediapipe as mp
import csv
import os
from pathlib import Path

# --- Setup for video capture & output file ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

downloads_path = str(Path.home() / "Downloads")
csv_file_path = os.path.join(downloads_path, "pose_data.csv")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# -- Landmarks for hands and legs only --
hand_leg_landmarks = [
    11, 12, 13, 14, 15, 16,     # shoulders, elbows, wrists
    23, 24, 25, 26, 27, 28      # hips, knees, ankles
]
hand_leg_connections = [
    (11,13), (13,15), (12,14), (14,16),
    (11,12), (23,24),
    (23,25), (25,27), (24,26), (26,28)
]

# --- Write CSV headers with only selected points ---
csv_file = open(csv_file_path, mode='w', newline='')
csv_writer = csv.writer(csv_file)
header = ["frame"]
for i in hand_leg_landmarks:
    header.extend([f"landmark_{i}_x", f"landmark_{i}_y", f"landmark_{i}_z", f"landmark_{i}_visibility"])
csv_writer.writerow(header)

# --- Classification helpers and new detection logic ---
def classify_speed_change(speed):
    """Classify speed to Low, Medium, or Strong based on magnitude."""
    if speed > 0.15:
        return 'Strong'
    elif speed > 0.08:
        return 'Medium'
    else:
        return 'Low'

def detect_punch_and_kick_with_power(landmarks, prev_landmarks):
    """Detect punch and kick power levels: returns (punch_power, kick_power) or None if no action."""
    punch_power = None
    kick_power = None

    if prev_landmarks is None:
        return punch_power, kick_power

    punch_speeds = []
    for idx in [15, 16]:  # Left and right wrist
        if idx in landmarks and idx in prev_landmarks:
            speed = abs(landmarks[idx][0] - prev_landmarks[idx][0])
            punch_speeds.append(speed)
    max_punch_speed = max(punch_speeds) if punch_speeds else 0
    punch_power = classify_speed_change(max_punch_speed) if max_punch_speed > 0.05 else None

    kick_speeds = []
    for idx in [27, 28]:  # Left and right ankle
        if idx in landmarks and idx in prev_landmarks:
            speed = abs(landmarks[idx][1] - prev_landmarks[idx][1])
            kick_speeds.append(speed)
    max_kick_speed = max(kick_speeds) if kick_speeds else 0
    kick_power = classify_speed_change(max_kick_speed) if max_kick_speed > 0.05 else None

    return punch_power, kick_power

def get_body_bounding_box(landmarks, image_width, image_height):
    xs = [lm[0] * image_width for lm in landmarks.values()]
    ys = [lm[1] * image_height for lm in landmarks.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    return min_x, min_y, max_x, max_y

def check_movement_zone(min_x, min_y, max_x, max_y, image_width, image_height):
    """Return which movement zones the body bounding box intersects."""
    zones = []
    top_zone = image_height * 0.1
    bottom_zone = image_height * 0.9
    left_zone = image_width * 0.1
    right_zone = image_width * 0.9

    if min_y < top_zone:
        zones.append('JUMP')
    # CROTCH: majority of body in bottom
    body_height = max_y - min_y
    overlap_bottom = max_y > bottom_zone
    if overlap_bottom and (body_height * 0.6) < (max_y - bottom_zone):
        zones.append('CROTCH')
    if max_x < left_zone:
        zones.append('LEFT')
    if min_x > right_zone:
        zones.append('RIGHT')

    return zones

def draw_movement_zones(frame):
    overlay = frame.copy()
    height, width, _ = frame.shape

    zones = [
        {'name': 'JUMP', 'color': (255, 0, 0), 'coords': (0, 0, width, int(height * 0.1))},          # Blue Top
        {'name': 'CROTCH', 'color': (0, 255, 0), 'coords': (0, int(height * 0.9), width, height)},  # Green Bottom
        {'name': 'LEFT', 'color': (0, 255, 255), 'coords': (0, 0, int(width * 0.1), height)},      # Yellow Left
        {'name': 'RIGHT', 'color': (0, 0, 255), 'coords': (int(width * 0.9), 0, width, height)},   # Red Right
    ]

    alpha = 0.5
    for zone in zones:
        x1, y1, x2, y2 = zone['coords']
        cv2.rectangle(overlay, (x1, y1), (x2, y2), zone['color'], -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

# --- Draw the action and movement texts on window sides ---
def draw_action_texts(frame, punch_power, kick_power, movement_zones):
    height, width, _ = frame.shape
    # Left: Punch/Kick powers
    y_start = int(height * 0.1)
    x_left = int(width * 0.05)
    if punch_power:
        cv2.putText(frame, f'Punch: {punch_power}', (x_left, y_start), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
    if kick_power:
        cv2.putText(frame, f'Kick: {kick_power}', (x_left, y_start + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
    # Right: Movement (JUMP, CROTCH, LEFT, RIGHT)
    x_right = int(width * 0.85)
    y_movement_start = int(height * 0.1)
    for i, zone in enumerate(movement_zones):
        color_map = {
            'JUMP': (255, 0, 0),
            'CROTCH': (0, 255, 0),
            'LEFT': (0, 255, 255),
            'RIGHT': (0, 0, 255),
        }
        color = color_map.get(zone, (255, 255, 255))
        cv2.putText(frame, zone, (x_right, y_movement_start + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

prev_landmarks = None
frame_count = 0

with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        draw_movement_zones(frame)  # Draw the colored, 50% transparent movement regions

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = pose.process(rgb_frame)
        rgb_frame.flags.writeable = True
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        landmarks_list = {}
        if results.pose_landmarks:
            h, w, _ = frame.shape
            # Draw only arm and leg landmarks/connections
            for connection in hand_leg_connections:
                start_idx, end_idx = connection
                start = results.pose_landmarks.landmark[start_idx]
                end = results.pose_landmarks.landmark[end_idx]
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(frame, start_point, end_point, (255,0,0), 2)
            for idx in hand_leg_landmarks:
                landmark = results.pose_landmarks.landmark[idx]
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)
                landmarks_list[idx] = (landmark.x, landmark.y, landmark.z, landmark.visibility)

            # --- Action and movement detection
            punch_power, kick_power = detect_punch_and_kick_with_power(landmarks_list, prev_landmarks)
            if landmarks_list:
                min_x, min_y, max_x, max_y = get_body_bounding_box(landmarks_list, frame.shape[1], frame.shape[0])
                movement_zones = check_movement_zone(min_x, min_y, max_x, max_y, frame.shape[1], frame.shape[0])
            else:
                movement_zones = []

            draw_action_texts(frame, punch_power, kick_power, movement_zones)

            # --- Write selected landmark data to CSV
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
        else:
            # still increment frame & write placeholder if no landmarks detected
            row = [frame_count] + [0] * (len(hand_leg_landmarks) * 4)
            csv_writer.writerow(row)
            frame_count += 1

        cv2.imshow("MediaPipe Pose - Press 'q' to Quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
csv_file.close()
cv2.destroyAllWindows()
print(f"Pose data saved to: {csv_file_path}")
