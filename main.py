import cv2
import yaml
from car import Car
from utils_processing import detect_lane_center_poly
from traffic_sign_detector import detect_signs
import re
from overlay import draw_overlay

DEBUG = False

car = Car()

cap = cv2.VideoCapture('./videos/vid2.mp4')

with open("detectors.yaml") as f:
    conf = yaml.safe_load(f)

with open("events.yaml") as f:
    events = yaml.safe_load(f)

with open("priorities.yaml") as f:
    priorities = yaml.safe_load(f)

def parse_speed(value_str):
    m = re.match(r"speed_(\d+)", value_str)
    if m:
        return float(m.group(1))
    return None

def get_priority(cls_name):
    # Simplemente devuelve la prioridad según priorities.yaml o 100 si no está
    return priorities.get(cls_name, 100)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Copiasr para dibujo sin afectar el frame original usado en detección
    frame_for_signs = frame.copy()
    frame_for_lanes = frame.copy()

    frame_with_signs, detections = detect_signs(frame_for_signs)
    frame_with_lanes, lane_detected, lateral_error, angle_deg, debug_lanes = detect_lane_center_poly(frame_for_lanes)

    # Fusionamos ambos overlays
    combined_frame = cv2.addWeighted(frame_with_signs, 0.5, frame_with_lanes, 0.5, 0)

    selected_brake_slow_action = None
    selected_brake_slow_priority = 1000
    max_speed_value = None

    for det in detections:
        cls_name = det["class"]
        if cls_name not in events:
            continue

        ev = events[cls_name]
        action = ev["action"]

        if action in ["BRAKE", "SLOW"]:
            prio = get_priority(cls_name)
            # Solo actualizamos si la prioridad es mejor (número menor)
            # Sirve para decidir entre SLOW y BRAKE
            if prio < selected_brake_slow_priority:
                selected_brake_slow_priority = prio
                selected_brake_slow_action = action

        elif action == "SET_SPEED":
            val = ev.get("value")
            speed_val = None
            if val == "parse_speed":
                speed_val = parse_speed(cls_name)
            else:
                try:
                    speed_val = float(val)
                except:
                    speed_val = None

            if speed_val is not None:
                # Escoger la velocidad máxima detectada 
                if (max_speed_value is None) or (speed_val > max_speed_value):
                    max_speed_value = speed_val

    # Llamamos a update con las dos acciones separadas
    state, speed = car.update(
        lane_detected,
        action_brake_slow=selected_brake_slow_action,
        action_speed=max_speed_value
    )

    draw_overlay(combined_frame, car, detections, lateral_error, angle_deg)

    cv2.imshow("Demo", combined_frame)

    if DEBUG:
        cv2.imshow("Mask White Filter", debug_lanes["mask_white_filter"])
        cv2.imshow("Edges Canny", debug_lanes["edges_canny"])
        cv2.imshow("Bird's Eye View", debug_lanes["birdseye"])
        cv2.imshow("Objects Mask", debug_lanes["objects_mask"])

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
