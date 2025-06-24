import cv2
import numpy as np
import tensorflow as tf
import yaml

# --- CONFIG ---
tflite_model_path = "./models/best_float16.tflite"
#image_path = "./ims/im4.jpg"
image_path = "./datasets/traffic_signs/valid/images/129_jpg.rf.df9201d1527c914346cfffc9e0941803.jpg"
input_size = 640
yaml_path = "./detectors.yaml"
# --- CARGAR LAS CLASES DESDE YAML ---
with open(yaml_path, "r") as f:
    data = yaml.safe_load(f)
class_names = data[0]["classes"]

def letterbox(img, new_size=640, color=(114,114,114)):
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

# --- Función para validar y corregir cajas ---
def validate_boxes(boxes, img_w, img_h):
    # Asegurar que xmin <= xmax y ymin <= ymax
    boxes[:, 0], boxes[:, 2] = np.minimum(boxes[:, 0], boxes[:, 2]), np.maximum(boxes[:, 0], boxes[:, 2])
    boxes[:, 1], boxes[:, 3] = np.minimum(boxes[:, 1], boxes[:, 3]), np.maximum(boxes[:, 1], boxes[:, 3])
    # Limitar al tamaño de la imagen
    boxes[:, 0] = np.clip(boxes[:, 0], 0, img_w - 1)
    boxes[:, 1] = np.clip(boxes[:, 1], 0, img_h - 1)
    boxes[:, 2] = np.clip(boxes[:, 2], 0, img_w - 1)
    boxes[:, 3] = np.clip(boxes[:, 3], 0, img_h - 1)
    # Eliminar cajas con ancho o alto <= 0
    widths = boxes[:, 2] - boxes[:, 0]
    heights = boxes[:, 3] - boxes[:, 1]
    valid_mask = (widths > 0) & (heights > 0)
    return boxes[valid_mask], valid_mask

# --- CARGAR Y PREPARAR IMAGEN ---
img = cv2.imread(image_path)
if img is None:
    raise ValueError(f"No se pudo cargar la imagen {image_path}")
orig_h, orig_w = img.shape[:2]
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img_padded, scale, pad = letterbox(img_rgb, new_size=input_size)
input_data = img_padded.astype(np.float32) / 255.0
input_data = np.expand_dims(input_data, axis=0)

# --- CARGAR MODELO TFLITE ---
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Ajustar canales si es necesario (modelo espera NCHW)
if input_details[0]['shape'][1] == 3:
    input_data = np.transpose(input_data, (0, 3, 1, 2))

# --- INFERENCIA ---
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
outputs = [interpreter.get_tensor(output['index']) for output in output_details]

# --- PROCESAR SALIDA ---
output = outputs[0]  # (1,1,46,8400)
output = np.squeeze(output)  # (46, 8400)
output = output.T           # (8400, 46)

boxes = output[:, 0:4]
objectness = output[:, 4]
class_probs = output[:, 5:]

class_ids = np.argmax(class_probs, axis=1)
class_scores = class_probs[np.arange(len(class_ids)), class_ids]
scores = objectness * class_scores

print(f"Total predicciones: {len(output)}")

print("Primeras 5 predicciones (raw):")
print(output[:5])

print(f"Objectness scores min={objectness.min()}, max={objectness.max()}")
print(f"Class scores min={class_scores.min()}, max={class_scores.max()}")

print(f"Scores min={scores.min()}, max={scores.max()}")

# --- FILTRAR CON UMBRAL CON INDICES ---
conf_threshold = 0.3
#idxs = np.where(scores > conf_threshold)[0]
idxs = np.where(class_scores > conf_threshold)[0]
print(f"Detecciones tras umbral ({conf_threshold}): {len(idxs)}")

boxes = boxes[idxs]
scores = scores[idxs]
class_ids = class_ids[idxs]

print("Class ids", class_ids[:])
print("Scores filtrados:", scores)
print("Clases filtradas:", [class_names[c] for c in class_ids])
print("Cajas filtradas (xywh normalizado):")
print(boxes)

# Convertir cajas a formato xyxy normalizado
boxes = xywh_to_xyxy(boxes)
print("Cajas convertidas a xyxy normalizadas:")
print(boxes)

# Convierte boxes normalizadas xyxy a pixeles en imagen padded (640x640)
boxes_px = boxes.copy()
boxes_px[:, [0, 2]] *= input_size
boxes_px[:, [1, 3]] *= input_size

# Ahora escala y ajusta padding
boxes_scaled = scale_coords(boxes_px, scale, pad, orig_w, orig_h)
print("Cajas escaladas a tamaño original (pixeles):")
print(boxes_scaled)

# Luego dibujar usando boxes_scaled, que son las coordenadas absolutas en la imagen original
for box, score, class_id in zip(boxes_scaled, scores, class_ids):
    x1, y1, x2, y2 = box
    if x2 <= x1 or y2 <= y1:
        print("Caja inválida, saltando:", box)
        continue
    label = f"{class_names[class_id]} {score:.2f}"
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, label, (x1, max(y1 - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

cv2.imshow("Predicciones", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
