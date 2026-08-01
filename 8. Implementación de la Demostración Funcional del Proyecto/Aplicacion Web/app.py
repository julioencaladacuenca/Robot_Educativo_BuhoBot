from flask import Flask, render_template, Response, jsonify, request
from picamera2 import Picamera2
from ultralytics import YOLO
from vosk import Model

import cv2
import json
import os
import random
import threading
import time
import uuid

from datetime import datetime
from pathlib import Path

import robot_steam_v6 as motor


# ==========================================================
# BÚHOBOT WEB
#
# Adaptación web sincronizada de robot_steam_v6.py.
#
# Flujo visual:
# 1. Inicio: aparece BúhoBot.
# 2. Al pulsar Iniciar: aparece la cámara y YOLO detecta.
# 3. Al confirmar: se oculta la cámara y aparece la tarjeta.
# 4. BúhoBot presenta la microhistoria.
# 5. Realiza las actividades y muestra el progreso.
# 6. Muestra el puntaje final.
# 7. El botón "Nueva tarjeta" reactiva cámara + YOLO.
# ==========================================================


app = Flask(__name__)

VERSION_INTERFAZ = "20260730-final-reiniciar-estadisticas-1"


@app.after_request
def desactivar_cache(respuesta):
    """Evita que Chromium muestre archivos de una versión anterior."""
    respuesta.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    respuesta.headers["Pragma"] = "no-cache"
    respuesta.headers["Expires"] = "0"
    respuesta.headers["X-BuhoBot-Version"] = VERSION_INTERFAZ
    return respuesta

CARPETA_PROYECTO = Path(__file__).resolve().parent
ARCHIVO_ESTADISTICAS = (
    CARPETA_PROYECTO
    / "estadisticas_comprension.json"
)


# =========================
# CONFIGURACIÓN
# =========================

FOTOGRAMAS_ESTABLES = 10
FOTOGRAMAS_SIN_TARJETA = 10
TIEMPO_REACTIVACION = 2.0

CONFIANZA_DETECCION = 0.50
CONFIANZA_PROMEDIO_MINIMA = 0.56

AREA_MINIMA_RELATIVA = 0.08
AREA_MAXIMA_RELATIVA = 0.82
MARGEN_BORDE = 8

PAUSA_TARJETA_DETECTADA = 2.5
PAUSA_BUHOBOT = 2.0


# =========================
# VARIABLES GENERALES
# =========================

picam2 = None

actividad_activa = False
robot_ocupado = False
detener_solicitado = False
cantidad_preguntas = 1

vista_actual = "inicio"

clase_candidata = None
contador_estabilidad = 0
confianzas_candidata = []

tarjeta_bloqueada = None
contador_sin_tarjeta = 0
ultima_interaccion = 0.0

ultimo_frame = None

bloqueo_estado = threading.Lock()
bloqueo_frame = threading.Lock()
bloqueo_voz = threading.Lock()
bloqueo_bienvenida = threading.Lock()
bloqueo_estadisticas = threading.Lock()
bienvenida_reproducida = False


estado_web = {
    "vista_actual": "inicio",
    "estado": "BúhoBot está listo",
    "detalle_estado": (
        "Selecciona la cantidad de preguntas "
        "y presiona Iniciar actividad."
    ),
    "tarjeta": "Ninguna",
    "confianza": None,
    "pregunta_actual": 0,
    "total_preguntas": 1,
    "tipo_actividad": "",
    "pregunta": "",
    "respuesta": "",
    "resultado": "Pendiente",
    "correctas": 0,
    "incorrectas": 0,
    "porcentaje": 0.0,
    "puntaje_texto": "Pendiente",
    "progreso": 0,
    "procesando": False,
    "titulo_central": "¡Hola! Soy BúhoBot",
    "mensaje_central": (
        "Aprenderemos juntos mediante tarjetas, "
        "historias y actividades con tu voz."
    ),
    "historial_actividades": [],
    "medallas": 0,
    "medallas_texto": "",
    "reconocimiento_texto": "",
}


# =========================
# ESTADO WEB
# =========================

def actualizar_estado(**datos):
    global vista_actual

    if "vista_actual" in datos:
        vista_actual = datos["vista_actual"]

    with bloqueo_estado:
        estado_web.update(datos)


def hablar_seguro(texto):
    """
    Reproduce un mensaje sin superponerlo con otra voz.
    """
    with bloqueo_voz:
        motor.hablar(texto)


def bienvenida_inicial():
    """
    Mensaje que se reproduce cuando el navegador abre la página.
    """
    hablar_seguro(
        "¡Hola! Soy BúhoBot, tu robot educativo. "
        "Aprenderemos juntos mediante tarjetas, historias "
        "y actividades con tu voz. "
        "Selecciona la cantidad de preguntas "
        "y presiona Iniciar actividad."
    )


def calcular_progreso_pregunta(indice, total, etapa):
    if total <= 0:
        return 0

    factores = {
        "hablando": 0.25,
        "escuchando": 0.50,
        "procesando": 0.68,
        "evaluando": 0.82,
        "terminada": 1.00,
    }

    factor = factores.get(etapa, 0.0)
    base = (indice - 1) / total
    avance = factor / total

    return min(99, round((base + avance) * 100))




# =========================
# ESTADÍSTICAS PERSISTENTES
# =========================

def estructura_estadisticas_vacia():
    return {
        "version": 1,
        "sesiones": [],
    }


