# RoadRunner 🚗💨

**RoadRunner** es un sistema de conducción autónoma diseñado para que un coche sea capaz de mantenerse dentro del carril, detectar obstáculos en su trayectoria y reconocer señales de tráfico utilizando visión por computadora.

## 🎯 Objetivos del proyecto

- ✅ Mantener el coche dentro de su carril de forma autónoma.
- ✅ Detectar obstáculos u objetos en la ruta.
- ✅ Reconocer señales de tráfico usando una cámara.


## 🧠 Tecnologías utilizadas

- Python
- OpenCV (visión por computadora)
- TensorFlow / PyTorch (reconocimiento de señales)
- Raspberry Pi (hardware de control)
- Sensores ultrasónicos (detección de obstáculos)
- Cámara Raspberry Pi v2(reconocimiento visual)

## ⚙️ Requisitos

- Python 3.9+
- OpenCV
- NumPy
- PyYAML
- Torch (para modelos `.pt`)
- Yolo

## 🧩 Hardware utilizado

- Raspberry Pi 4  
- Cámara Raspberry Pi v2  
- Controladora L298N  
- 2x Motores con reductora N20  
- Sensor de distancia por ultrasonidos HC-SR04  
- Powerbank  
- Petaca de pilas 4 AA

## 🚀 Instalación y ejecución

1. Cloná este repositorio:

```bash
git clone https://github.com/1669321/RoadRunner.git
cd RoadRunner
```

2. Instalá las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutá el programa principal:

```bash
python main.py
```

> 💡 Asegurate de tener conectada la cámara y los sensores antes de ejecutar el código.

## 📸 Ejemplos de funcionamiento

| Detección de carril | Reconocimiento de señal | 
|---------------------|--------------------------|
| ![lane](docs/img/lane.png) | ![sign](docs/img/sign.png) |

## 📁 Estructura del proyecto

```
RoadRunner/
├── car.py # Lógica principal del coche
├── main.py # Script principal del sistema
├── lane_detector.py # Detección de líneas de carril
├── overlay.py # Visualización y superposición de datos
├── priorities.py # Gestión de prioridades entre eventos
├── events.yaml # Configuración de eventos del coche
├── detectors.yaml # Configuración de los detectores
├── utils_processing.py # Utilidades de procesamiento de imagen
├── tf_test.py # Prueba de detección de señales (foto)
├── tf_test_video.py # Prueba de detección de señales (vídeo)
├── test_line_detector.py # Test de detección de carril
├── models/ # Modelos entrenados (.pt)
├── ims/ # Imágenes para pruebas o visualización
├── videos/ # Vídeos de ejemplo
├── lane_detector/ # Módulo de detección de carril
├── requirements.txt # Dependencias del proyecto
├── .gitignore # Ignorados por Git
└── README.md # Este archivo
```

## 🧪 Estado del desarrollo

- [x] Seguimiento de carril funcional
- [x] Detección de obstáculos básica
- [x] Reconocimiento de señales de tráfico


## 🤝 Autores

- Roger González  
- Oriol Alarcón  
- Pau Díaz  
- Nil Caballero  
