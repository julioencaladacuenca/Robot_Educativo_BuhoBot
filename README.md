# Robot Educativo BuhoBot

Sistema Inteligente basado en Inteligencia Artificial, Visión por Computadora e interacción por voz para apoyar la comprensión lectora en estudiantes de Primer Año de Educación General Básica.

**Proyecto de Maestría en Inteligencia Artificial**  
**Universidad Espíritu Santo (UEES)**

---

## Descripción

Robot Educativo BuhoBot es un sistema educativo inteligente desarrollado para integrar tecnologías de Inteligencia Artificial en el aula. El proyecto combina visión por computadora, reconocimiento de voz y síntesis de voz para ofrecer experiencias de aprendizaje interactivas, permitiendo que los estudiantes interactúen verbalmente con un robot educativo a partir del reconocimiento automático de cartas pedagógicas.

El sistema identifica el material didáctico mediante un modelo de detección de objetos basado en YOLOv8, consulta una base de conocimientos estructurada en formato JSON, formula preguntas al estudiante mediante síntesis de voz y evalúa automáticamente las respuestas utilizando reconocimiento de voz.

---

## Objetivo

Desarrollar un robot educativo basado en Inteligencia Artificial y Visión por Computadora que favorezca la comprensión lectora mediante la interacción por voz con estudiantes de Primer Año de Educación General Básica.

---

## Características principales

- Reconocimiento de cartas pedagógicas mediante Visión por Computadora.
- Detección automática utilizando YOLOv8.
- Síntesis de voz mediante Piper TTS.
- Reconocimiento de voz mediante Vosk.
- Base de conocimientos estructurada en formato JSON.
- Evaluación automática de respuestas.
- Retroalimentación inmediata al estudiante.
- Registro de resultados de la interacción.

---

## Arquitectura del sistema

> **Nota:** La imagen de la arquitectura será incorporada en futuras actualizaciones del repositorio.

---

## Tecnologías utilizadas

| Tecnología | Descripción |
|------------|-------------|
| Python | Lenguaje principal del proyecto |
| Flask | Gestión y orquestación de la aplicación |
| Raspberry Pi 5 | Plataforma de ejecución |
| YOLOv8 | Modelo de Visión por Computadora |
| OpenCV | Procesamiento de imágenes |
| Piper TTS | Síntesis de voz |
| Vosk | Reconocimiento de voz |
| JSON | Base de conocimientos |
| Git | Control de versiones |
| GitHub | Gestión del repositorio |

---

## Flujo general del sistema

1. Captura de la carta mediante una cámara USB.
2. Detección automática utilizando YOLOv8.
3. Consulta de la base de conocimientos.
4. Generación de la historia y preguntas mediante Piper TTS.
5. Interacción verbal con el estudiante.
6. Conversión de voz a texto mediante Vosk.
7. Evaluación de la respuesta.
8. Generación de retroalimentación.
9. Registro de resultados.

---

## Estructura del proyecto

```text
Robot_Educativo_BuhoBot/

├── src/                # Código fuente
├── modelos/            # Modelos de IA
├── conocimiento/       # Base de conocimientos
├── imagenes/           # Recursos gráficos
├── audios/             # Recursos de audio
├── docs/               # Documentación
├── resultados/         # Evidencias experimentales
├── README.md
├── requirements.txt
└── LICENSE
```

---

## Estado del proyecto

**En desarrollo.**

Actualmente se encuentra implementado el flujo principal del sistema, incluyendo el reconocimiento de cartas pedagógicas mediante Visión por Computadora, la interacción por voz y la evaluación automática de respuestas.

---

## Trabajos futuros

- Optimización del modelo de detección.
- Incorporación de nuevos escenarios educativos.
- Ampliación de la base de conocimientos.
- Evaluación experimental en instituciones educativas.
- Desarrollo de un panel de resultados para docentes.

---

## Autores

**Julio Encalada Cuenca**  
Docente de la Universidad Técnica de Machala (UTMACH)

**Sara Cruz Naranjo**  
Docente de la Universidad Técnica de Machala (UTMACH)

---

## Licencia

Este proyecto ha sido desarrollado con fines académicos, científicos y de investigación como parte de un proyecto de Maestría en Inteligencia Artificial.
