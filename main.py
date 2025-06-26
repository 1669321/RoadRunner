import cv2
import yaml
from sim_car import Car
from utils_processing import detect_lane_center_poly
from traffic_sign_detector import detect_signs
import re
from overlay import draw_overlay

DEBUG = False
OUTPUT_PATH = "output_video.mp4"

car = Car()

cap = cv2.VideoCapture("./videos/vid2.mp4")

# Obtener propiedades del video original
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Inicializar el escritor de video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # o 'MJPG', 'mp4v' si lo necesitas en .mp4
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

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
    return priorities.get(cls_name, 100)

saw_stop_sign = False
stop_triggered = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_for_signs = frame.copy()
    frame_for_lanes = frame.copy()

    frame_with_signs, detections = detect_signs(frame_for_signs)
    frame_with_lanes, lane_detected, lateral_error, angle_deg, debug_lanes = detect_lane_center_poly(frame_for_lanes)

    combined_frame = cv2.addWeighted(frame_with_signs, 0.5, frame_with_lanes, 0.5, 0)

    selected_brake_slow_action = None
    selected_brake_slow_priority = 1000
    max_speed_value = None
    stop_visible = False

    for det in detections:
        cls_name = det["class"]
        if cls_name not in events:
            continue

        ev = events[cls_name]
        action = ev["action"]

        if cls_name.lower() == "stop":
            stop_visible = True

        if action in ["BRAKE", "SLOW"]:
            if cls_name.lower() == "stop":
                continue
            prio = get_priority(cls_name)
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
                if (max_speed_value is None) or (speed_val > max_speed_value):
                    max_speed_value = speed_val

    if stop_visible:
        saw_stop_sign = True
        stop_triggered = False
    else:
        if saw_stop_sign and not stop_triggered:
            selected_brake_slow_action = "BRAKE"
            stop_triggered = True
            saw_stop_sign = False

    state, speed = car.update(
        lane_detected,
        selected_brake_slow_action,
        max_speed_value,
        angle_deg
    )

    if stop_triggered and state != "BRAKE":
        stop_triggered = False

    draw_overlay(combined_frame, car, detections, lateral_error, angle_deg)

    # Guardar el frame en el video
    out.write(combined_frame)

    cv2.imshow("Demo", combined_frame)

    if DEBUG:
        cv2.imshow("Mask White Filter", debug_lanes["mask_white_filter"])
        cv2.imshow("Edges Canny", debug_lanes["edges_canny"])
        cv2.imshow("Bird's Eye View", debug_lanes["birdseye"])
        cv2.imshow("Objects Mask", debug_lanes["objects_mask"])

    # Pausar si el coche está frenando
    while state == "BRAKE":
        state, speed = car.update(
            lane_detected,
            selected_brake_slow_action,
            max_speed_value,
            angle_deg
        )
        draw_overlay(combined_frame, car, detections, lateral_error, angle_deg)
        cv2.imshow("Demo", combined_frame)
        out.write(combined_frame)  # Seguir escribiendo durante la pausa
        if cv2.waitKey(100) == ord("q"):
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            exit()

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
