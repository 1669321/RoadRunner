import cv2
import numpy as np
import tensorflow as tf
import yaml

# --- CONFIG ---
tflite_model_path = "./models/V2best_float16.tflite"
video_path = "./videos/vid2.mp4"  # Cambia esto por el path de tu video
input_size = 640
yaml_path = "./detectors.yaml"

# --- CARGAR LAS CLASES DESDE YAML ---
with open(yaml_path, "r") as f:
    data = yaml.safe_load(f)
class_names = data[0]["classes"]

def compute_iou(box, boxes):
    x_min = np.maximum(box[0], boxes[:, 0])
    y_min = np.maximum(box[1], boxes[:, 1])
    x_max = np.minimum(box[2], boxes[:, 2])
    y_max = np.minimum(box[3], boxes[:, 3])
    inter_area = np.maximum(0, x_max - x_min) * np.maximum(0, y_max - y_min)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - inter_area
    return inter_area / union_area

def non_max_suppression_global(boxes, scores, iou_threshold=0.5):
    order = scores.argsort()[::-1]
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)
        if len(order) == 1:
            break
        ious = compute_iou(boxes[i], boxes[order[1:]])
        order = order[1:][ious < iou_threshold]
    return keep

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def letterbox(img, new_size=640, color=(0,0,0)):
    h, w = img.shape[:2]
    scale = new_size / max(h, w)
    nh, nw = int(h * scale), int(w * scale)
    img_resized = cv2.resize(img, (nw, nh))
    top = (new_size - nh) // 2
    bottom = new_size - nh - top
    left = (new_size - nw) // 2
    right = new_size - nw - left
    img_padded = cv2.copyMakeBorder(img_resized, top, bottom, left, right,
                                    cv2.BORDER_CONSTANT, value=color)
    return img_padded, scale, (left, top)

def xywh_to_xyxy(xywh):
    x, y, w, h = xywh.T
    xmin = x - w / 2
    ymin = y - h / 2
    xmax = x + w / 2
    ymax = y + h / 2
    return np.stack([xmin, ymin, xmax, ymax], axis=1)

def scale_coords(boxes, scale, pad, orig_w, orig_h):
    left, top = pad
    boxes[:, [0, 2]] -= left
    boxes[:, [1, 3]] -= top
    boxes /= scale
    boxes[:, 0] = np.clip(boxes[:, 0], 0, orig_w)
    boxes[:, 2] = np.clip(boxes[:, 2], 0, orig_w)
    boxes[:, 1] = np.clip(boxes[:, 1], 0, orig_h)
    boxes[:, 3] = np.clip(boxes[:, 3], 0, orig_h)
    return boxes.astype(np.int32)

# --- CARGAR MODELO TFLITE ---
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# --- ABRIR VIDEO ---
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"No se pudo abrir el video: {video_path}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    orig_h, orig_w = frame.shape[:2]
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_padded, scale, pad = letterbox(img_rgb, new_size=input_size)
    input_data = np.expand_dims(img_padded, axis=0).astype(np.float32) / 255.0

    # --- INFERENCIA ---
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    outputs = [interpreter.get_tensor(output['index']) for output in output_details]

    output = outputs[0].squeeze().T
    output[:, 4:] = sigmoid(output[:, 4:])

    boxes = output[:, 0:4]
    objectness = output[:, 4]
    class_probs = output[:, 5:]

    class_ids = np.argmax(class_probs, axis=1)
    class_scores = class_probs[np.arange(len(class_ids)), class_ids]
    scores = objectness * class_scores

    conf_threshold = 0.3
    idxs = np.where(scores > conf_threshold)[0]

    boxes = boxes[idxs]
    scores = scores[idxs]
    class_ids = class_ids[idxs]

    boxes = xywh_to_xyxy(boxes)
    keep = non_max_suppression_global(boxes, scores, iou_threshold=0.5)
    boxes = boxes[keep]
    scores = scores[keep]
    class_ids = class_ids[keep]

    boxes_px = boxes.copy()
    boxes_px[:, [0, 2]] *= input_size
    boxes_px[:, [1, 3]] *= input_size
    boxes_scaled = scale_coords(boxes_px, scale, pad, orig_w, orig_h)

    # Dibujar cajas
    for box, score, class_id in zip(boxes_scaled, scores, class_ids):
        x1, y1, x2, y2 = box
        if x2 <= x1 or y2 <= y1:
            continue
        label = f"{class_names[class_id + 1]} {score:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Video con detecciones", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
