import cv2
from utils_processing import *

cv2.namedWindow("Original | Carriles Detectados", cv2.WINDOW_NORMAL)  # ventana redimensionable
cv2.resizeWindow("Original | Carriles Detectados", 800, 800)          # tamaño deseado

image = True
video = False

if image:
    # Cargar imagen original
    original = cv2.imread("./ims/im6.jpg")

    # Procesar para detectar carriles
    processed, lane_detected, lateral_error, angle, debug_ims = detect_lane_center_poly(original.copy())

    cv2.imshow("objects_mask", debug_ims["objects_mask"])
    


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

    cv2.putText(
            processed,
            f"Curvature angle: {angle:.2f} deg",
            (30, 80),  # un poco más abajo para no solapar el texto del error lateral
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

if video:
    # Ruta del video (puede ser un archivo .mp4 o un dispositivo cámara, ej: 0)
    video_path = "./videos/line_detector.avi"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error al abrir el video o cámara")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # fin del video

        processed, lane_detected, lateral_error, angle, debug_ims = detect_lane_center_poly(frame.copy())

        cv2.putText(
            processed,
            f"Lateral error: {lateral_error:.2f}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        cv2.putText(
            processed,
            f"Curvature angle: {angle:.2f} deg",
            (30, 80),  # un poco más abajo para no solapar el texto del error lateral
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        combined = cv2.hconcat([frame, processed])
        cv2.imshow("Original | Carriles Detectados", combined)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
