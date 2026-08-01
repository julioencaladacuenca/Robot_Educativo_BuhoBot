const botonIniciar = document.getElementById("botonIniciar");
const botonNuevaTarjeta = document.getElementById("botonNuevaTarjeta");
const botonDetener = document.getElementById("botonDetener");
const botonEstadisticas = document.getElementById("botonEstadisticas");
const cantidadPreguntas = document.getElementById("cantidadPreguntas");

const indicador = document.getElementById("indicador");
const textoEstado = document.getElementById("textoEstado");
const detalleEstado = document.getElementById("detalleEstado");

const barraProgreso = document.getElementById("barraProgreso");
const porcentajeProgreso = document.getElementById("porcentajeProgreso");
const mensajeProceso = document.getElementById("mensajeProceso");
const barraAccesible = document.getElementById("barraAccesible");

const vistaCamara = document.getElementById("vistaCamara");
const vistaCentral = document.getElementById("vistaCentral");
const tituloEscenario = document.getElementById("tituloEscenario");
const estadoCamara = document.getElementById("estadoCamara");
const tituloCentral = document.getElementById("tituloCentral");
const mensajeCentral = document.getElementById("mensajeCentral");
const medallasResultado = document.getElementById("medallasResultado");
const mensajeCamaraTitulo = document.getElementById("mensajeCamaraTitulo");
const mensajeCamaraTexto = document.getElementById("mensajeCamaraTexto");
const imagenBuhobot = document.getElementById("imagenBuhobot");

const tarjetaDetectada = document.getElementById("tarjetaDetectada");
const confianza = document.getElementById("confianza");
const numeroPregunta = document.getElementById("numeroPregunta");
const resultado = document.getElementById("resultado");
const correctas = document.getElementById("correctas");
const incorrectas = document.getElementById("incorrectas");
const porcentajeResultado = document.getElementById("porcentajeResultado");
const puntajeFinal = document.getElementById("puntajeFinal");
const tipoActividad = document.getElementById("tipoActividad");
const preguntaActual = document.getElementById("preguntaActual");
const respuestaReconocida = document.getElementById("respuestaReconocida");

const listaHistorial = document.getElementById("listaHistorial");
const historialVacio = document.getElementById("historialVacio");
const cantidadHistorial = document.getElementById("cantidadHistorial");

const modalEstadisticas = document.getElementById("modalEstadisticas");
const cerrarEstadisticas = document.getElementById("cerrarEstadisticas");
const botonReiniciarEstadisticas = document.getElementById("botonReiniciarEstadisticas");
const mensajeReinicioEstadisticas = document.getElementById("mensajeReinicioEstadisticas");
const estadSesiones = document.getElementById("estadSesiones");
const estadPreguntas = document.getElementById("estadPreguntas");
const estadCorrectas = document.getElementById("estadCorrectas");
const estadIncorrectas = document.getElementById("estadIncorrectas");
const estadPorcentaje = document.getElementById("estadPorcentaje");
const estadisticasPorTarjeta = document.getElementById("estadisticasPorTarjeta");
const listaSesionesEstadisticas = document.getElementById("listaSesionesEstadisticas");

const actividadEstado = document.getElementById("actividadEstado");
const actividadPreguntas = document.getElementById("actividadPreguntas");
const actividadCorrectas = document.getElementById("actividadCorrectas");
const actividadIncorrectas = document.getElementById("actividadIncorrectas");
const actividadPorcentaje = document.getElementById("actividadPorcentaje");

let ultimoEstadoRecibido = {};


async function reproducirBienvenidaInicial() {
    try {
        await fetch("/bienvenida", {
            method: "POST",
        });
    } catch (error) {
        console.error(
            "No se pudo reproducir la bienvenida:",
            error
        );
    }
}


async function iniciarActividad() {
    const cantidad = Number(cantidadPreguntas.value);

    try {
        const respuestaServidor = await fetch("/iniciar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                cantidad_preguntas: cantidad,
            }),
        });

        const datos = await respuestaServidor.json();

        if (!datos.ok) {
            throw new Error("No fue posible iniciar.");
        }

    } catch (error) {
        console.error(error);
        alert("No fue posible iniciar la actividad.");
    }
}


async function solicitarNuevaTarjeta() {
    try {
        const respuestaServidor = await fetch("/nueva_tarjeta", {
            method: "POST",
        });

        const datos = await respuestaServidor.json();

        if (!datos.ok) {
            throw new Error("No fue posible continuar.");
        }

    } catch (error) {
        console.error(error);
        alert("No fue posible buscar una nueva tarjeta.");
    }
}


