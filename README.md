<p align="center">
  <img src="assets/Logo_BuhoBot.png" width="220" alt="BúhoBot">
</p>

<h1 align="center">🤖 Robot Educativo Inteligente BúhoBot</h1>

<h3 align="center">
Proyecto Integrador de Inteligencia Artificial
</h3>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-success)
![Flask](https://img.shields.io/badge/Flask-Web_App-black)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5-red)
![Estado](https://img.shields.io/badge/Estado-Finalizado-brightgreen)

</p>

---

# 📖 Descripción del proyecto

**BúhoBot** es un robot educativo inteligente basado en **Visión por Computadora** e **Inteligencia Artificial**, diseñado para reconocer cartas pedagógicas e interactuar mediante voz con estudiantes de **Primer Año de Educación General Básica**, apoyando actividades orientadas al desarrollo de la comprensión lectora.

El sistema integra un modelo de detección de objetos basado en **YOLOv8**, una aplicación web desarrollada con **Flask**, una base de conocimientos en formato **JSON**, síntesis de voz mediante **Piper TTS** y reconocimiento automático del habla mediante **Vosk**, permitiendo una interacción educativa automatizada.

---

# 🎯 Objetivo del proyecto

**Desarrollar y validar un robot educativo basado en visión por computadora e inteligencia artificial para apoyar el desarrollo de la comprensión lectora en estudiantes de Primer Año de Educación General Básica, mediante el reconocimiento de cartas pedagógicas y la interacción por voz.**

---

# 🏗 Arquitectura del sistema

<p align="center">
<img src="1. Descripción General del Proyecto/Arquitectura_General.png" width="100%" alt="Arquitectura del sistema">
</p>

La aplicación está orquestada por **Flask**, que coordina la comunicación entre todos los módulos del sistema. El flujo inicia con la detección de la carta mediante **YOLOv8**, continúa con la consulta de la base de conocimientos en **JSON**, la generación del audio mediante **Piper TTS**, la captura de la respuesta del estudiante utilizando **Vosk**, la evaluación automática de la respuesta y la generación de la retroalimentación correspondiente.

---

# ⚙ Componentes tecnológicos del sistema

| Tecnología | Función |
|------------|---------|
| Python | Lenguaje principal del proyecto. |
| Flask | Framework web y orquestador de la aplicación. |
| YOLOv8 (Ultralytics) | Reconocimiento de cartas pedagógicas mediante visión por computadora. |
| OpenCV | Captura y procesamiento de imágenes. |
| Piper TTS | Conversión de texto a voz. |
| Vosk | Reconocimiento automático del habla. |
| JSON | Base de conocimientos del robot. |
| Roboflow | Construcción y exportación del dataset. |
| Raspberry Pi 5 | Plataforma de ejecución. |
| Cámara USB | Captura de las cartas pedagógicas. |
| Micrófono USB | Captura la respuesta del estudiante. |
| Parlante USB | Reproduce historias y retroalimentación. |
| HTML5, CSS3 y JavaScript | Desarrollo de la interfaz web. |

---

# 📊 Dataset utilizado

El modelo fue entrenado con un conjunto de datos propio compuesto por cinco clases:

- 🏥 Hospital
- 🏫 Escuela
- 🌳 Parque
- 🥖 Panadería
- 🛒 Supermercado

El dataset se encuentra organizado en formato **YOLOv8** dentro de:

📁 **`1. Descripción General del Proyecto/Dataset/`**

---

# 📂 Estructura del repositorio

| Sección | Contenido |
|---------|-----------|
| 📁 [1. Descripción General del Proyecto](./1.%20Descripción%20General%20del%20Proyecto/) | Arquitectura del sistema y dataset utilizado. |
| 📁 [2. Análisis Exploratorio de Datos (EDA)](./2.%20Análisis%20Exploratorio%20de%20Datos%20(EDA)/) | Exploración y análisis del conjunto de datos. |
| 📁 [3. Preparación y Procesamiento de Datos](./3.%20Preparación%20y%20Procesamiento%20de%20Datos/) | Limpieza, balanceo y Data Augmentation. |
| 📁 [4. Modelo Baseline](./4.%20Modelo%20Baseline/) | Modelo de referencia para benchmarking. |
| 📁 [5. Evaluación y Optimización del Modelo](./5.%20Evaluación%20y%20Optimización%20del%20Modelo/) | Entrenamiento y evaluación del modelo propuesto. |
| 📁 [6. Workshop Integral de Evaluación y Simulación](./6.%20Workshop%20Integral%20de%20Evaluación%20y%20Simulación/) | Simulación y pruebas de robustez. |
| 📁 [7. Optimización de Hiperparámetros y Evaluación Avanzada](./7.%20Optimización%20de%20Hiperparámetros%20y%20Evaluación%20Avanzada/) | Optimización avanzada del modelo. |
| 📁 [8. Implementación de la Demostración Funcional del Proyecto](./8.%20Implementación%20de%20la%20Demostración%20Funcional%20del%20Proyecto/) | Aplicación web y demostración funcional del sistema. |

---

# 🚀 Ejecución del proyecto

## 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/Proyecto_Integrador_IA.git
```

## 2. Acceder a la aplicación

```bash
cd "8. Implementación de la Demostración Funcional del Proyecto/Aplicacion_Web"
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

```bash
python app.py
```

## 5. Abrir en el navegador

```
http://localhost:5000
```

---

# 📁 Contenido de la implementación

La carpeta **8. Implementación de la Demostración Funcional del Proyecto** contiene:

- 📂 **Aplicacion_Web/**
  - `app.py`
  - `robot_steam_final.py`
  - `detector_frutas1.py`
  - `detector_frutas2.py`
  - `templates/`
  - `static/`
  - `requirements.txt`

- 📂 **Modelo/**
  - `best.pt`

- 📂 **Base_Conocimiento/**
  - `conocimiento.json`

- 📂 **Material_Didactico/**
  - Hospital
  - Escuela
  - Parque
  - Panadería
  - Supermercado

- 📄 **Presentacion_Proyecto.pdf**

---

# 👨‍💻 Autores

**Julio Encalada Cuenca**  
Docente – Universidad Técnica de Machala (UTMACH)

**Sara Cruz Naranjo**  
Docente – Universidad Técnica de Machala (UTMACH)

---

# 🏛 Instituciones

- Universidad Espíritu Santo (UEES)
- Universidad Técnica de Machala (UTMACH)

---

# 📄 Licencia

Repositorio desarrollado con fines académicos como parte del **Proyecto Integrador de la Maestría en Inteligencia Artificial**.
