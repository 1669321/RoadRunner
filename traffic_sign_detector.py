# tflite_detector.py
import cv2
import numpy as np
import tensorflow as tf
import yaml

# --- CONFIG GLOBAL (modificable desde main) ---
TFLITE_MODEL_PATH = "./models/V2best_float16.tflite"
YAML_PATH = "./detectors.yaml"
INPUT_SIZE = 640

# --- CARGAR CLASES Y MODELO ---
with open(YAML_PATH, "r") as f:
    data = yaml.safe_load(f)
class_names = data["names"]

interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def detect_signs(image):
    orig_h, orig_w = image.shape[:2]
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    img_padded, scale, pad = letterbox(img_rgb, new_size=INPUT_SIZE)
    input_data = np.expand_dims(img_padded, axis=0).astype(np.float32) / 255.0

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
    boxes, scores, class_ids = boxes[idxs], scores[idxs], class_ids[idxs]

    boxes = xywh_to_xyxy(boxes)
    keep = non_max_suppression_global(boxes, scores, iou_threshold=0.5)

    boxes, scores, class_ids = boxes[keep], scores[keep], class_ids[keep]

    boxes_px = boxes.copy()
    boxes_px[:, [0, 2]] *= INPUT_SIZE
    boxes_px[:, [1, 3]] *= INPUT_SIZE
    boxes_scaled = scale_coords(boxes_px, scale, pad, orig_w, orig_h)

    detections = []
    frame_with_boxes = image.copy()

    for box, score, class_id in zip(boxes_scaled, scores, class_ids):
        x1, y1, x2, y2 = map(int, box)
        if x2 <= x1 or y2 <= y1:
            continue

        class_name = class_names[class_id + 1]
        detections.append({"class": class_name, "box": box, "score": float(score)})

        # Dibujar rectángulo y etiqueta
        color = (0, 255, 0)
        cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), color, 2)
        label = f"{class_name}: {score:.2f}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame_with_boxes, (x1, y1 - h - 4), (x1 + w, y1), color, -1)
        cv2.putText(frame_with_boxes, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)

    return frame_with_boxes, detections


# Funciones auxiliares aquí (sigmoid, letterbox, etc.)

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
