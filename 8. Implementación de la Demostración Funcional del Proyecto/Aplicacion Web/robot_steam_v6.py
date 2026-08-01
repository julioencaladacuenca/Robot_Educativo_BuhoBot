from pathlib import Path
from picamera2 import Picamera2
from ultralytics import YOLO

import cv2
import subprocess
import time
import random
import json
import wave
import unicodedata

from vosk import Model, KaldiRecognizer


# ==========================================================
# ROBOT STEAM V6
# Detección automática de tarjetas + interacción oral
#
# Funcionamiento:
# 1. El estudiante acerca una tarjeta.
# 2. YOLO confirma que la detección sea estable.
# 3. El robot inicia automáticamente la actividad.
# 4. El robot espera que la tarjeta sea retirada.
# 5. Luego queda listo para reconocer una nueva tarjeta.
# ==========================================================


# =========================
# CONFIGURACIÓN
# =========================

CARPETA_PROYECTO = Path(__file__).resolve().parent

MODELO_YOLO = CARPETA_PROYECTO / "nuevobest.pt"
MODELO_PIPER = CARPETA_PROYECTO / "es_ES-davefx-medium.onnx"
MODELO_VOSK = CARPETA_PROYECTO / "vosk-model-small-es-0.42"
BASE_JSON = CARPETA_PROYECTO / "base_conocimiento2.json"

AUDIO_DEVICE = "hw:2,0"

# Confianza mínima para aceptar una detección
CONFIANZA_MINIMA = 0.45

# Parámetro para reducir detecciones superpuestas
IOU_MAXIMO = 0.45

# Duración de la grabación de la respuesta del estudiante
DURACION_GRABACION = 4

# Número de detecciones consecutivas necesarias
# para confirmar una tarjeta
FOTOGRAMAS_ESTABLES = 8

# Número de fotogramas sin detectar la misma tarjeta
# para considerar que fue retirada
FOTOGRAMAS_SIN_TARJETA = 8

# Tiempo mínimo entre dos interacciones
TIEMPO_REACTIVACION = 2.0


# =========================
# UTILIDADES
# =========================

def normalizar(texto):
    """
    Convierte el texto a minúsculas,
    elimina espacios exteriores y tildes.
    """

    texto = str(texto).lower().strip()

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def verificar_archivos():
    """
    Comprueba que todos los archivos necesarios
    existan antes de iniciar el robot.
    """

    requeridos = {
        "modelo YOLO": MODELO_YOLO,
        "modelo Piper": MODELO_PIPER,
        "modelo Vosk": MODELO_VOSK,
        "base de conocimientos": BASE_JSON,
    }

    faltantes = [
        f"{nombre}: {ruta}"
        for nombre, ruta in requeridos.items()
        if not ruta.exists()
    ]

    if faltantes:
        detalle = "\n".join(
            f"- {elemento}"
            for elemento in faltantes
        )

        raise FileNotFoundError(
            "Faltan archivos necesarios para iniciar el robot:\n"
            + detalle
        )


def cargar_base_conocimiento():
    """
    Carga la información pedagógica
    desde base_conocimiento2.json.
    """

    with BASE_JSON.open(
        "r",
        encoding="utf-8",
    ) as archivo:

        base = json.load(archivo)

    return {
        normalizar(clave): valor
        for clave, valor in base.items()
    }


# =========================
# VOZ DEL ROBOT
# =========================