def leer_estadisticas():
    """
    Lee el archivo JSON de estadísticas.
    Si no existe o está dañado, devuelve una estructura vacía.
    """

    with bloqueo_estadisticas:

        if not ARCHIVO_ESTADISTICAS.exists():
            return estructura_estadisticas_vacia()

        try:
            with ARCHIVO_ESTADISTICAS.open(
                "r",
                encoding="utf-8",
            ) as archivo:
                datos = json.load(archivo)

            if not isinstance(
                datos.get("sesiones"),
                list,
            ):
                raise ValueError(
                    "El archivo no contiene una lista de sesiones."
                )

            return datos

        except (
            json.JSONDecodeError,
            OSError,
            ValueError,
        ) as error:

            print(
                "No se pudieron leer las estadísticas:",
                error,
            )

            return estructura_estadisticas_vacia()


def guardar_sesion_estadistica(
    tarjeta,
    total_preguntas,
    correctas,
    incorrectas,
    porcentaje,
    actividades,
):
    """
    Guarda una sesión anónima de interacción.
    Se usa escritura atómica para reducir el riesgo
    de corromper el archivo si el programa se interrumpe.
    """

    sesion = {
        "id": str(uuid.uuid4()),
        "fecha": datetime.now().isoformat(
            timespec="seconds"
        ),
        "tarjeta": str(tarjeta),
        "total_preguntas": int(
            total_preguntas
        ),
        "correctas": int(correctas),
        "incorrectas": int(incorrectas),
        "porcentaje": float(porcentaje),
        "actividades": list(actividades),
    }

    with bloqueo_estadisticas:

        if ARCHIVO_ESTADISTICAS.exists():
            try:
                with ARCHIVO_ESTADISTICAS.open(
                    "r",
                    encoding="utf-8",
                ) as archivo:
                    datos = json.load(archivo)
            except (
                json.JSONDecodeError,
                OSError,
            ):
                datos = estructura_estadisticas_vacia()
        else:
            datos = estructura_estadisticas_vacia()

        sesiones = datos.setdefault(
            "sesiones",
            [],
        )

        sesiones.append(sesion)

        archivo_temporal = (
            ARCHIVO_ESTADISTICAS
            .with_suffix(".json.tmp")
        )

        with archivo_temporal.open(
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=2,
            )

        os.replace(
            archivo_temporal,
            ARCHIVO_ESTADISTICAS,
        )

    return sesion


def reiniciar_estadisticas():
    """Borra las estadísticas acumuladas y conserva un JSON válido."""

    datos_vacios = estructura_estadisticas_vacia()

    with bloqueo_estadisticas:
        archivo_temporal = (
            ARCHIVO_ESTADISTICAS
            .with_suffix(".json.tmp")
        )

        with archivo_temporal.open(
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                datos_vacios,
                archivo,
                ensure_ascii=False,
                indent=2,
            )

        os.replace(
            archivo_temporal,
            ARCHIVO_ESTADISTICAS,
        )

    return datos_vacios



def resumir_estadisticas(datos):
    sesiones = datos.get(
        "sesiones",
        [],
    )

    total_sesiones = len(sesiones)

    total_preguntas = sum(
        int(sesion.get(
            "total_preguntas",
            0,
        ))
        for sesion in sesiones
    )

    total_correctas = sum(
        int(sesion.get(
            "correctas",
            0,
        ))
        for sesion in sesiones
    )

    total_incorrectas = sum(
        int(sesion.get(
            "incorrectas",
            0,
        ))
        for sesion in sesiones
    )

    porcentaje_global = (
        round(
            total_correctas
            / total_preguntas
            * 100,
            1,
        )
        if total_preguntas > 0
        else 0.0
    )

    por_tarjeta = {}

    for sesion in sesiones:

        tarjeta = str(
            sesion.get(
                "tarjeta",
                "Sin identificar",
            )
        )

        resumen_tarjeta = por_tarjeta.setdefault(
            tarjeta,
            {
                "tarjeta": tarjeta,
                "sesiones": 0,
                "preguntas": 0,
                "correctas": 0,
                "incorrectas": 0,
                "porcentaje": 0.0,
            },
        )

        resumen_tarjeta["sesiones"] += 1
        resumen_tarjeta["preguntas"] += int(
            sesion.get(
                "total_preguntas",
                0,
            )
        )
        resumen_tarjeta["correctas"] += int(
            sesion.get(
                "correctas",
                0,
            )
        )
        resumen_tarjeta["incorrectas"] += int(
            sesion.get(
                "incorrectas",
                0,
            )
        )

    for resumen_tarjeta in por_tarjeta.values():

        preguntas = resumen_tarjeta[
            "preguntas"
        ]

        resumen_tarjeta["porcentaje"] = (
            round(
                resumen_tarjeta["correctas"]
                / preguntas
                * 100,
                1,
            )
            if preguntas > 0
            else 0.0
        )

    return {
        "total_sesiones": total_sesiones,
        "total_preguntas": total_preguntas,
        "correctas": total_correctas,
        "incorrectas": total_incorrectas,
        "porcentaje_global": porcentaje_global,
        "por_tarjeta": sorted(
            por_tarjeta.values(),
            key=lambda elemento:
                elemento["tarjeta"],
        ),
    }


# =========================
# NOMBRES DE ACTIVIDADES
# =========================

