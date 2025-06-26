# RoadRunner 🚗💨

**RoadRunner** es un proyecto de conducción autónoma que permite a un coche mantenerse dentro del carril, detectar obstáculos y reconocer señales de tráfico usando visión por computadora.

---

## Tabla de Contenidos

- [¿Qué es RoadRunner?](#qué-es-roadrunner)
- [Requisitos](#requisitos)
- [Cómo usar](#cómo-usar)
- [Características](#características)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Estado del desarrollo](#estado-del-desarrollo)
- [Autores](#autores)
- [Licencia](#licencia)

---

## ¿Qué es RoadRunner?

RoadRunner es un sistema diseñado para el control autónomo de un vehículo, que integra detección de carril, reconocimiento de señales de tráfico y detección de obstáculos mediante sensores y visión por computadora.

Este proyecto está pensado para implementarse en hardware embebido, como Raspberry Pi, con sensores y cámaras para la adquisición de datos en tiempo real.

---

## Requisitos

Para ejecutar el proyecto, se necesitan las siguientes librerías y software:

- Python 3.9 o superior
- OpenCV
- NumPy
- PyYAML
- PyTorch (para los modelos `.pt`)
- YOLO (para detección de objetos)
- Otros sensores y controladores (Raspberry Pi, sensor ultrasonido HC-SR04, controladora L298N)

---

## Cómo usar

1. Clonar el repositorio:

```bash
git clone https://github.com/1669321/RoadRunner.git
cd RoadRunner
