import cv2
from utils import *

cv2.namedWindow("Original | Carriles Detectados", cv2.WINDOW_NORMAL)  # ventana redimensionable
cv2.resizeWindow("Original | Carriles Detectados", 1000, 1000)          # tamaño deseado

# Cargar imagen original
#original = cv2.imread("./ims/im2.jpg")
#original = cv2.imread("./ims/im3.jpeg")
original = cv2.imread("./ims/im4.jpg")

# Procesar para detectar carriles
processed, lane_detected, lateral_error = detect_lane_center_poly(original.copy())

# Dibujar el error lateral como texto en la imagen procesada
cv2.putText(
    processed,
    f"Lateral error: {lateral_error:.2f}",
    (30, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 255),
    2
)

# Concatenar original + procesada
combined = cv2.hconcat([original, processed])

# Mostrar
cv2.imshow("Original | Carriles Detectados", combined)
cv2.waitKey(0)
cv2.destroyAllWindows()