def hablar(texto):
    """
    Convierte un texto en voz mediante Piper
    y lo reproduce por el dispositivo de audio.
    """

    texto = str(texto).strip()

    if not texto:
        return

    print(f"Robot: {texto}")

    audio_original = (
        CARPETA_PROYECTO
        / "respuesta_original.wav"
    )

    audio_salida = (
        CARPETA_PROYECTO
        / "respuesta.wav"
    )

    try:

        subprocess.run(
            [
                "piper",
                "--model",
                str(MODELO_PIPER),
                "--output_file",
                str(audio_original),
            ],
            input=texto,
            text=True,
            check=True,
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(audio_original),
                "-ar",
                "48000",
                "-ac",
                "2",
                str(audio_salida),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        subprocess.run(
            [
                "aplay",
                "-D",
                AUDIO_DEVICE,
                str(audio_salida),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    except FileNotFoundError as error:

        print(
            "No se encontró uno de los programas "
            f"necesarios para el audio: {error}"
        )

    except subprocess.CalledProcessError as error:

        print(
            "Ocurrió un error durante la generación "
            f"o reproducción de voz: {error}"
        )


# =========================
# ESCUCHA DEL ESTUDIANTE
# =========================

def grabar_audio():
    """
    Graba la respuesta oral del estudiante.
    """

    print(
        f"Escuchando durante "
        f"{DURACION_GRABACION} segundos..."
    )

    audio_original = (
        CARPETA_PROYECTO
        / "audio_original.wav"
    )

    subprocess.run(
        [
            "arecord",
            "-D",
            AUDIO_DEVICE,
            "-f",
            "S16_LE",
            "-r",
            "48000",
            "-c",
            "2",
            "-d",
            str(DURACION_GRABACION),
            str(audio_original),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def convertir_audio():
    """
    Convierte el audio grabado al formato
    requerido por Vosk.
    """

    audio_original = (
        CARPETA_PROYECTO
        / "audio_original.wav"
    )

    audio_vosk = (
        CARPETA_PROYECTO
        / "audio_vosk.wav"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_original),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(audio_vosk),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def reconocer_con_vosk(respuestas_validas):
    """
    Reconoce libremente lo pronunciado por el estudiante.

    No limita el reconocimiento únicamente a las respuestas esperadas,
    para que la página pueda mostrar y guardar el texto real reconocido
    por Vosk. La validación pedagógica se realiza después, comparando
    esta transcripción con las respuestas válidas.
    """

    print("Reconociendo respuesta...")

    audio_vosk = (
        CARPETA_PROYECTO
        / "audio_vosk.wav"
    )

    with wave.open(
        str(audio_vosk),
        "rb",
    ) as archivo_audio:

        reconocedor = KaldiRecognizer(
            modelo_vosk,
            archivo_audio.getframerate(),
        )

        partes = []

        while True:

            datos = archivo_audio.readframes(
                4000
            )

            if len(datos) == 0:
                break

            if reconocedor.AcceptWaveform(
                datos
            ):

                resultado = json.loads(
                    reconocedor.Result()
                )

                texto_parcial = resultado.get(
                    "text",
                    "",
                ).strip()

                if texto_parcial:
                    partes.append(
                        texto_parcial
                    )

        resultado_final = json.loads(
            reconocedor.FinalResult()
        )

        texto_final = resultado_final.get(
            "text",
            "",
        ).strip()

        if texto_final:
            partes.append(
                texto_final
            )

    # Se conserva la transcripción producida por Vosk.
    # La función respuesta_es_correcta() se encarga de normalizarla.
    texto_reconocido = " ".join(
        partes
    ).strip()

    if texto_reconocido:
        print(
            f"Estudiante dijo: "
            f"{texto_reconocido}"
        )
    else:
        print(
            "Estudiante dijo: "
            "(Vosk no produjo texto)"
        )

    return texto_reconocido


def escuchar_respuesta(
    respuestas_validas,
):
    """
    Ejecuta la grabación, conversión
    y reconocimiento de la respuesta.
    """

    try:

        grabar_audio()
        convertir_audio()

        return reconocer_con_vosk(
            respuestas_validas
        )

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        wave.Error,
    ) as error:

        print(
            "No se pudo procesar "
            f"la respuesta oral: {error}"
        )

        return ""


# =========================
# VALIDACIÓN DE RESPUESTAS
# =========================

def respuesta_es_correcta(
    texto_estudiante,
    respuestas_validas,
):
    """
    Compara la respuesta reconocida con
    las respuestas aceptadas en el JSON.
    """

    texto_estudiante = normalizar(
        texto_estudiante
    )

    if not texto_estudiante:
        return False

    for respuesta in respuestas_validas:

        respuesta_normalizada = normalizar(
            respuesta
        )

        if (
            texto_estudiante
            == respuesta_normalizada
        ):
            return True

        if (
            respuesta_normalizada
            in texto_estudiante
        ):
            return True

    return False


def preparar_actividad(actividad):
    """
    Convierte cualquier tipo de actividad
    del JSON a una estructura común.
    """

    tipo = actividad.get(
        "tipo",
        "",
    )

    # ---------------------------------
    # RESPUESTA CORTA O ABIERTA
    # ---------------------------------

    if tipo in {
        "respuesta_corta",
        "respuesta_abierta",
    }:

        pregunta = actividad[
            "pregunta"
        ]

        respuestas = list(
            actividad.get(
                "respuestas_aceptadas",
                [],
            )
        )

        if actividad.get(
            "respuesta_correcta"
        ):
            respuestas.append(
                actividad[
                    "respuesta_correcta"
                ]
            )

    # ---------------------------------
    # VERDADERO O FALSO
    # ---------------------------------

    elif tipo == "verdadero_falso":

        pregunta = (
            actividad["enunciado"]
            + " Responde verdadero o falso."
        )

        if actividad[
            "respuesta_correcta"
        ]:

            respuestas = [
                "verdadero",
                "es verdadero",
                "cierto",
                "si",
            ]

        else:

            respuestas = [
                "falso",
                "es falso",
                "no",
            ]

    # ---------------------------------
    # VERDADERO O FALSO MÚLTIPLE
    # ---------------------------------

    elif tipo == "verdadero_falso_multiple":

        enunciados = actividad.get(
            "enunciados",
            [],
        )

        if not enunciados:
            raise ValueError(
                "La actividad de verdadero "
                "o falso no contiene enunciados."
            )

        seleccionado = random.choice(
            enunciados
        )

        pregunta = (
            seleccionado["texto"]
            + " Responde verdadero o falso."
        )

        if seleccionado[
            "respuesta_correcta"
        ]:

            respuestas = [
                "verdadero",
                "es verdadero",
                "cierto",
                "si",
            ]

        else:

            respuestas = [
                "falso",
                "es falso",
                "no",
            ]

    # ---------------------------------
    # OPCIÓN MÚLTIPLE
    # ---------------------------------

    elif tipo == "opcion_multiple":

        opciones = actividad[
            "opciones"
        ]

        opciones_texto = " ".join(
            f"Opción {letra}: {texto}"
            for letra, texto
            in opciones.items()
        )

        pregunta = (
            f'{actividad["pregunta"]} '
            f"{opciones_texto}"
        )

        letra_correcta = (
            actividad[
                "respuesta_correcta"
            ]
            .upper()
        )

        texto_correcto = opciones[
            letra_correcta
        ]

        respuestas = [
            letra_correcta,
            f"opcion {letra_correcta}",
            f"opción {letra_correcta}",
            texto_correcto,
        ]

    else:

        raise ValueError(
            "Tipo de actividad "
            f"no reconocido: {tipo}"
        )

    return {
        "pregunta": pregunta,
        "respuestas_validas": respuestas,
        "retroalimentacion_correcta":
            actividad[
                "retroalimentacion_correcta"
            ],
        "retroalimentacion_incorrecta":
            actividad[
                "retroalimentacion_incorrecta"
            ],
    }


# =========================
# INTERACCIÓN PEDAGÓGICA
# =========================

def interactuar_con_tarjeta(
    nombre_clase,
):
    """
    Busca la clase en el JSON y realiza
    una actividad seleccionada al azar.
    """

    clave = normalizar(
        nombre_clase
    )

    datos = base_conocimiento.get(
        clave
    )

    if datos is None:

        hablar(
            f"Reconocí {nombre_clase}, "
            "pero no encuentro su información "
            "en la base de conocimientos."
        )

        return

    nombre = datos.get(
        "nombre",
        nombre_clase,
    )

    descripcion = datos.get(
        "descripcion",
        "",
    )

    microhistoria = " ".join(
        datos.get(
            "microhistoria",
            [],
        )
    )

    actividades = list(
        datos.get(
            "actividades",
            {},
        ).values()
    )

    if not actividades:

        hablar(
            f"Reconocí la tarjeta {nombre}, "
            "pero no tiene actividades."
        )

        return

    actividad_original = random.choice(
        actividades
    )

    actividad = preparar_actividad(
        actividad_original
    )

    introduccion = (
        f"He reconocido la tarjeta {nombre}. "
        f"{descripcion} "
        f"Escucha esta pequeña historia. "
        f"{microhistoria} "
        f"Ahora responde. "
        f"{actividad['pregunta']}"
    )

    hablar(introduccion)

    respuesta_estudiante = escuchar_respuesta(
        actividad[
            "respuestas_validas"
        ]
    )

    if respuesta_es_correcta(
        respuesta_estudiante,
        actividad[
            "respuestas_validas"
        ],
    ):

        hablar(
            actividad[
                "retroalimentacion_correcta"
            ]
        )

    else:

        hablar(
            actividad[
                "retroalimentacion_incorrecta"
            ]
        )


# =========================
# DETECCIÓN CON YOLO
# =========================

def obtener_mejor_deteccion(
    frame,
):
    """
    Ejecuta YOLO y devuelve únicamente
    la detección con mayor confianza.
    """

    resultados = modelo.predict(
        source=frame,
        conf=CONFIANZA_MINIMA,
        iou=IOU_MAXIMO,
        max_det=5,
        verbose=False,
    )

    resultado = resultados[0]

    if len(resultado.boxes) == 0:
        return None

    mejor_indice = int(
        resultado.boxes.conf.argmax()
    )

    mejor_caja = resultado.boxes[
        mejor_indice
    ]

    clase_id = int(
        mejor_caja.cls[0]
    )

    confianza = float(
        mejor_caja.conf[0]
    )

    nombre_clase = modelo.names[
        clase_id
    ]

    coordenadas = tuple(
        map(
            int,
            mejor_caja.xyxy[0],
        )
    )

    return {
        "clase": nombre_clase,
        "confianza": confianza,
        "coordenadas": coordenadas,
    }


def dibujar_deteccion(
    frame,
    deteccion,
):
    """
    Dibuja solamente la detección
    seleccionada por mayor confianza.
    """

    frame_anotado = frame.copy()

    if deteccion is None:
        return frame_anotado

    x1, y1, x2, y2 = deteccion[
        "coordenadas"
    ]

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
        (
            x1,
            max(y1 - 10, 25),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2,
    )

    return frame_anotado


# =========================
# PROGRAMA PRINCIPAL
# =========================

def main():
    """
    Ejecuta la detección automática
    y controla la estabilidad de la tarjeta.
    """

    picam2 = Picamera2()

    configuracion = (
        picam2.create_preview_configuration(
            main={
                "size": (640, 480),
                "format": "RGB888",
            }
        )
    )

    picam2.configure(
        configuracion
    )

    picam2.start()

    time.sleep(2)

    print("")
    print("======================================")
    print("ROBOT EDUCATIVO STEAM V6")
    print("======================================")
    print(
        "Acerca una tarjeta frente "
        "a la cámara."
    )
    print(
        "No es necesario presionar "
        "la tecla C."
    )
    print("Presiona Q para salir.")
    print("======================================")
    print("")

    # Clase que YOLO está tratando
    # de confirmar.
    clase_candidata = None

    # Número de detecciones consecutivas
    # de la misma clase.
    contador_estabilidad = 0

    # Tarjeta que ya realizó una actividad.
    tarjeta_bloqueada = None

    # Fotogramas en los que la tarjeta bloqueada
    # ya no aparece.
    contador_sin_tarjeta = 0

    # Tiempo de la última interacción.
    ultima_interaccion = 0.0

    try:

        while True:

            frame = picam2.capture_array()

            # YOLO analiza continuamente
            # la imagen de la cámara.
            deteccion = obtener_mejor_deteccion(
                frame
            )

            frame_anotado = dibujar_deteccion(
                frame,
                deteccion,
            )

            # ---------------------------------
            # TEXTO DE ESTADO EN PANTALLA
            # ---------------------------------

            if tarjeta_bloqueada is not None:

                estado = (
                    "Retira la tarjeta: "
                    f"{tarjeta_bloqueada}"
                )

            elif deteccion is not None:

                estado = (
                    "Detectando: "
                    f"{deteccion['clase']}"
                )

            else:

                estado = (
                    "Acerca una tarjeta"
                )

            cv2.putText(
                frame_anotado,
                estado,
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame_anotado,
                "Q: salir",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "Robot educativo STEAM V6",
                frame_anotado,
            )

            tecla = (
                cv2.waitKey(1)
                & 0xFF
            )

            if tecla == ord("q"):
                break

            # =================================
            # ESPERAR RETIRO DE LA TARJETA
            # =================================

            if tarjeta_bloqueada is not None:

                # Si no existe detección o se detecta
                # una clase diferente, aumentamos
                # el contador de retiro.
                if deteccion is None:

                    contador_sin_tarjeta += 1

                elif (
                    normalizar(
                        deteccion["clase"]
                    )
                    != normalizar(
                        tarjeta_bloqueada
                    )
                ):

                    contador_sin_tarjeta += 1

                else:

                    # La tarjeta todavía está
                    # frente a la cámara.
                    contador_sin_tarjeta = 0

                # Confirmar que la tarjeta
                # realmente fue retirada.
                if (
                    contador_sin_tarjeta
                    >= FOTOGRAMAS_SIN_TARJETA
                ):

                    print(
                        f"Tarjeta "
                        f"{tarjeta_bloqueada} "
                        "retirada."
                    )

                    tarjeta_bloqueada = None
                    contador_sin_tarjeta = 0
                    clase_candidata = None
                    contador_estabilidad = 0

                    print(
                        "Sistema listo para "
                        "una nueva tarjeta."
                    )

                continue

            # =================================
            # NO EXISTE DETECCIÓN
            # =================================

            if deteccion is None:

                clase_candidata = None
                contador_estabilidad = 0

                continue

            clase_actual = normalizar(
                deteccion["clase"]
            )

            # Comprobar que la clase detectada
            # exista en el JSON.
            if (
                clase_actual
                not in base_conocimiento
            ):

                print(
                    f"La clase {clase_actual} "
                    "no existe en "
                    "base_conocimiento2.json."
                )

                clase_candidata = None
                contador_estabilidad = 0

                continue

            # =================================
            # CONFIRMACIÓN DE ESTABILIDAD
            # =================================

            if (
                clase_actual
                == clase_candidata
            ):

                contador_estabilidad += 1

            else:

                clase_candidata = (
                    clase_actual
                )

                contador_estabilidad = 1

            print(
                f"Clase candidata: "
                f"{clase_actual} | "
                f"Estabilidad: "
                f"{contador_estabilidad}/"
                f"{FOTOGRAMAS_ESTABLES} | "
                f"Confianza: "
                f"{deteccion['confianza']:.2f}"
            )

            # Todavía no se han alcanzado
            # suficientes detecciones consecutivas.
            if (
                contador_estabilidad
                < FOTOGRAMAS_ESTABLES
            ):
                continue

            tiempo_actual = time.time()

            # Evitar una reactivación inmediata
            # después de una actividad anterior.
            if (
                tiempo_actual
                - ultima_interaccion
                < TIEMPO_REACTIVACION
            ):
                continue

            # =================================
            # TARJETA CONFIRMADA
            # =================================

            tarjeta_confirmada = (
                clase_actual
            )

            print("")
            print(
                "Tarjeta confirmada: "
                f"{tarjeta_confirmada}"
            )

            print(
                "Confianza de detección: "
                f"{deteccion['confianza']:.2f}"
            )

            tarjeta_bloqueada = (
                tarjeta_confirmada
            )

            ultima_interaccion = (
                tiempo_actual
            )

            clase_candidata = None
            contador_estabilidad = 0
            contador_sin_tarjeta = 0

            # Mostrar visualmente que
            # la tarjeta fue confirmada.
            cv2.putText(
                frame_anotado,
                "Tarjeta confirmada",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "Robot educativo STEAM V6",
                frame_anotado,
            )

            cv2.waitKey(500)

            # Iniciar la actividad pedagógica.
            interactuar_con_tarjeta(
                tarjeta_confirmada
            )

            print("")
            print(
                "Actividad terminada."
            )

            print(
                "Retira la tarjeta "
                "para continuar."
            )
            print("")

    except KeyboardInterrupt:

        print(
            "\nPrograma detenido "
            "manualmente."
        )

    finally:

        picam2.stop()

        cv2.destroyAllWindows()

        print(
            "Cámara cerrada correctamente."
        )


# =========================
# INICIO DEL PROGRAMA
# =========================

if __name__ == "__main__":

    verificar_archivos()

    print(
        "Cargando el modelo YOLO..."
    )

    modelo = YOLO(
        str(MODELO_YOLO)
    )

    print(
        "Cargando la base "
        "de conocimientos..."
    )

    base_conocimiento = (
        cargar_base_conocimiento()
    )

    print(
        "Cargando el modelo Vosk..."
    )

    modelo_vosk = Model(
        str(MODELO_VOSK)
    )

    print("")
    print("Clases del modelo YOLO:")
    print(modelo.names)

    print("")
    print(
        "Clases de la base "
        "de conocimientos:"
    )

    print(
        list(
            base_conocimiento.keys()
        )
    )

    print("")

    main()