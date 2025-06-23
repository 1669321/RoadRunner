from ultralytics import YOLO
import cv2, yaml
from car import Car
from utils import *

car = Car()
cap = cv2.VideoCapture("videos/driving_sample.mp4")

with open("detectors.yaml") as f:
    conf = yaml.safe_load(f)

model = YOLO(conf[0]['weights'])  # traffic_signs model

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, imgsz=conf[0]['imgsz'])[0]
    detections = []
    for box in results.boxes.data:
        cls_id = int(box[-1])
        cls_name = conf[0]['classes'][cls_id]
        detections.append({"class": cls_name})

    frame_with_lanes, lane_detected, lateral_error = detect_lane_center(frame)
    frame = frame_with_lanes

    state, speed = car.update(detections, lane_detected)

    # Dibujo
    for box in results.boxes.data:
        x1, y1, x2, y2, conf_score, cls = box
        cls_name = conf[0]['classes'][int(cls)]
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
        cv2.putText(frame, cls_name, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    cv2.putText(frame, f"STATE: {state}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f"SPEED: {speed}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Demo", frame)
    if cv2.waitKey(1) == ord("q"):
        break