async function detenerActividad() {
    try {
        await fetch("/detener", {
            method: "POST",
        });

    } catch (error) {
        console.error(error);
        alert("No fue posible detener la actividad.");
    }
}


function actualizarBarra(datos) {
    const progreso = Math.max(
        0,
        Math.min(Number(datos.progreso || 0), 100)
    );

    barraProgreso.style.width = `${progreso}%`;
    porcentajeProgreso.textContent = `${progreso} %`;

    barraAccesible.setAttribute(
        "aria-valuenow",
        String(progreso)
    );

    if (datos.procesando) {
        barraProgreso.classList.add("procesando");
    } else {
        barraProgreso.classList.remove("procesando");
    }

    mensajeProceso.textContent =
        datos.detalle_estado
        || "BúhoBot está trabajando.";
}




const IMAGENES_BUHOBOT = {
    saludo: "/static/saludo.png?v=20260730-final-sin-transcripcion-2",
    buscando: "/static/buo_buscando.png?v=20260730-final-sin-transcripcion-2",

    escuela: "/static/buo_detectada_escuela.png?v=20260730-final-sin-transcripcion-2",
    parque: "/static/buo_detectada_parque.png?v=20260730-final-sin-transcripcion-2",
    hospital: "/static/buo_detectada_hospital.png?v=20260730-final-sin-transcripcion-2",
    panaderia: "/static/buo_detectada_panaderia.png?v=20260730-final-sin-transcripcion-2",
    supermercado: "/static/buo_detectada_supermercado.png?v=20260730-final-sin-transcripcion-2",

    feliz: "/static/buo_feliz.png?v=20260730-final-sin-transcripcion-2",
    explicando: "/static/buo_explicando.png?v=20260730-final-sin-transcripcion-2",

    medalla1: "/static/buho_1_medalla.png?v=20260730-final-sin-transcripcion-2",
    medalla2: "/static/buho_2_medallas.png?v=20260730-final-sin-transcripcion-2",
    medalla3: "/static/buho_3_medallas.png?v=20260730-final-sin-transcripcion-2",
    medalla4: "/static/buho_4_medallas.png?v=20260730-final-sin-transcripcion-2",
    explorador: "/static/buho_explorador.png?v=20260730-final-sin-transcripcion-2",
};


