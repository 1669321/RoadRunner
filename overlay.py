# overlay.py
import cv2

def draw_overlay(frame, car, detections, lateral_error=None, angle_deg=None):
    # 2️⃣ Panel de estado (esquina superior izquierda)
    panel = [
        f"STATE      : {car.state}",
        f"SPEED      : {car.speed:.2f} km/h",
        f"MAX SPD    : {car.max_speed:.2f} km/h",
        f"LATERAL ERR: {lateral_error:.3f}" if lateral_error is not None else "LATERAL ERR: N/A",
        f"CURVE ANGLE: {angle_deg:.2f} deg" if angle_deg is not None else "CURVE ANGLE: N/A",
        f"#DETECS    : {len(detections)}"
    ]
    for i, line in enumerate(panel):
        cv2.putText(frame, line, (10, 20 + 18 * i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2, cv2.LINE_AA)
