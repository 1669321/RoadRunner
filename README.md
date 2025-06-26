RoadRunner 🚗💨

RoadRunner es un proyecto de conducción autónoma que permite a un coche mantenerse dentro del carril, detectar obstáculos y reconocer señales de tráfico usando visión por computadora.

---

Descripción

RoadRunner es un sistema de control autónomo de vehículos que integra:
- Detección y seguimiento de carril
- Reconocimiento de señales de tráfico mediante modelos de deep learning
- Detección de obstáculos con sensores ultrasónicos

Este sistema está pensado para implementarse en hardware embebido (ej. Raspberry Pi) usando cámaras y sensores para adquisición de datos en tiempo real y control de motores.

---

Características principales

- Seguimiento de carril con visión por computadora
- Detección básica de obstáculos con sensor ultrasonido HC-SR04
- Reconocimiento de señales de tráfico con PyTorch y modelos YOLO
- Control de vehículo con controladora L298N y motores reductores

---

Requisitos

- Python 3.9 o superior
- OpenCV
- NumPy
- PyYAML
- PyTorch
- YOLO (para detección de objetos)
- Hardware: Raspberry Pi, sensor ultrasonido HC-SR04, controladora L298N

---

Instalación

Clona el repositorio y instala las dependencias:

git clone https://github.com/1669321/RoadRunner.git
cd RoadRunner
pip install -r requirements.txt

---

Uso

Conecta la cámara y sensores antes de ejecutar el sistema.

Para iniciar la conducción autónoma:

python main.py

También puedes probar módulos específicos:

- Detección de carril:
  python test_line_detector.py
- Reconocimiento de señales en imagen:
  python tf_test.py
- Reconocimiento de señales en video:
  python tf_test_video.py

---

Estructura del proyecto

RoadRunner/
├── car.py                  # Lógica principal del vehículo  
├── main.py                 # Script principal de ejecución  
├── lane_detector.py        # Módulo para detección de carril  
├── overlay.py              # Visualización y superposición de información  
├── priorities.py           # Gestión de prioridades entre eventos  
├── events.yaml             # Configuración de eventos del coche  
├── detectors.yaml          # Configuración de detectores  
├── utils_processing.py     # Utilidades de procesamiento de imagen  
├── tf_test.py              # Test de reconocimiento de señales en foto  
├── tf_test_video.py        # Test de reconocimiento de señales en vídeo  
├── test_line_detector.py   # Test de detección de carril  
├── models/                 # Modelos entrenados (.pt)  
├── ims/                    # Imágenes de prueba  
├── videos/                 # Vídeos de prueba  
├── lane_detector/          # Funciones y utilidades de detección de carril  
├── requirements.txt        # Lista de dependencias  
├── .gitignore              # Archivos ignorados por git  
└── README.md               # Este archivo  

---

Estado del desarrollo

Funcionalidad                   | Estado      
------------------------------ | ----------- 
Seguimiento de carril           | Completo   
Detección básica de obstáculos  | Completo   
Reconocimiento de señales       | Completo   

---

Autores

- Roger González  
- Oriol Alarcón  
- Pau Díaz  
- Nil Caballero  

---

Licencia

Este proyecto está bajo la licencia MIT.

---

Referencias

- OpenCV: https://opencv.org/  
- PyTorch: https://pytorch.org/  
- YOLO: https://pjreddie.com/darknet/yolo/  
"""