def nombre_oral_actividad(tipo_actividad):
    nombres = {
        "adivinanza": "una adivinanza",
        "verdadero_falso": "una pregunta de verdadero o falso",
        "respuesta_oral": "una pregunta de respuesta oral",
        "opcion_multiple": "una pregunta de opción múltiple",
    }

    return nombres.get(tipo_actividad, "una actividad")


def nombre_visible_actividad(tipo_actividad):
    nombres = {
        "adivinanza": "Adivinanza",
        "verdadero_falso": "Verdadero o falso",
        "respuesta_oral": "Respuesta oral",
        "opcion_multiple": "Opción múltiple",
    }

    return nombres.get(tipo_actividad, "Actividad")


# =========================
# DETECCIÓN VALIDADA
# =========================

def obtener_deteccion_valida(frame):
    resultados = motor.modelo.predict(
        source=frame,
        conf=0.35,
        iou=0.45,
        max_det=5,
        verbose=False,
    )

    resultado = resultados[0]

    if len(resultado.boxes) == 0:
        return None

    alto_frame, ancho_frame = frame.shape[:2]
    area_frame = alto_frame * ancho_frame

    detecciones_validas = []

    for caja in resultado.boxes:
        clase_id = int(caja.cls[0])
        confianza = float(caja.conf[0])

        if confianza < CONFIANZA_DETECCION:
            continue

        nombre_clase = motor.modelo.names[clase_id]
        x1, y1, x2, y2 = map(int, caja.xyxy[0])

        ancho_caja = max(0, x2 - x1)
        alto_caja = max(0, y2 - y1)
        area_caja = ancho_caja * alto_caja
        proporcion_area = area_caja / area_frame

        if proporcion_area < AREA_MINIMA_RELATIVA:
            continue

        if proporcion_area > AREA_MAXIMA_RELATIVA:
            continue

        toca_izquierda = x1 <= MARGEN_BORDE
        toca_derecha = x2 >= ancho_frame - MARGEN_BORDE
        toca_arriba = y1 <= MARGEN_BORDE
        toca_abajo = y2 >= alto_frame - MARGEN_BORDE

        if (
            (toca_izquierda and toca_derecha)
            or (toca_arriba and toca_abajo)
        ):
            continue

        detecciones_validas.append(
            {
                "clase": nombre_clase,
                "confianza": confianza,
                "coordenadas": (x1, y1, x2, y2),
                "area_relativa": proporcion_area,
            }
        )

    if not detecciones_validas:
        return None

    return max(
        detecciones_validas,
        key=lambda deteccion: deteccion["confianza"],
    )


