import numpy as np
import cv2
import torch

# Cargar modelo YOLOv5 una vez
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

classes_to_mask = ['car', 'stop sign', 'traffic light', 'truck', 'bus']

def mask_detected_objects(frame):
    results = model(frame)
    df = results.pandas().xyxy[0]
    mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255
    for _, row in df.iterrows():
        cls_name = row['name']
        if cls_name in classes_to_mask:
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            cv2.rectangle(mask, (x1, y1), (x2, y2), 0, thickness=-1)
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
    return masked_frame, mask

def detect_lane_center_poly(frame):
    clean_frame, mask_objects = mask_detected_objects(frame)
    height, width = clean_frame.shape[:2]

    # Definir puntos para bird's eye view
    src = np.float32([
        [width * 0.45, height * 0.63],
        [width * 0.55, height * 0.63],
        [width * 0.9, height * 0.95],
        [width * 0.1, height * 0.95]
    ])

    dst = np.float32([
        [width * 0.2, 0],
        [width * 0.8, 0],
        [width * 0.8, height],
        [width * 0.2, height]
    ])

    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)

    birdseye = cv2.warpPerspective(clean_frame, M, (width, height))

    # Función para aislar las líneas blancas
    def isolate_white_lane(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v_eq = cv2.equalizeHist(v)
        hsv_eq = cv2.merge([h, s, v_eq])
        img_eq = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2BGR)
        hsv2 = cv2.cvtColor(img_eq, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 220])
        upper_white = np.array([220, 80, 255])
        mask = cv2.inRange(hsv2, lower_white, upper_white)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        return mask, cv2.bitwise_and(img_eq, img_eq, mask=mask)

    mask, white_filtered = isolate_white_lane(birdseye)

    gray = cv2.cvtColor(white_filtered, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    lane_detected = False
    masked_edges = None

    widths = [0.68, 0.8, 0.9]
    height_be, width_be = edges.shape
    for w in widths:
        mask_poly = np.zeros_like(edges)
        poly_width = int(width_be * w)
        x_left = (width_be - poly_width) // 2
        x_right = x_left + poly_width
        polygon = np.array([[  
            (x_left, height_be),
            (x_right, height_be),
            (x_right, int(0.6 * height_be)),
            (x_left, int(0.6 * height_be))
        ]], np.int32)
        cv2.fillPoly(mask_poly, polygon, 255)
        masked_edges_try = cv2.bitwise_and(edges, mask_poly)
        if np.sum(masked_edges_try) > 1000:
            lane_detected = True
            masked_edges = masked_edges_try
            break

    if not lane_detected:
        cv2.imshow("Mask White Filter", mask)
        cv2.imshow("Edges Canny", edges)
        cv2.imshow("Bird's Eye View", birdseye)
        cv2.imshow("Masked Edges", np.zeros_like(edges))
        cv2.imshow("Objects Mask", mask_objects)
        return frame, False, 0, 0

    ys, xs = np.where(masked_edges != 0)

    car_center = width_be // 2
    left_xs, left_ys, right_xs, right_ys = [], [], [], []

    for x, y in zip(xs, ys):
        if x < car_center:
            left_xs.append(x)
            left_ys.append(y)
        else:
            right_xs.append(x)
            right_ys.append(y)

    left_fit, right_fit = None, None
    if len(left_xs) > 0:
        left_fit = np.polyfit(left_ys, left_xs, 2)
    if len(right_xs) > 0:
        right_fit = np.polyfit(right_ys, right_xs, 2)

    line_img = np.zeros_like(birdseye)

    y_vals = np.linspace(int(0.6 * height_be), height_be, num=100).astype(int)

    def draw_polyline(fit, color):
        if fit is None:
            return
        pts = []
        for y in y_vals:
            x = int(np.polyval(fit, y))
            pts.append((x, y))
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        cv2.polylines(line_img, [pts], isClosed=False, color=color, thickness=5)

    draw_polyline(left_fit, (255, 0, 0))   # azul
    draw_polyline(right_fit, (0, 0, 255))  # rojo

    pts_center = []
    for y in y_vals:
        if left_fit is not None and right_fit is not None:
            x_left = int(np.polyval(left_fit, y))
            x_right = int(np.polyval(right_fit, y))
            x_center = (x_left + x_right) // 2
        elif left_fit is not None:
            x_center = int(np.polyval(left_fit, y)) + 200
        elif right_fit is not None:
            x_center = int(np.polyval(right_fit, y)) - 200
        else:
            x_center = car_center
        pts_center.append((x_center, y))
    pts_center = np.array(pts_center, np.int32).reshape((-1, 1, 2))
    cv2.polylines(line_img, [pts_center], isClosed=False, color=(0, 255, 255), thickness=3)

    # Warp inverso para volver a la perspectiva original
    line_img_warped_back = cv2.warpPerspective(line_img, Minv, (width, height))

    combo = cv2.addWeighted(frame, 0.8, line_img_warped_back, 1, 1)

    # Calcular posición del carril en la parte inferior de la imagen birdseye
    if left_fit is not None and right_fit is not None:
        left_x_bottom = int(np.polyval(left_fit, height_be))
        right_x_bottom = int(np.polyval(right_fit, height_be))
        lane_center = (left_x_bottom + right_x_bottom) // 2
    elif left_fit is not None:
        lane_center = int(np.polyval(left_fit, height_be)) + 200
    elif right_fit is not None:
        lane_center = int(np.polyval(right_fit, height_be)) - 200
    else:
        lane_center = car_center

    lateral_error = lane_center - car_center

    # Calcular ángulo de la curva en la parte inferior
    y_eval = height_be
    y_delta = 10
    if left_fit is not None and right_fit is not None:
        center_fit = (left_fit + right_fit) / 2
    elif left_fit is not None:
        center_fit = left_fit
    elif right_fit is not None:
        center_fit = right_fit
    else:
        center_fit = np.array([0, 0, car_center])

    x1 = np.polyval(center_fit, y_eval)
    x2 = np.polyval(center_fit, y_eval - y_delta)

    dx = x2 - x1
    dy = y_delta

    angle_rad = np.arctan2(dx, dy)
    angle_deg = np.degrees(angle_rad)

    # Mostrar imágenes para debug
    cv2.imshow("Mask White Filter", mask)
    cv2.imshow("Edges Canny", edges)
    cv2.imshow("Bird's Eye View", birdseye)
    cv2.imshow("Bird's Eye with Lines", line_img)
    cv2.imshow("Objects Mask", mask_objects)

    return combo, lane_detected, lateral_error, angle_deg
