
<!--
README.md para RoadRunner
Este archivo describe un sistema de conducción autónoma basado en Python
y visión por computadora, inspirado en el estilo del proyecto PythonRobotics.
-->

# RoadRunner 🚗💨  
Sistema de conducción autónoma con visión por computadora

---

## 📚 Tabla de contenidos

- [¿Qué es RoadRunner?](#qué-es-roadrunner)
- [Objetivos del proyecto](#objetivos-del-proyecto)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Hardware](#hardware)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Ejemplos visuales](#ejemplos-visuales)
- [Estado del desarrollo](#estado-del-desarrollo)
- [Cómo contribuir](#cómo-contribuir)
- [Licencia](#licencia)
- [Autores](#autores)

---

## ¿Qué es RoadRunner?

**RoadRunner** es un sistema de conducción autónoma desarrollado con Python y visión por computadora. Su objetivo es permitir que un vehículo se mantenga dentro del carril, detecte obstáculos y reconozca señales de tráfico en tiempo real, utilizando hardware accesible como la Raspberry Pi.

---

## Objetivos del proyecto

- ✅ Mantener el coche dentro del carril de forma autónoma.  
- ✅ Detectar obstáculos u objetos en la ruta.  
- ✅ Reconocer señales de tráfico usando una cámara.

---

## Tecnologías utilizadas

- Python 3.9+
- OpenCV (visión por computadora)
- TensorFlow / PyTorch (reconocimiento de señales)
- YOLO (detección de objetos)
- NumPy, PyYAML
- Raspberry Pi OS

---

## Hardware

- Raspberry Pi 4  
- Cámara Raspberry Pi v2  
- Controladora L298N  
- 2x Motores con reductora N20  
- Sensor ultrasónico HC-SR04  
- Powerbank  
- Petaca de pilas 4 AA

---

## Instalación

```bash
git clone https://github.com/1669321/RoadRunner.git
cd RoadRunner
pip install -r requirements.txt
```

---

## Ejecución

```bash
python main.py
```

> 💡 Asegúrate de tener conectada la cámara y los sensores antes de ejecutar el código.

---

## Estructura del proyecto

```
RoadRunner/
├── main.py                  # Script principal
├── car.py                   # Lógica del coche
├── lane_detector.py         # Detección de carril
├── overlay.py               # Visualización de datos
├── priorities.py            # Gestión de eventos
├── tf_test.py               # Prueba de señales (imagen)
├── tf_test_video.py         # Prueba de señales (vídeo)
├── test_line_detector.py    # Test de carril
├── utils_processing.py      # Utilidades de imagen
├── lane_detector/           # Módulo de carril
├── models/                  # Modelos entrenados
├── ims/                     # Imágenes de prueba
├── videos/                  # Vídeos de ejemplo
├── events.yaml              # Configuración de eventos
├── detectors.yaml           # Configuración de detectores
├── requirements.txt         # Dependencias
└── README.md
```

---

## Ejemplos visuales

| Detección de carril | Reconocimiento de señal |
|---------------------|--------------------------|
| ![lane](docs/img/lane.png) | ![sign](docs/img/sign.png) |

---

## Estado del desarrollo

- [x] Seguimiento de carril funcional  
- [x] Detección de obstáculos básica  
- [x] Reconocimiento de señales de tráfico  

---

## Cómo contribuir

¡Las contribuciones son bienvenidas! Puedes abrir un issue o enviar un pull request. Asegúrate de seguir buenas prácticas de codificación y documentar tus cambios.

---

## Licencia

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## Autores

- Roger González  
- Oriol Alarcón  
- Pau Díaz  
- Nil Caballero