def dibujar_deteccion(frame, deteccion):
    frame_anotado = frame.copy()

    if deteccion is None:
        return frame_anotado

    x1, y1, x2, y2 = deteccion["coordenadas"]

    texto = (
        f'{deteccion["clase"]} '
        f'{deteccion["confianza"]:.2f}'
    )

    cv2.rectangle(
        frame_anotado,
        (x1, y1),
        (x2, y2),
        (255, 0, 0),
        3,
    )

    cv2.putText(
        frame_anotado,
        texto,
        (x1, max(y1 - 10, 25)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2,
    )

    return frame_anotado


# =========================
# MENSAJES DE VOZ
# =========================

def hablar_invitacion_tarjeta(es_nueva=False):
    """
    Primero reproduce toda la indicación oral con BúhoBot visible.
    Solo cuando termina el audio cambia a la cámara.
    Como YOLO depende de vista_actual == "camara",
    la detección comienza exactamente en ese momento.
    """
    if es_nueva:
        mensaje = (
            "Muy bien. Ahora coloca una nueva tarjeta frente a mí. "
            "Mantenla quieta, completa y sin reflejos "
            "hasta que pueda reconocerla."
        )
        estado_busqueda = "Buscando una nueva tarjeta"
        titulo_busqueda = "Muéstrame otra tarjeta"
    else:
        mensaje = (
            "Muy bien. La actividad ha comenzado. "
            "Ahora coloca una tarjeta frente a mí. "
            "Mantenla quieta, completa y sin reflejos "
            "hasta que pueda reconocerla."
        )
        estado_busqueda = "Buscando una tarjeta"
        titulo_busqueda = "Muéstrame una tarjeta"

    # Mientras se reproduce este audio, vista_actual continúa
    # siendo "indicacion", por lo que YOLO permanece desactivado.
    hablar_seguro(mensaje)

    # Si el usuario detuvo la actividad durante la indicación,
    # no se abre la cámara ni se activa YOLO.
    if not actividad_activa or detener_solicitado:
        return

    # Cámara visible y YOLO activo desde el mismo cambio de estado.
    actualizar_estado(
        vista_actual="camara",
        estado=estado_busqueda,
        detalle_estado=(
            "Colócala completa frente a BúhoBot "
            "y mantenla quieta."
        ),
        titulo_central=titulo_busqueda,
        mensaje_central=(
            "Mantén la tarjeta completa y sin reflejos."
        ),
        tarjeta="Ninguna",
        confianza=None,
        progreso=0,
        procesando=True,
    )


# =========================
# INTERACCIÓN PEDAGÓGICA
# =========================

def interactuar_con_tarjeta_web(nombre_clase, numero_preguntas):
    global robot_ocupado
    global detener_solicitado

    robot_ocupado = True
    detener_solicitado = False

    try:
        clave = motor.normalizar(nombre_clase)
        datos = motor.base_conocimiento.get(clave)

        if datos is None:
            actualizar_estado(
                vista_actual="buho",
                estado="No se encontró información",
                detalle_estado=(
                    "La tarjeta no existe en la base de conocimientos."
                ),
                titulo_central="No encontré esta tarjeta",
                mensaje_central=(
                    "Prueba con otra tarjeta disponible."
                ),
                procesando=False,
            )

            hablar_seguro(
                f"Reconocí {nombre_clase}, "
                "pero no encuentro su información "
                "en la base de conocimientos."
            )
            return

        nombre = datos.get("nombre", nombre_clase)
        descripcion = datos.get("descripcion", "")
        microhistoria = " ".join(
            datos.get("microhistoria", [])
        )

        actividades = list(
            datos.get("actividades", {}).items()
        )

        if not actividades:
            hablar_seguro(
                f"La tarjeta {nombre} no tiene actividades."
            )
            return

        try:
            numero_preguntas = int(numero_preguntas)
        except (TypeError, ValueError):
            numero_preguntas = 1

        numero_preguntas = max(
            1,
            min(numero_preguntas, len(actividades)),
        )

        actividades_seleccionadas = random.sample(
            actividades,
            numero_preguntas,
        )

        # Pantalla de tarjeta confirmada.
        actualizar_estado(
            vista_actual="tarjeta",
            estado="Tarjeta confirmada",
            detalle_estado="BúhoBot está preparando la actividad.",
            tarjeta=nombre,
            titulo_central="¡Tarjeta detectada!",
            mensaje_central=nombre.upper(),
            resultado="Iniciando actividad",
            progreso=8,
            procesando=True,
        )

        time.sleep(PAUSA_TARJETA_DETECTADA)

        # Aparece BúhoBot mientras presenta la historia.
        actualizar_estado(
            vista_actual="buho",
            estado="BúhoBot presenta la historia",
            detalle_estado="Escucha con atención la microhistoria.",
            titulo_central=f"Conozcamos: {nombre}",
            mensaje_central=(
                "Escucha la historia y prepárate "
                "para responder con tu voz."
            ),
            pregunta_actual=0,
            total_preguntas=numero_preguntas,
            tipo_actividad="",
            pregunta="",
            respuesta="",
            resultado="Presentación",
            correctas=0,
            incorrectas=0,
            porcentaje=0.0,
            puntaje_texto="Pendiente",
            historial_actividades=[],
            progreso=10,
            procesando=True,
        )

        introduccion = (
            f"He reconocido la tarjeta {nombre}. "
            f"{descripcion} "
            f"Escucha esta pequeña historia. "
            f"{microhistoria}"
        )

        hablar_seguro(introduccion)

        actualizar_estado(
            vista_actual="buho",
            estado="Preparando actividades lúdicas",
            detalle_estado=(
                "BúhoBot está preparando la primera actividad."
            ),
            titulo_central="¡Ahora tú participas!",
            mensaje_central=(
                "Escucha cada actividad y responde con tu voz."
            ),
            progreso=15,
            procesando=True,
        )

        time.sleep(PAUSA_BUHOBOT)

        hablar_seguro(
            "Ahora comenzaremos con algunas actividades lúdicas "
            "para comprobar cuánto comprendiste. "
            "Escucha con atención y responde con tu voz."
        )

        correctas = 0
        incorrectas = 0
        historial_actividades = []

        for indice, (
            tipo_actividad,
            actividad_original,
        ) in enumerate(
            actividades_seleccionadas,
            start=1,
        ):
            if detener_solicitado:
                break

            actividad = motor.preparar_actividad(
                actividad_original
            )

            tipo_hablado = nombre_oral_actividad(
                tipo_actividad
            )

            tipo_visible = nombre_visible_actividad(
                tipo_actividad
            )

            anuncio_pregunta = (
                f"Pregunta {indice} de {numero_preguntas}. "
                f"Ahora realizaremos {tipo_hablado}. "
                f"{actividad['pregunta']}"
            )

            actualizar_estado(
                vista_actual="actividad",
                estado=f"Pregunta {indice} de {numero_preguntas}",
                detalle_estado="BúhoBot está leyendo la actividad.",
                titulo_central=f"Pregunta {indice} de {numero_preguntas}",
                mensaje_central=tipo_visible,
                pregunta_actual=indice,
                total_preguntas=numero_preguntas,
                tipo_actividad=tipo_visible,
                pregunta=actividad["pregunta"],
                respuesta="",
                resultado="Hablando",
                correctas=correctas,
                incorrectas=incorrectas,
                progreso=calcular_progreso_pregunta(
                    indice,
                    numero_preguntas,
                    "hablando",
                ),
                procesando=True,
            )

            hablar_seguro(anuncio_pregunta)

            actualizar_estado(
                vista_actual="actividad",
                estado="Escuchando al estudiante",
                detalle_estado=(
                    "El micrófono está activo. "
                    "Ahora puedes responder."
                ),
                titulo_central="Te escucho",
                mensaje_central="Responde con tu voz.",
                resultado="Escuchando",
                progreso=calcular_progreso_pregunta(
                    indice,
                    numero_preguntas,
                    "escuchando",
                ),
                procesando=True,
            )

            respuesta_estudiante = motor.escuchar_respuesta(
                actividad["respuestas_validas"]
            )

            actualizar_estado(
                vista_actual="actividad",
                estado="Procesando respuesta",
                detalle_estado=(
                    "BúhoBot está interpretando tu respuesta."
                ),
                titulo_central="Estoy pensando…",
                mensaje_central="Procesando tu respuesta.",
                respuesta=respuesta_estudiante,
                resultado="Procesando",
                progreso=calcular_progreso_pregunta(
                    indice,
                    numero_preguntas,
                    "procesando",
                ),
                procesando=True,
            )

            es_correcta = motor.respuesta_es_correcta(
                respuesta_estudiante,
                actividad["respuestas_validas"],
            )

            actualizar_estado(
                vista_actual="actividad",
                estado="Evaluando respuesta",
                detalle_estado=(
                    "BúhoBot está comprobando la respuesta."
                ),
                titulo_central="Comprobando…",
                mensaje_central="Un momento, por favor.",
                progreso=calcular_progreso_pregunta(
                    indice,
                    numero_preguntas,
                    "evaluando",
                ),
                procesando=True,
            )

            if es_correcta:
                correctas += 1
                resultado = "Correcta"

                # La imagen buo_feliz.png ya contiene el mensaje visual.
                # La voz utiliza una frase breve y natural.
                retroalimentacion_visible = (
                    "¡Muy bien! Esa respuesta es correcta. "
                    "¡Vamos por la siguiente pregunta!"
                )
                retroalimentacion_oral = (
                    "¡Excelente! Lo hiciste muy bien. "
                    "Continuemos con la siguiente actividad."
                )
            else:
                incorrectas += 1
                resultado = "Incorrecta"

                # La imagen buo_explicando.png muestra un mensaje
                # positivo. La voz reproduce la explicación dinámica
                # guardada en la base de conocimientos.
                retroalimentacion_visible = (
                    "¡Gracias por intentarlo! "
                    "Escuchemos la respuesta correcta "
                    "para seguir aprendiendo."
                )
                retroalimentacion_oral = (
                    actividad["retroalimentacion_incorrecta"]
                )

            realizadas = correctas + incorrectas
            porcentaje = round(
                correctas / realizadas * 100,
                1,
            )

            registro_actividad = {
                "numero": indice,
                "tipo": tipo_visible,
                "pregunta": actividad["pregunta"],
                # Se guarda exactamente el texto devuelto por Vosk.
                # Si Vosk no produjo texto, se conserva una cadena vacía.
                "respuesta_reconocida":
                    respuesta_estudiante,
                "resultado": resultado,
                "retroalimentacion": retroalimentacion_oral,
            }

            historial_actividades.append(
                registro_actividad
            )

            actualizar_estado(
                vista_actual="actividad",
                estado=f"Pregunta {indice} finalizada",
                detalle_estado=(
                    "BúhoBot está dando la retroalimentación."
                ),
                titulo_central=(
                    "¡Respuesta correcta!"
                    if es_correcta
                    else "Sigamos aprendiendo"
                ),
                mensaje_central=retroalimentacion_visible,
                respuesta=respuesta_estudiante,
                resultado=resultado,
                correctas=correctas,
                incorrectas=incorrectas,
                porcentaje=porcentaje,
                historial_actividades=list(
                    historial_actividades
                ),
                progreso=calcular_progreso_pregunta(
                    indice,
                    numero_preguntas,
                    "terminada",
                ),
                procesando=True,
            )

            hablar_seguro(retroalimentacion_oral)

        realizadas = correctas + incorrectas

        porcentaje = (
            round(correctas / realizadas * 100, 1)
            if realizadas > 0
            else 0.0
        )

        if detener_solicitado:
            mensaje_final = "La actividad fue detenida."
            estado_final = "Actividad detenida"
            titulo_resultado = "Actividad detenida"
            mensaje_resultado = (
                "Puedes iniciar nuevamente cuando estés listo."
            )
            reconocimiento_texto = ""
            medallas = 0

        elif correctas == 0:
            # Nunca se presenta al niño como perdedor ni se menciona
            # que obtuvo cero. Recibe una insignia de Explorador.
            estado_final = "Aventura completada"
            titulo_resultado = "¡Aventura completada!"
            reconocimiento_texto = "⭐ Explorador de BúhoBot"
            mensaje_resultado = (
                "Hoy eres un Explorador de BúhoBot. "
                "¡Gracias por aprender conmigo!"
            )
            mensaje_final = (
                "¡Aventura completada! "
                "Hoy eres un Explorador de BúhoBot. "
                "Gracias por aprender conmigo. "
                "La próxima aventura te espera."
            )
            medallas = 0

        elif correctas == 1:
            estado_final = "Actividad finalizada"
            titulo_resultado = "¡Conseguiste una medalla!"
            reconocimiento_texto = "🏅 1 medalla"
            mensaje_resultado = (
                "¡Muy bien! Has conseguido tu primera medalla."
            )
            mensaje_final = (
                "¡Muy bien! Has conseguido tu primera medalla. "
                "Sigue aprendiendo con BúhoBot."
            )
            medallas = 1

        elif correctas == 2:
            estado_final = "Actividad finalizada"
            titulo_resultado = "¡Conseguiste dos medallas!"
            reconocimiento_texto = "🏅🏅 2 medallas"
            mensaje_resultado = (
                "¡Muy bien! Has conseguido dos medallas."
            )
            mensaje_final = (
                "¡Muy bien! Has conseguido dos medallas. "
                "Sigue aprendiendo con BúhoBot."
            )
            medallas = 2

        elif correctas == 3:
            estado_final = "Actividad finalizada"
            titulo_resultado = "¡Conseguiste tres medallas!"
            reconocimiento_texto = "🏅🏅🏅 3 medallas"
            mensaje_resultado = (
                "¡Fantástico! Has conseguido tres medallas."
            )
            mensaje_final = (
                "¡Fantástico! Has conseguido tres medallas. "
                "Sigue así, vas excelente."
            )
            medallas = 3

        else:
            estado_final = "Actividad finalizada"
            titulo_resultado = "¡Conseguiste cuatro medallas!"
            reconocimiento_texto = "🏅🏅🏅🏅 4 medallas"
            mensaje_resultado = (
                "¡Increíble! Has conseguido cuatro medallas."
            )
            mensaje_final = (
                "¡Increíble! Has conseguido cuatro medallas. "
                "Eres un campeón de la comprensión."
            )
            medallas = 4

        medallas_texto = reconocimiento_texto

        if (
            not detener_solicitado
            and realizadas > 0
        ):
            guardar_sesion_estadistica(
                tarjeta=nombre,
                total_preguntas=realizadas,
                correctas=correctas,
                incorrectas=incorrectas,
                porcentaje=porcentaje,
                actividades=historial_actividades,
            )

        actualizar_estado(
            vista_actual="resultado",
            estado="Finalizando actividad",
            detalle_estado="BúhoBot está preparando tu puntaje.",
            titulo_central="Calculando tu puntaje…",
            mensaje_central="Ya casi terminamos.",
            resultado="Finalizando",
            historial_actividades=list(
                historial_actividades
            ),
            progreso=99,
            procesando=True,
        )

        hablar_seguro(mensaje_final)

        puntaje_texto = (
            f"{correctas} de {realizadas} respuestas correctas "
            f"({porcentaje} %)"
        )

        actualizar_estado(
            vista_actual="resultado",
            estado=estado_final,
            detalle_estado=(
                "Actividad completada. "
                "Revisa el detalle de las actividades al final de la página."
            ),
            titulo_central=titulo_resultado,
            mensaje_central=mensaje_resultado,
            resultado=estado_final,
            correctas=correctas,
            incorrectas=incorrectas,
            porcentaje=porcentaje,
            puntaje_texto=puntaje_texto,
            historial_actividades=list(
                historial_actividades
            ),
            medallas=medallas,
            medallas_texto=medallas_texto,
            reconocimiento_texto=reconocimiento_texto,
            progreso=100,
            procesando=False,
        )

    except Exception as error:
        print("Error durante la actividad:", error)

        actualizar_estado(
            vista_actual="buho",
            estado="Error durante la actividad",
            detalle_estado=str(error),
            titulo_central="Necesito ayuda",
            mensaje_central=(
                "Ocurrió un problema durante la actividad."
            ),
            resultado="Error",
            procesando=False,
        )

    finally:
        robot_ocupado = False


# =========================
# CÁMARA
# =========================

def iniciar_camara():
    global picam2

    picam2 = Picamera2()

    configuracion = (
        picam2.create_preview_configuration(
            main={
                "size": (640, 480),
                "format": "RGB888",
            }
        )
    )

    picam2.configure(configuracion)
    picam2.start()

    time.sleep(2)

    print("Cámara iniciada correctamente.")


def lanzar_interaccion(nombre_clase):
    hilo = threading.Thread(
        target=interactuar_con_tarjeta_web,
        args=(nombre_clase, cantidad_preguntas),
        daemon=True,
    )

    hilo.start()


def reiniciar_candidata():
    global clase_candidata
    global contador_estabilidad
    global confianzas_candidata

    clase_candidata = None
    contador_estabilidad = 0
    confianzas_candidata = []


# =========================
# BUCLE PRINCIPAL
# =========================

def bucle_robot():
    global ultimo_frame
    global clase_candidata
    global contador_estabilidad
    global confianzas_candidata
    global tarjeta_bloqueada
    global contador_sin_tarjeta
    global ultima_interaccion

    while True:
        frame = picam2.capture_array()
        deteccion = None

        # Misma condición para mostrar cámara y ejecutar YOLO.
        debe_buscar_tarjeta = (
            actividad_activa
            and vista_actual == "camara"
            and not robot_ocupado
        )

        if debe_buscar_tarjeta:
            deteccion = obtener_deteccion_valida(frame)

        if debe_buscar_tarjeta:
            if tarjeta_bloqueada is not None:
                if deteccion is None:
                    contador_sin_tarjeta += 1
                elif (
                    motor.normalizar(deteccion["clase"])
                    != motor.normalizar(tarjeta_bloqueada)
                ):
                    contador_sin_tarjeta += 1
                else:
                    contador_sin_tarjeta = 0

                if (
                    contador_sin_tarjeta
                    >= FOTOGRAMAS_SIN_TARJETA
                ):
                    tarjeta_bloqueada = None
                    contador_sin_tarjeta = 0
                    reiniciar_candidata()

            elif deteccion is None:
                reiniciar_candidata()

                actualizar_estado(
                    vista_actual="camara",
                    estado="Buscando una tarjeta",
                    detalle_estado=(
                        "Colócala completa frente a BúhoBot "
                        "y mantenla quieta."
                    ),
                    titulo_central="Muéstrame una tarjeta",
                    mensaje_central=(
                        "Mantén la tarjeta completa y sin reflejos."
                    ),
                    tarjeta="Ninguna",
                    confianza=None,
                    progreso=0,
                    procesando=True,
                )

            else:
                clase_actual = motor.normalizar(
                    deteccion["clase"]
                )

                if clase_actual in motor.base_conocimiento:
                    if clase_actual == clase_candidata:
                        contador_estabilidad += 1
                        confianzas_candidata.append(
                            deteccion["confianza"]
                        )
                    else:
                        clase_candidata = clase_actual
                        contador_estabilidad = 1
                        confianzas_candidata = [
                            deteccion["confianza"]
                        ]

                    promedio_confianza = (
                        sum(confianzas_candidata)
                        / len(confianzas_candidata)
                    )

                    progreso_confirmacion = min(
                        8,
                        round(
                            contador_estabilidad
                            / FOTOGRAMAS_ESTABLES
                            * 8
                        ),
                    )

                    actualizar_estado(
                        vista_actual="camara",
                        estado=(
                            "Confirmando tarjeta "
                            f"{contador_estabilidad}/"
                            f"{FOTOGRAMAS_ESTABLES}"
                        ),
                        detalle_estado=(
                            "Mantén la tarjeta quieta "
                            "mientras BúhoBot la confirma."
                        ),
                        tarjeta=deteccion["clase"],
                        confianza=round(
                            promedio_confianza * 100,
                            1,
                        ),
                        progreso=progreso_confirmacion,
                        procesando=True,
                    )

                    if contador_estabilidad >= FOTOGRAMAS_ESTABLES:
                        if (
                            promedio_confianza
                            < CONFIANZA_PROMEDIO_MINIMA
                        ):
                            reiniciar_candidata()

                        elif (
                            time.time()
                            - ultima_interaccion
                            >= TIEMPO_REACTIVACION
                        ):
                            tarjeta_confirmada = clase_actual

                            print(
                                "Tarjeta confirmada:",
                                tarjeta_confirmada,
                            )

                            tarjeta_bloqueada = tarjeta_confirmada
                            ultima_interaccion = time.time()
                            contador_sin_tarjeta = 0
                            reiniciar_candidata()

                            # Cambiar la vista antes de lanzar la interacción
                            # detiene inmediatamente las nuevas detecciones.
                            actualizar_estado(
                                vista_actual="tarjeta",
                                estado="Tarjeta confirmada",
                                detalle_estado=(
                                    "BúhoBot está preparando la actividad."
                                ),
                                tarjeta=tarjeta_confirmada,
                                confianza=round(
                                    promedio_confianza * 100,
                                    1,
                                ),
                                titulo_central="¡Tarjeta detectada!",
                                mensaje_central=(
                                    tarjeta_confirmada.upper()
                                ),
                                resultado="Iniciando actividad",
                                progreso=8,
                                procesando=True,
                            )

                            lanzar_interaccion(
                                tarjeta_confirmada
                            )

        frame_anotado = dibujar_deteccion(
            frame,
            deteccion,
        )

        if vista_actual == "camara":
            with bloqueo_estado:
                estado_actual = estado_web["estado"]

            cv2.putText(
                frame_anotado,
                estado_actual,
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

        with bloqueo_frame:
            ultimo_frame = frame_anotado

        time.sleep(0.01)


# =========================
# TRANSMISIÓN DE VIDEO
# =========================

def generar_frames():
    while True:
        with bloqueo_frame:
            frame = (
                None
                if ultimo_frame is None
                else ultimo_frame.copy()
            )

        if frame is None:
            time.sleep(0.05)
            continue

        frame_bgr = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2BGR,
        )

        correcto, buffer = cv2.imencode(
            ".jpg",
            frame_bgr,
        )

        if not correcto:
            continue

        imagen = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + imagen
            + b"\r\n"
        )


