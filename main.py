from ultralytics import YOLO
import cv2
import yaml
from car import Car
from utils_processing import detect_lane_center

def read_distance_sensor():
    # Aquí iría la lectura real del sensor de distancia,
    # por ahora devolvemos un valor simulado (ej. 2.0 metros)
    # Cambia este valor para probar la lógica.
    return 2.0

car = Car()

# VideoCapture 0 para camara o path para cargar video
cap = cv2.VideoCapture(0)

with open("detectors.yaml") as f:
    conf = yaml.safe_load(f)

model = YOLO(conf[0]['weights'])  # modelo detección señales

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Detección de señales
    results = model(frame, imgsz=conf[0]['imgsz'])[0]
    detections = []
    for box in results.boxes.data:
        cls_id = int(box[-1])
        cls_name = conf[0]['classes'][cls_id]
        detections.append({"class": cls_name})

    # Detección de carril
    frame_with_lanes, lane_detected, lateral_error = detect_lane_center(frame)

    # Leer sensor de distancia
    distance = read_distance_sensor()

    # Actualizar estado del coche con detecciones y sensor
    state, speed = car.update(detections, lane_detected, distance_sensor=distance)

    # Visualización: dibujar cajas señales sobre la imagen con carril
    for box in results.boxes.data:
        x1, y1, x2, y2, conf_score, cls = box
        cls_name = conf[0]['classes'][int(cls)]
        cv2.rectangle(frame_with_lanes, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
        cv2.putText(frame_with_lanes, cls_name, (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Mostrar estado y velocidad
    cv2.putText(frame_with_lanes, f"STATE: {state}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame_with_lanes, f"SPEED: {speed:.2f}", (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    # Mostrar la imagen con detecciones y carril
    cv2.imshow("Demo", frame_with_lanes)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
