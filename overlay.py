# overlay.py
import cv2

def draw_overlay(frame, car, detections):
    # 1️⃣ Dibujar bounding-boxes
    for det in detections:
        x1,y1,x2,y2 = map(int, det["bbox"])
        label       = f"{det['class']} {det['conf']:.2f}"
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(frame, label, (x1, y1-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)

    # 2️⃣ Panel de estado (esquina superior izquierda)
    panel = [
        f"STATE   : {car.state}",
        f"SPEED   : {car.speed:.2f} m/s",
        f"MAX SPD : {car.max_speed:.2f} m/s",
        f"#DETECS : {len(detections)}"
    ]
    for i, line in enumerate(panel):
        cv2.putText(frame, line, (10, 20+18*i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2, cv2.LINE_AA)