# =========================
# RUTAS FLASK
# =========================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generar_frames(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


@app.route("/bienvenida", methods=["POST"])
def reproducir_bienvenida():
    """
    Reproduce la bienvenida únicamente la primera vez
    que se abre la página después de iniciar el servidor.
    """
    global bienvenida_reproducida

    with bloqueo_bienvenida:
        if bienvenida_reproducida:
            return jsonify({
                "ok": True,
                "reproducida": False,
                "mensaje": "La bienvenida ya fue reproducida.",
            })

        bienvenida_reproducida = True

    threading.Thread(
        target=bienvenida_inicial,
        daemon=True,
    ).start()

    return jsonify({
        "ok": True,
        "reproducida": True,
    })


@app.route("/iniciar", methods=["POST"])
def iniciar_actividad():
    global actividad_activa
    global cantidad_preguntas
    global detener_solicitado
    global tarjeta_bloqueada
    global contador_sin_tarjeta

    datos = request.get_json(silent=True) or {}

    try:
        cantidad = int(
            datos.get("cantidad_preguntas", 1)
        )
    except (TypeError, ValueError):
        cantidad = 1

    cantidad_preguntas = max(1, min(cantidad, 4))

    actividad_activa = True
    detener_solicitado = False
    tarjeta_bloqueada = None
    contador_sin_tarjeta = 0

    reiniciar_candidata()

    # Durante la indicación permanece BúhoBot visible.
    # YOLO todavía está desactivado porque la vista no es "camara".
    actualizar_estado(
        vista_actual="indicacion",
        estado="Escucha a BúhoBot",
        detalle_estado=(
            "BúhoBot está explicando cómo presentar la tarjeta."
        ),
        titulo_central="Prepárate para mostrar tu tarjeta",
        mensaje_central=(
            "Escucha la indicación. La cámara aparecerá "
            "cuando sea el momento de colocar la tarjeta."
        ),
        tarjeta="Ninguna",
        confianza=None,
        pregunta_actual=0,
        total_preguntas=cantidad_preguntas,
        tipo_actividad="",
        pregunta="",
        respuesta="",
        resultado="Preparando búsqueda",
        correctas=0,
        incorrectas=0,
        porcentaje=0.0,
        puntaje_texto="Pendiente",
        historial_actividades=[],
        medallas=0,
        medallas_texto="",
        reconocimiento_texto="",
        progreso=0,
        procesando=True,
    )

    threading.Thread(
        target=hablar_invitacion_tarjeta,
        args=(False,),
        daemon=True,
    ).start()

    return jsonify(
        {
            "ok": True,
            "vista_actual": "indicacion",
            "estado": "Escucha a BúhoBot",
            "cantidad_preguntas": cantidad_preguntas,
        }
    )


