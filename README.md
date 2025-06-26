RoadRunner 🚗💨

RoadRunner es un proyecto de conducción autónoma que permite a un coche mantenerse dentro del carril, detectar obstáculos y reconocer señales de tráfico usando visión por computadora.

---

Tabla de Contenidos

- Qué es RoadRunner?
- Requisitos
- Cómo usar
- Características
- Estructura del proyecto
- Estado del desarrollo
- Autores
- Licencia

---

Qué es RoadRunner?

RoadRunner es un sistema diseñado para el control autónomo de un vehículo, que integra detección de carril, reconocimiento de señales de tráfico y detección de obstáculos mediante sensores y visión por computadora.

Este proyecto está pensado para implementarse en hardware embebido, como Raspberry Pi, con sensores y cámaras para la adquisición de datos en tiempo real.

---

Requisitos

Para ejecutar el proyecto, se necesitan las siguientes librerías y software:

- Python 3.9 o superior  
- OpenCV  
- NumPy  
- PyYAML  
- PyTorch (para los modelos .pt)  
- YOLO (para detección de objetos)  
- Otros sensores y controladores (Raspberry Pi, sensor ultrasonido HC-SR04, controladora L298N)  

---

Cómo usar

1. Clonar el repositorio:

    git clone https://github.com/1669321/RoadRunner.git  
    cd RoadRunner  

2. Instalar dependencias:

    pip install -r requirements.txt  

3. Ejecutar el sistema:

    python main.py  

> Asegúrate de tener conectada la cámara y sensores antes de iniciar.

---

Características

- Seguimiento de carril con visión por computadora.  
- Detección básica de obstáculos con sensores ultrasónicos.  
- Reconocimiento de señales de tráfico con modelos de deep learning.  
- Control del vehículo mediante controladora L298N y motores reductores.  

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
├── lane_detector/          # Módulo con funciones para detección de carril  
├── requirements.txt        # Lista de dependencias  
├── .gitignore              # Archivos ignorados por git  
└── README.md               # Este archivo  

---

Estado del desarrollo

- [x] Seguimiento de carril funcional  
- [x] Detección básica de obstáculos  
- [x] Reconocimiento de señales de tráfico  

---

Autores

- Roger González  
- Oriol Alarcón  
- Pau Díaz  
- Nil Caballero  

---

Licencia

Este proyecto está bajo licencia MIT.

---
