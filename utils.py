import numpy as np
import cv2

def detect_lane_center_poly(frame):
    def isolate_white_lane(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Ecualizar el canal V para normalizar brillo (rigidez ante imágenes con más/menos luz)
        v_eq = cv2.equalizeHist(v)

        # Recombinar y volver a BGR
        hsv_eq = cv2.merge([h, s, v_eq])
        img_eq = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2BGR)
        
        # Ahora filtrar blanco sobre la imagen ecualizada (color de las líneas)
        hsv2 = cv2.cvtColor(img_eq, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 210])
        upper_white = np.array([210, 80, 255])
        mask = cv2.inRange(hsv2, lower_white, upper_white)

        # Morfología para limpiar ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        res = cv2.bitwise_and(img_eq, img_eq, mask=mask)
        return res

    white_filtered = isolate_white_lane(frame)
    cv2.imshow("filtered", white_filtered)

    gray = cv2.cvtColor(white_filtered, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    cv2.imshow("edges", edges)

    height, width = edges.shape
    lane_detected = False
    masked_edges = None

    # Intentar con anchuras crecientes del polígono (de 60% a 90% ancho)
    widths = [0.68, 0.8, 0.9]
    for w in widths:
        mask = np.zeros_like(edges)
        poly_width = int(width * w)
        x_left = (width - poly_width) // 2
        x_right = x_left + poly_width
        polygon = np.array([[  
            (x_left, height),
            (x_right, height),
            (x_right, int(0.6 * height)),
            (x_left, int(0.6 * height))
        ]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked_edges_try = cv2.bitwise_and(edges, mask)
        if np.sum(masked_edges_try) > 1000:
            lane_detected = True
            masked_edges = masked_edges_try
            break
        
    if not lane_detected:
        # No se detecta línea con ninguna anchura
        return frame, False, 0

    cv2.imshow("Polygon", mask)
    cv2.imshow("masked edges", masked_edges)

    # Encuentra coordenadas de todos los bordes (píxeles blancos)
    ys, xs = np.where(masked_edges != 0)

    # Separar puntos en izquierdo y derecho según la posición relativa al centro
    car_center = width // 2
    left_xs = []
    left_ys = []
    right_xs = []
    right_ys = []

    for x, y in zip(xs, ys):
        if x < car_center:
            left_xs.append(x)
            left_ys.append(y)
        else:
            right_xs.append(x)
            right_ys.append(y)

    # Ajustar polinomio grado 2 (curva) para cada lado (y vs x)
    left_fit = None
    right_fit = None

    if len(left_xs) > 0:
        left_fit = np.polyfit(left_ys, left_xs, 2)
    if len(right_xs) > 0:
        right_fit = np.polyfit(right_ys, right_xs, 2)

    line_img = np.zeros_like(frame)

    y_vals = np.linspace(int(0.6 * height), height, num=100).astype(int)

    def draw_polyline(fit, color):
        if fit is None:
            return
        pts = []
        for y in y_vals:
            x = int(np.polyval(fit, y))
            pts.append((x, y))
        pts = np.array(pts, np.int32).reshape((-1,1,2))
        cv2.polylines(line_img, [pts], isClosed=False, color=color, thickness=5)

    # Dibuja curvas polinomiales para bordes izquierdo y derecho
    draw_polyline(left_fit, (255,0,0))   # azul
    draw_polyline(right_fit, (0,0,255))  # rojo

    # Dibujar línea amarilla (centro entre los dos carriles)
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
    pts_center = np.array(pts_center, np.int32).reshape((-1,1,2))
    cv2.polylines(line_img, [pts_center], isClosed=False, color=(0,255,255), thickness=3)

    combo = cv2.addWeighted(frame, 0.8, line_img, 1, 1)

    # Calcular error horizontal en la base (útil para saber cuánto girar)
    if left_fit is not None and right_fit is not None:
        left_x_bottom = int(np.polyval(left_fit, height))
        right_x_bottom = int(np.polyval(right_fit, height))
        lane_center = (left_x_bottom + right_x_bottom) // 2
    elif left_fit is not None:
        lane_center = int(np.polyval(left_fit, height)) + 200
    elif right_fit is not None:
        lane_center = int(np.polyval(right_fit, height)) - 200
    else:
        lane_center = car_center

    error = lane_center - car_center

    return combo, lane_detected, error
