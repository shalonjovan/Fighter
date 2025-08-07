# networked_pose_game.py
import cv2
import mediapipe as mp
import csv
import os
import sys
import json
from pathlib import Path
from network import NetworkHandler  # Must be in same directory

# --- Network setup ---
is_host = sys.argv[1].lower() == "host"
net = NetworkHandler(is_host)

# --- Setup for video capture & output file ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

mp_pose = mp.solutions.pose

# -- Landmarks for hands and legs only --
hand_leg_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
hand_leg_connections = [
    (11,13), (13,15), (12,14), (14,16),
    (11,12), (23,24), (23,25), (25,27), (24,26), (26,28)
]

# --- Helpers ---
def classify_speed_change(speed):
    if speed > 0.15:
        return 'Strong'
    elif speed > 0.08:
        return 'Medium'
    else:
        return 'Low'

def detect_punch_and_kick_with_power(landmarks, prev_landmarks):
    punch_power = kick_power = None
    if prev_landmarks is None:
        return punch_power, kick_power

    punch_speeds = [
        abs(landmarks[idx][0] - prev_landmarks[idx][0])
        for idx in [15, 16] if idx in landmarks and idx in prev_landmarks
    ]
    if punch_speeds:
        max_punch_speed = max(punch_speeds)
        if max_punch_speed > 0.05:
            punch_power = classify_speed_change(max_punch_speed)

    kick_speeds = [
        abs(landmarks[idx][1] - prev_landmarks[idx][1])
        for idx in [27, 28] if idx in landmarks and idx in prev_landmarks
    ]
    if kick_speeds:
        max_kick_speed = max(kick_speeds)
        if max_kick_speed > 0.05:
            kick_power = classify_speed_change(max_kick_speed)

    return punch_power, kick_power

def get_body_bounding_box(landmarks, w, h):
    xs = [lm[0] * w for lm in landmarks.values()]
    ys = [lm[1] * h for lm in landmarks.values()]
    return min(xs), min(ys), max(xs), max(ys)

def check_movement_zone(min_x, min_y, max_x, max_y, w, h):
    zones = []
    if min_y < h * 0.1:
        zones.append('JUMP')
    if max_y > h * 0.9 and (max_y - min_y) * 0.6 < (max_y - h * 0.9):
        zones.append('CROTCH')
    if max_x < w * 0.1:
        zones.append('LEFT')
    if min_x > w * 0.9:
        zones.append('RIGHT')
    return zones

def draw_movement_zones(frame):
    h, w, _ = frame.shape
    overlay = frame.copy()
    zones = [
        ((0, 0, w, int(h * 0.1)), (255, 0, 0)),
        ((0, int(h * 0.9), w, h), (0, 255, 0)),
        ((0, 0, int(w * 0.1), h), (0, 255, 255)),
        ((int(w * 0.9), 0, w, h), (0, 0, 255))
    ]
    for (x1, y1, x2, y2), color in zones:
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

def draw_action_texts(frame, punch, kick, zones, opp=None):
    h, w, _ = frame.shape
    x, y = int(w * 0.05), int(h * 0.1)
    if punch:
        cv2.putText(frame, f'Punch: {punch}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    if kick:
        cv2.putText(frame, f'Kick: {kick}', (x, y+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    for i, zone in enumerate(zones):
        color = {'JUMP':(255,0,0),'CROTCH':(0,255,0),'LEFT':(0,255,255),'RIGHT':(0,0,255)}.get(zone, (255,255,255))
        cv2.putText(frame, zone, (int(w*0.85), y + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    if opp:
        cv2.putText(frame, f"Opponent: P:{opp.get('punch')} K:{opp.get('kick')} Z:{','.join(opp.get('zones', []))}",
                    (x, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

prev_landmarks = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        draw_movement_zones(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = pose.process(rgb)
        rgb.flags.writeable = True

        landmarks = {}
        punch = kick = None
        zones = []

        if result.pose_landmarks:
            h, w, _ = frame.shape
            for idx in hand_leg_landmarks:
                lm = result.pose_landmarks.landmark[idx]
                landmarks[idx] = (lm.x, lm.y, lm.z, lm.visibility)
            for start, end in hand_leg_connections:
                s, e = result.pose_landmarks.landmark[start], result.pose_landmarks.landmark[end]
                cv2.line(frame, (int(s.x*w), int(s.y*h)), (int(e.x*w), int(e.y*h)), (255,0,0), 2)
            for idx in hand_leg_landmarks:
                cx, cy = int(landmarks[idx][0]*w), int(landmarks[idx][1]*h)
                cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)

            punch, kick = detect_punch_and_kick_with_power(landmarks, prev_landmarks)
            if landmarks:
                min_x, min_y, max_x, max_y = get_body_bounding_box(landmarks, w, h)
                zones = check_movement_zone(min_x, min_y, max_x, max_y, w, h)
            prev_landmarks = landmarks

        net.send({"punch": punch, "kick": kick, "zones": zones})
        opponent_data = net.get_latest_data()

        draw_action_texts(frame, punch, kick, zones, opp=opponent_data)

        cv2.imshow("Pose Game", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