@app.route("/nueva_tarjeta", methods=["POST"])
def nueva_tarjeta():
    global actividad_activa
    global detener_solicitado
    global tarjeta_bloqueada
    global contador_sin_tarjeta

    actividad_activa = True
    detener_solicitado = False
    tarjeta_bloqueada = None
    contador_sin_tarjeta = 0

    reiniciar_candidata()

    actualizar_estado(
        vista_actual="indicacion",
        estado="Escucha a BúhoBot",
        detalle_estado=(
            "BúhoBot está explicando cómo presentar la nueva tarjeta."
        ),
        titulo_central="Preparemos una nueva actividad",
        mensaje_central=(
            "Escucha la indicación. La cámara aparecerá "
            "cuando sea el momento de colocar la nueva tarjeta."
        ),
        tarjeta="Ninguna",
        confianza=None,
        pregunta_actual=0,
        tipo_actividad="",
        pregunta="",
        respuesta="",
        resultado="Preparando búsqueda",
        correctas=0,
        incorrectas=0,
        porcentaje=0.0,
        puntaje_texto="Pendiente",
        historial_actividades=[],
        medallas=0,
        medallas_texto="",
        reconocimiento_texto="",
        progreso=0,
        procesando=True,
    )

    threading.Thread(
        target=hablar_invitacion_tarjeta,
        args=(True,),
        daemon=True,
    ).start()

    return jsonify({"ok": True})


