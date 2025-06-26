import cv2
from ultralytics import YOLO

"""def inferir_y_mostrar(model_path, image_path):
    # Carga modelo YOLOv8
    model = YOLO(model_path)
    
    # Leer imagen
    img = cv2.imread(image_path)
    if img is None:
        print(f"No se pudo cargar la imagen en: {image_path}")
        return
    
    # Inferencia
    results = model(img)
    
    # results es una lista de objetos Results, tomamos el primero
    result = results[0]

    # Mostrar predicciones en consola (opcional)
    result.print()

    # Obtener imagen con predicciones dibujadas
    img_pred = result.plot()  # devuelve imagen con predicciones sobrepuestas (numpy array)

    # Mostrar con OpenCV
    cv2.imshow('Predicciones YOLOv8', img_pred)
    cv2.waitKey(0)
    cv2.destroyAllWindows()"""

# Ejemplo
model_path = './models/yolov8n.pt'
image_path = './ims/im6.jpg'

# Carga modelo YOLOv8
model = YOLO(model_path)

# Leer imagen
img = cv2.imread(image_path)
if img is None:
    print(f"No se pudo cargar la imagen en: {image_path}")

# Inferencia
results = model(img)

# results es una lista de objetos Results, tomamos el primero
result = results[0]
# Mostrar predicciones en consola (opcional)
result.print()
# Obtener imagen con predicciones dibujadas
img_pred = result.plot()  # devuelve imagen con predicciones sobrepuestas (numpy array)
# Mostrar con OpenCV
cv2.imshow('Predicciones YOLOv8', img_pred)
cv2.waitKey(0)
cv2.destroyAllWindows()