function normalizarTexto(valor) {
    return String(valor || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}


function imagenDeTarjeta(tarjeta) {
    const clase = normalizarTexto(tarjeta);

    return IMAGENES_BUHOBOT[clase]
        || IMAGENES_BUHOBOT.saludo;
}


function seleccionarImagenBuhobot(datos) {
    const vista = normalizarTexto(datos.vista_actual);
    const resultadoActual = normalizarTexto(datos.resultado);
    const tarjeta =
        datos.tarjeta_detectada
        || datos.tarjeta
        || "";

    if (vista === "inicio") {
        return IMAGENES_BUHOBOT.saludo;
    }

    if (vista === "indicacion") {
        return IMAGENES_BUHOBOT.buscando;
    }

    /*
     * El cierre usa una imagen de medalla según el total
     * de respuestas correctas. Cuando no hay aciertos,
     * BúhoBot aparece feliz y la interfaz entrega la
     * insignia "Explorador de BúhoBot", sin mostrar cero.
     */
    if (vista === "resultado") {
        const correctas = Number(datos.correctas || 0);

        if (correctas >= 4) {
            return IMAGENES_BUHOBOT.medalla4;
        }

        if (correctas === 3) {
            return IMAGENES_BUHOBOT.medalla3;
        }

        if (correctas === 2) {
            return IMAGENES_BUHOBOT.medalla2;
        }

        if (correctas === 1) {
            return IMAGENES_BUHOBOT.medalla1;
        }

        return IMAGENES_BUHOBOT.explorador;
    }

    if (resultadoActual === "correcta") {
        return IMAGENES_BUHOBOT.feliz;
    }

    if (resultadoActual === "incorrecta") {
        return IMAGENES_BUHOBOT.explicando;
    }

    /*
     * Durante la presentación, la historia, la pregunta,
     * la escucha y el procesamiento se conserva la imagen
     * correspondiente a la tarjeta detectada.
     */
    if (
        vista === "tarjeta"
        || vista === "buho"
        || vista === "actividad"
    ) {
        return imagenDeTarjeta(tarjeta);
    }

    return IMAGENES_BUHOBOT.saludo;
}

let imagenActualBuhobot = "";


function actualizarImagenBuhobot(datos) {
    if (!imagenBuhobot) {
        return;
    }

    const nuevaImagen = seleccionarImagenBuhobot(datos);

    if (nuevaImagen === imagenActualBuhobot) {
        return;
    }

    imagenActualBuhobot = nuevaImagen;
    imagenBuhobot.classList.add("cambiando");

    window.setTimeout(() => {
        imagenBuhobot.src = nuevaImagen;
        imagenBuhobot.onload = () => {
            imagenBuhobot.classList.remove("cambiando");
        };
    }, 120);
}


function actualizarVista(datos) {
    const vista = datos.vista_actual || "inicio";

    if (vista === "camara") {
        vistaCamara.classList.remove("oculto");
        vistaCentral.classList.add("oculto");

        tituloEscenario.textContent = "Cámara en vivo";
        estadoCamara.textContent = "Buscando tarjeta";

        mensajeCamaraTitulo.textContent =
            datos.estado || "Buscando una tarjeta";

        mensajeCamaraTexto.textContent =
            datos.detalle_estado
            || "Mantenla completa y sin reflejos.";

    } else {
        vistaCamara.classList.add("oculto");
        vistaCentral.classList.remove("oculto");

        tituloEscenario.textContent =
            vista === "resultado"
                ? "Resultado"
                : "BúhoBot";

        estadoCamara.textContent =
            vista === "tarjeta"
                ? "Tarjeta confirmada"
                : vista === "actividad"
                ? "Actividad en curso"
                : vista === "resultado"
                ? "Actividad finalizada"
                : "Listo para comenzar";

        tituloCentral.textContent =
            datos.titulo_central || "BúhoBot";

        mensajeCentral.textContent =
            datos.mensaje_central || "";
    }

    if (vista === "resultado") {
        botonNuevaTarjeta.classList.remove("oculto");
    } else {
        botonNuevaTarjeta.classList.add("oculto");
    }
}




function escaparHtml(valor) {
    return String(valor ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}




function actualizarMedallas(datos) {
    if (datos.vista_actual !== "resultado") {
        medallasResultado.classList.add("oculto");
        medallasResultado.innerHTML = "";
        return;
    }

    const reconocimiento =
        datos.reconocimiento_texto
        || datos.medallas_texto
        || "⭐ Explorador de BúhoBot";

    medallasResultado.classList.remove("oculto");
    medallasResultado.innerHTML = `
        <span class="reconocimiento-final">
            ${escaparHtml(reconocimiento)}
        </span>
    `;
}

function actualizarHistorial(historial) {
    const actividades = Array.isArray(historial)
        ? historial
        : [];

    cantidadHistorial.textContent =
        `${actividades.length} ${
            actividades.length === 1
                ? "actividad"
                : "actividades"
        }`;

    if (actividades.length === 0) {
        historialVacio.classList.remove("oculto");
        listaHistorial.innerHTML = "";
        return;
    }

    historialVacio.classList.add("oculto");

    listaHistorial.innerHTML = actividades
        .map((actividad) => {
            const correcta =
                actividad.resultado === "Correcta";

            const claseResultado = correcta
                ? "correcta"
                : "incorrecta";

            return `
                <article class="tarjeta-historial">
                    <div class="cabecera-actividad">
                        <h3>
                            Actividad ${escaparHtml(actividad.numero)}:
                            ${escaparHtml(actividad.tipo)}
                        </h3>

                        <span
                            class="insignia-resultado ${claseResultado}"
                        >
                            ${escaparHtml(actividad.resultado)}
                        </span>
                    </div>

                    <div class="cuerpo-actividad">
                        <div class="campo-historial completo">
                            <span>Pregunta o enunciado</span>
                            <p>${escaparHtml(actividad.pregunta)}</p>
                        </div>

                        <div class="campo-historial">
                            <span>Respuesta reconocida</span>
                            <p>
                                ${escaparHtml(
                                    actividad.respuesta_reconocida || "—"
                                )}
                            </p>
                        </div>

                        <div class="campo-historial">
                            <span>Resultado</span>
                            <p>${escaparHtml(actividad.resultado)}</p>
                        </div>

                        <div class="campo-historial completo">
                            <span>Retroalimentación de BúhoBot</span>
                            <p>
                                ${escaparHtml(
                                    actividad.retroalimentacion
                                )}
                            </p>
                        </div>
                    </div>
                </article>
            `;
        })
        .join("");
}




function formatearFecha(fechaIso) {
    if (!fechaIso) {
        return "Sin fecha";
    }

    const fecha = new Date(fechaIso);

    if (Number.isNaN(fecha.getTime())) {
        return fechaIso;
    }

    return fecha.toLocaleString("es-EC");
}



function dibujarResumenActividadActual(datos) {
    const historial = Array.isArray(datos.historial_actividades)
        ? datos.historial_actividades
        : [];

    const correctasActuales = Number(datos.correctas || 0);
    const incorrectasActuales = Number(datos.incorrectas || 0);
    const contestadas = correctasActuales + incorrectasActuales;
    const totalConfigurado = Number(
        datos.total_preguntas
        || historial.length
        || 0
    );

    const porcentajeActual = contestadas > 0
        ? Math.round((correctasActuales / contestadas) * 100)
        : 0;

    actividadPreguntas.textContent =
        totalConfigurado > 0
            ? `${contestadas} de ${totalConfigurado}`
            : String(contestadas);

    actividadCorrectas.textContent = correctasActuales;
    actividadIncorrectas.textContent = incorrectasActuales;
    actividadPorcentaje.textContent = `${porcentajeActual} %`;

    const finalizada =
        datos.vista_actual === "resultado"
        && !datos.actividad_activa;

    actividadEstado.textContent = finalizada
        ? "Actividad finalizada"
        : contestadas > 0
        ? "Actividad en curso"
        : "Todavía no inicia";
}

function dibujarEstadisticas(datos) {
    const resumen = datos.resumen || {};
    const porTarjeta = Array.isArray(
        resumen.por_tarjeta
    )
        ? resumen.por_tarjeta
        : [];

    const sesiones = Array.isArray(
        datos.sesiones
    )
        ? datos.sesiones
        : [];

    estadSesiones.textContent =
        resumen.total_sesiones ?? 0;

    estadPreguntas.textContent =
        resumen.total_preguntas ?? 0;

    estadCorrectas.textContent =
        resumen.correctas ?? 0;

    estadIncorrectas.textContent =
        resumen.incorrectas ?? 0;

    estadPorcentaje.textContent =
        `${resumen.porcentaje_global ?? 0} %`;

    estadisticasPorTarjeta.innerHTML =
        porTarjeta.length > 0
            ? porTarjeta.map((fila) => `
                <tr>
                    <td>${escaparHtml(fila.tarjeta)}</td>
                    <td>${fila.sesiones}</td>
                    <td>${fila.preguntas}</td>
                    <td>${fila.correctas}</td>
                    <td>${fila.incorrectas}</td>
                    <td>${fila.porcentaje} %</td>
                </tr>
            `).join("")
            : `
                <tr>
                    <td colspan="6">
                        Todavía no existen registros.
                    </td>
                </tr>
            `;

    listaSesionesEstadisticas.innerHTML =
        sesiones.length > 0
            ? sesiones.map((sesion) => {
                const actividades = Array.isArray(
                    sesion.actividades
                )
                    ? sesion.actividades
                    : [];

                return `
                    <details class="sesion-estadistica">
                        <summary>
                            <span>
                                ${escaparHtml(sesion.tarjeta)}
                                · ${formatearFecha(sesion.fecha)}
                            </span>

                            <strong>
                                ${sesion.correctas}
                                de
                                ${sesion.total_preguntas}
                                (${sesion.porcentaje} %)
                            </strong>
                        </summary>

                        <div class="detalle-sesion-estadistica">
                            ${actividades.map((actividad) => `
                                <div class="actividad-estadistica">
                                    <p>
                                        <strong>
                                            Pregunta ${actividad.numero}:
                                        </strong>
                                        ${escaparHtml(actividad.pregunta)}
                                    </p>

                                    <p>
                                        <strong>
                                            Texto reconocido:
                                        </strong>
                                        ${escaparHtml(
                                            actividad.respuesta_reconocida || "—"
                                        )}
                                    </p>

                                    <p>
                                        <strong>Resultado:</strong>
                                        ${escaparHtml(actividad.resultado)}
                                    </p>
                                </div>
                            `).join("")}
                        </div>
                    </details>
                `;
            }).join("")
            : `
                <div class="historial-vacio">
                    Todavía no existen cartas trabajadas.
                </div>
            `;
}


async function abrirEstadisticas() {
    modalEstadisticas.classList.remove(
        "oculto"
    );

    dibujarResumenActividadActual(
        ultimoEstadoRecibido
    );

    listaSesionesEstadisticas.innerHTML =
        "<p>Cargando estadísticas acumuladas…</p>";

    try {
        const respuesta = await fetch(
            "/estadisticas"
        );

        const datos = await respuesta.json();

        if (!datos.ok) {
            throw new Error(
                "No fue posible leer las estadísticas."
            );
        }

        dibujarEstadisticas(datos);

    } catch (error) {
        console.error(error);

        listaSesionesEstadisticas.innerHTML = `
            <div class="historial-vacio">
                No fue posible cargar las estadísticas.
            </div>
        `;
    }
}


async function reiniciarEstadisticasAcumuladas() {
    const confirmar = window.confirm(
        "¿Está seguro de borrar todas las estadísticas acumuladas? Esta acción no se puede deshacer."
    );

    if (!confirmar) {
        return;
    }

    botonReiniciarEstadisticas.disabled = true;
    mensajeReinicioEstadisticas.textContent =
        "Reiniciando estadísticas…";

    try {
        const respuesta = await fetch(
            "/estadisticas/reiniciar",
            { method: "POST" }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.ok) {
            throw new Error(
                datos.mensaje ||
                "No fue posible reiniciar las estadísticas."
            );
        }

        dibujarEstadisticas(datos);
        mensajeReinicioEstadisticas.textContent =
            "Las estadísticas acumuladas se reiniciaron correctamente.";

    } catch (error) {
        console.error(error);
        mensajeReinicioEstadisticas.textContent =
            "No fue posible reiniciar las estadísticas.";

    } finally {
        botonReiniciarEstadisticas.disabled = false;
    }
}


function ocultarEstadisticas() {
    modalEstadisticas.classList.add(
        "oculto"
    );
}


async function actualizarEstado() {
    try {
        const respuestaServidor = await fetch("/estado");
        const datos = await respuestaServidor.json();
        ultimoEstadoRecibido = datos;

        textoEstado.textContent =
            datos.estado || "";

        detalleEstado.textContent =
            datos.detalle_estado || "";

        tarjetaDetectada.textContent =
            datos.tarjeta_detectada
            || datos.tarjeta
            || "Ninguna";

        confianza.textContent =
            datos.confianza === null
            || datos.confianza === undefined
                ? "—"
                : `${datos.confianza} %`;

        numeroPregunta.textContent =
            `${datos.pregunta_actual || 0} de ${datos.total_preguntas || 1}`;

        resultado.textContent =
            datos.resultado || "Pendiente";

        correctas.textContent =
            datos.correctas ?? 0;

        incorrectas.textContent =
            datos.incorrectas ?? 0;

        porcentajeResultado.textContent =
            `${datos.porcentaje ?? 0} %`;

        puntajeFinal.textContent =
            datos.puntaje_texto || "Pendiente";

        tipoActividad.textContent =
            datos.tipo_actividad || "—";

        preguntaActual.textContent =
            datos.pregunta
            || "Todavía no se ha formulado una pregunta.";

        if (respuestaReconocida) {
            respuestaReconocida.textContent = datos.respuesta || "—";
        }

        actualizarBarra(datos);
        actualizarVista(datos);
        actualizarImagenBuhobot(datos);
        actualizarMedallas(datos);
        actualizarHistorial(datos.historial_actividades);

        if (datos.actividad_activa) {
            indicador.textContent =
                datos.robot_ocupado
                    ? "BúhoBot interactuando"
                    : "Actividad iniciada";

            indicador.classList.remove("detenido");
            indicador.classList.add("activo");

            botonIniciar.disabled = true;
            botonDetener.disabled = false;
            cantidadPreguntas.disabled = true;

        } else {
            indicador.textContent = "BúhoBot está listo";

            indicador.classList.remove("activo");
            indicador.classList.add("detenido");

            botonIniciar.disabled = false;
            botonDetener.disabled = true;
            cantidadPreguntas.disabled = false;
        }

    } catch (error) {
        console.error(
            "No se pudo actualizar el estado:",
            error
        );

        mensajeProceso.textContent =
            "No se pudo consultar el estado de BúhoBot.";
    }
}


botonIniciar.addEventListener(
    "click",
    iniciarActividad
);

botonNuevaTarjeta.addEventListener(
    "click",
    solicitarNuevaTarjeta
);

botonDetener.addEventListener(
    "click",
    detenerActividad
);

botonEstadisticas.addEventListener(
    "click",
    abrirEstadisticas
);

cerrarEstadisticas.addEventListener(
    "click",
    ocultarEstadisticas
);


botonReiniciarEstadisticas.addEventListener(
    "click",
    reiniciarEstadisticasAcumuladas
);

modalEstadisticas.addEventListener(
    "click",
    (evento) => {
        if (
            evento.target === modalEstadisticas
        ) {
            ocultarEstadisticas();
        }
    }
);

actualizarEstado();
reproducirBienvenidaInicial();

setInterval(
    actualizarEstado,
    400
);