@app.route("/detener", methods=["POST"])
def detener_actividad():
    global actividad_activa
    global detener_solicitado

    actividad_activa = False
    detener_solicitado = True

    reiniciar_candidata()

    actualizar_estado(
        vista_actual="inicio",
        estado="BúhoBot está listo",
        detalle_estado=(
            "Selecciona la cantidad de preguntas "
            "y presiona Iniciar actividad."
        ),
        titulo_central="¡Hola! Soy BúhoBot",
        mensaje_central=(
            "Aprenderemos juntos mediante tarjetas, "
            "historias y actividades con tu voz."
        ),
        tarjeta="Ninguna",
        confianza=None,
        resultado="Actividad detenida",
        historial_actividades=[],
        medallas=0,
        medallas_texto="",
        reconocimiento_texto="",
        progreso=0,
        procesando=False,
    )

    return jsonify(
        {
            "ok": True,
            "estado": "Sistema detenido",
        }
    )




@app.route("/estadisticas")
def obtener_estadisticas():
    datos = leer_estadisticas()
    resumen = resumir_estadisticas(
        datos
    )

    sesiones = sorted(
        datos.get(
            "sesiones",
            [],
        ),
        key=lambda sesion:
            sesion.get(
                "fecha",
                "",
            ),
        reverse=True,
    )

    return jsonify({
        "ok": True,
        "resumen": resumen,
        "sesiones": sesiones,
    })

