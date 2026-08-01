<p align="center">
  <img src="./assets/LogoBuhoBot.png" width="180" alt="BúhoBot">
</p>

<h1 align="center">🤖 Robot Educativo Inteligente BúhoBot</h1>

<p align="center">
<b>Proyecto Integrador de Inteligencia Artificial</b>
</p>

<p align="center">

![](https://img.shields.io/badge/Python-3.11-blue)
![](https://img.shields.io/badge/YOLOv8-Ultralytics-success)
![](https://img.shields.io/badge/Flask-Web_App-lightgrey)
![](https://img.shields.io/badge/Raspberry%20Pi-5-red)
![](https://img.shields.io/badge/Estado-Finalizado-brightgreen)

</p>

---

# 📖 Descripción del proyecto

**BúhoBot** es un robot educativo inteligente basado en **Visión por Computadora** e **Inteligencia Artificial**, diseñado para reconocer cartas pedagógicas e interactuar mediante voz con estudiantes de **Primer Año de Educación General Básica**, apoyando actividades orientadas al desarrollo de la comprensión lectora.

El sistema integra un modelo de detección basado en **YOLOv8**, una aplicación web desarrollada con **Flask**, una base de conocimientos en formato **JSON**, síntesis de voz mediante **Piper TTS** y reconocimiento automático del habla mediante **Vosk**, permitiendo una interacción educativa automatizada.

---

# 🎯 Objetivo del proyecto

Desarrollar un robot educativo inteligente basado en visión por computadora e inteligencia artificial capaz de reconocer cartas pedagógicas e interactuar mediante voz con estudiantes de Primer Año de Educación General Básica para apoyar actividades de comprensión lectora.

---

# 🏗 Arquitectura general

<p align="center">

<img src="./1.%20Descripción%20General%20del%20Proyecto/Arquitectura_General.png" width="1000">

</p>

---

# 🛠 Tecnologías utilizadas

- Python 3.11
- YOLOv8 (Ultralytics)
- Flask
- Raspberry Pi 5
- OpenCV
- Piper TTS
- Vosk Speech Recognition
- JSON
- HTML5
- CSS3
- JavaScript

---

# 📂 Dataset

El conjunto de datos fue construido específicamente para este proyecto utilizando imágenes propias de cinco cartas pedagógicas correspondientes a distintos entornos cotidianos.

### Clases utilizadas

- 🏥 Hospital
- 🏫 Escuela
- 🌳 Parque
- 🥖 Panadería
- 🛒 Supermercado

El dataset se encuentra organizado en formato **YOLOv8**, incluyendo los conjuntos de entrenamiento, validación y prueba.

<p align="center">

<a href="./1.%20Descripción%20General%20del%20Proyecto/Dataset">

<img src="https://img.shields.io/badge/📂%20EXPLORAR%20DATASET-blue?style=for-the-badge">

</a>

</p>

---

# 🚀 Presentación de la demostración funcional

La memoria técnica resume la implementación, arquitectura y funcionamiento del Robot Educativo BúhoBot durante la demostración final del proyecto.

Incluye el flujo del sistema, los componentes desarrollados y las principales evidencias de funcionamiento.

<p align="center">

<a href="./8.%20Implementación%20de%20la%20Demostración%20Funcional%20del%20Proyecto/Presentacion%20Demo/Memoria_Demostracion_Funcional_BuhoBot.pdf">

<img src="https://img.shields.io/badge/📄%20ABRIR%20MEMORIA%20DE%20LA%20DEMOSTRACIÓN-red?style=for-the-badge">

</a>

</p>

---

# 📁 Organización del repositorio

```text
Robot_Educativo_BuhoBot
│
├── 📁 1. Descripción General del Proyecto
│   ├── Dataset
│   └── Arquitectura_General.png
│
├── 📁 2. Análisis Exploratorio de Datos (EDA)
│
├── 📁 3. Preparación y Procesamiento de Datos
│
├── 📁 4. Modelo Baseline
│
├── 📁 5. Evaluación y Optimización del Modelo
│
├── 📁 6. Workshop Integral de Evaluación y Simulación
│
├── 📁 7. Optimización de Hiperparámetros y Evaluación Avanzada
│
├── 📁 8. Implementación de la Demostración Funcional del Proyecto
│   ├── Aplicación Web
│   ├── Modelo
│   │     └── best.pt
│   ├── Base Conocimiento
│   │     └── conocimiento.json
│   ├── Material Didáctico
│   └── Presentación Demo
│
├── 📁 assets
│
└── README.md
```

---

# 📑 Contenido académico

| Nº | Sección | Descripción |
|:--:|---------|-------------|
| **1** | **Descripción General del Proyecto** | Presenta el contexto del proyecto, el problema de investigación, la arquitectura general del sistema y el conjunto de datos empleado para el entrenamiento del modelo de visión por computadora. |
| **2** | **Análisis Exploratorio de Datos (EDA)** | Contiene el análisis estadístico y visual del dataset, permitiendo conocer la distribución de las clases, la calidad de las imágenes y las características principales del conjunto de datos. |
| **3** | **Preparación y Procesamiento de Datos** | Describe el proceso de organización, etiquetado, validación y preparación del dataset antes del entrenamiento del modelo de inteligencia artificial. |
| **4** | **Modelo Baseline** | Documenta el entrenamiento del modelo base utilizado como referencia inicial para comparar posteriormente el impacto de las estrategias de optimización implementadas. |
| **5** | **Evaluación y Optimización del Modelo** | Presenta las métricas de desempeño, el análisis de resultados y las mejoras aplicadas para incrementar la precisión y robustez del sistema de detección. |
| **6** | **Workshop Integral de Evaluación y Simulación** | Reúne las actividades académicas relacionadas con la validación experimental, simulaciones y pruebas de robustez desarrolladas durante el proyecto integrador. |
| **7** | **Optimización de Hiperparámetros y Evaluación Avanzada** | Incluye los experimentos de ajuste de hiperparámetros, comparación entre configuraciones y análisis avanzado del comportamiento del modelo entrenado. |
| **8** | **Implementación de la Demostración Funcional del Proyecto** | Contiene la aplicación web desarrollada en Flask, el modelo entrenado, la base de conocimientos, el material didáctico y la memoria técnica utilizada durante la demostración funcional del robot. |

---

# 👨‍💻 Autores

### Julio Encalada Cuenca

Docente — Universidad Técnica de Machala (UTMACH)

### Sara Cruz Naranjo

Docente — Universidad Técnica de Machala (UTMACH)

---

# 🏛 Instituciones

- Universidad Técnica de Machala (UTMACH)
- Universidad Espíritu Santo (UEES)

---

<p align="center">

Proyecto desarrollado como parte del Proyecto Integrador de Titulación de la Maestría en Inteligencia Artificial.

© 2026

</p>