@app.route("/estadisticas/reiniciar", methods=["POST"])
def borrar_estadisticas():
    reiniciar_estadisticas()

    return jsonify({
        "ok": True,
        "mensaje": "Las estadísticas acumuladas fueron reiniciadas.",
        "resumen": resumir_estadisticas(
            estructura_estadisticas_vacia()
        ),
        "sesiones": [],
    })


@app.route("/estado")
def obtener_estado():
    with bloqueo_estado:
        respuesta = dict(estado_web)

    respuesta.update(
        {
            "actividad_activa": actividad_activa,
            "cantidad_preguntas": cantidad_preguntas,
            "robot_ocupado": robot_ocupado,
            "tarjeta_detectada": respuesta.get(
                "tarjeta",
                "Ninguna",
            ),
        }
    )

    return jsonify(respuesta)


# =========================
# INICIO
# =========================

if __name__ == "__main__":
    motor.verificar_archivos()

    print("Cargando el modelo YOLO...")
    motor.modelo = YOLO(
        str(motor.MODELO_YOLO)
    )

    print("Cargando la base de conocimientos...")
    motor.base_conocimiento = (
        motor.cargar_base_conocimiento()
    )

    print("Cargando el modelo Vosk...")
    motor.modelo_vosk = Model(
        str(motor.MODELO_VOSK)
    )

    print("")
    print("Clases del modelo YOLO:")
    print(motor.modelo.names)

    print("")
    print("Clases de la base de conocimientos:")
    print(
        list(motor.base_conocimiento.keys())
    )

    iniciar_camara()

    hilo_robot = threading.Thread(
        target=bucle_robot,
        daemon=True,
    )
    hilo_robot.start()

    print("")
    print("======================================")
    print("ROBOT EDUCATIVO BÚHOBOT")
    print("======================================")
    print("Abre Chromium en:")
    print("http://localhost:5000")
    print("======================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
