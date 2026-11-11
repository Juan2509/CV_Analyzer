"""Carga de documentos y presentación del análisis del candidato."""

from hashlib import sha256

import streamlit as st

from models.cv_model import AnalisisCV
from services.cv_evaluator import ErrorEvaluacionCV, evaluar_candidato
from services.pdf_processor import ErrorProcesamientoPDF, extraer_texto_pdf


def clasificar_ajuste(porcentaje: int) -> str:
    """Clasifica el ajuste según la escala principal del taller."""
    if porcentaje >= 80:
        return "Excelente"
    if porcentaje >= 60:
        return "Bueno"
    if porcentaje >= 40:
        return "Regular"
    return "Bajo"


def recomendar_candidato(porcentaje: int) -> str:
    """Aplica la escala de recomendación, distinta de la principal."""
    if porcentaje >= 70:
        return "Candidato recomendado"
    if porcentaje >= 50:
        return "Candidato con potencial"
    return "Candidato no recomendado"


def _mostrar_lista(titulo: str, elementos: list[str]) -> None:
    st.subheader(titulo)
    if not elementos:
        st.write("Sin elementos documentados en el análisis.")
    for elemento in elementos:
        st.text(f"• {elemento}")


def mostrar_analisis(analisis: AnalisisCV) -> None:
    """Presenta todos los campos y ambas escalas sin renderizar HTML externo."""
    st.divider()
    st.header("Análisis del candidato")
    ajuste, evaluacion = st.columns(2)
    ajuste.metric("Ajuste al puesto", f"{analisis.porcentaje_ajuste} %")
    evaluacion.metric("Evaluación principal", clasificar_ajuste(analisis.porcentaje_ajuste))
    st.progress(analisis.porcentaje_ajuste)

    st.subheader("Perfil del candidato")
    st.text(analisis.nombre_candidato)
    st.write("Formación")
    st.text(analisis.education)
    st.write("Experiencia relevante")
    st.text(f"Años indicados en el análisis: {analisis.experiencia_años}")
    st.text(analisis.experiencia_relevante)
    if analisis.experiencia_años == 0:
        st.caption(
            "El valor 0 puede indicar que la duración no está especificada. "
            "Consulta el resumen de experiencia; no implica por sí solo falta de experiencia."
        )

    habilidades, fortalezas, mejoras = st.columns(3)
    with habilidades:
        _mostrar_lista("Habilidades clave", analisis.habilidades_clave)
    with fortalezas:
        _mostrar_lista("Fortalezas", analisis.fortalezas)
    with mejoras:
        _mostrar_lista("Áreas de mejora", analisis.areas_mejora)

    st.subheader("Recomendación final")
    st.info(recomendar_candidato(analisis.porcentaje_ajuste))
    st.caption("Revisa las evidencias del CV antes de tomar una decisión de contratación.")


def _descartar_analisis() -> None:
    """Elimina resultados y mensajes sin modificar los widgets."""
    for clave in ("analisis_cv", "entradas_analizadas", "mensaje_analisis"):
        st.session_state.pop(clave, None)


def _limpiar_formulario() -> None:
    """Se ejecuta como callback antes de reconstruir los widgets."""
    _descartar_analisis()
    generacion = st.session_state.get("generacion_pdf", 0)
    st.session_state.pop(f"cv_pdf_{generacion}", None)
    # El uploader no permite asignar su valor desde session_state.
    # Una clave nueva crea un control vacío sin reutilizar el archivo anterior.
    st.session_state.generacion_pdf = generacion + 1
    st.session_state.descripcion_puesto = ""


def main() -> None:
    """Conserva el resultado en sesión y evalúa solo al pulsar Analizar."""
    st.set_page_config(page_title="CV Analyzer", page_icon="📄", layout="wide")
    st.title("Analizador de currículums con IA")
    st.write("Compara un CV con una vacante y revisa sus coincidencias y áreas de desarrollo.")
    st.info(
        "Al pulsar Analizar Candidato, el texto del CV y la descripción del puesto "
        "se envían a OpenAI. El resultado es una estimación generada como apoyo "
        "a la revisión humana."
    )

    generacion = st.session_state.get("generacion_pdf", 0)
    # Los cambios de widgets se envían al servidor para invalidar resultados
    # anteriores; no se agrupan en st.form, que aplazaría esos cambios.
    documento, vacante = st.columns(2)
    with documento:
        st.subheader("1. Carga el currículum")
        archivo_pdf = st.file_uploader(
            "CV en PDF", type=["pdf"], accept_multiple_files=False,
            key=f"cv_pdf_{generacion}",
            help="Usa un PDF con texto seleccionable. No se realiza OCR.",
        )
    with vacante:
        st.subheader("2. Describe el puesto")
        descripcion = st.text_area(
            "Descripción del puesto", key="descripcion_puesto", height=220,
            placeholder=(
                "Puesto: Desarrollador Python\n"
                "Obligatorios: 3 años de experiencia, Python y APIs REST.\n"
                "Deseables: Docker.\nResponsabilidades: desarrollar servicios."
            ),
        )

    entradas_actuales = (
        sha256(archivo_pdf.getvalue()).hexdigest() if archivo_pdf is not None else None,
        descripcion.strip(),
    )
    if st.session_state.get("entradas_analizadas") != entradas_actuales:
        _descartar_analisis()

    analizar = st.button("Analizar Candidato", type="primary", key="analizar")

    if analizar:
        _descartar_analisis()
        st.session_state.entradas_analizadas = entradas_actuales
        if archivo_pdf is None:
            st.session_state.mensaje_analisis = ("warning", "Carga un CV en PDF antes de analizar.")
        elif not descripcion.strip():
            st.session_state.mensaje_analisis = ("warning", "Escribe la descripción del puesto antes de analizar.")
        else:
            try:
                with st.spinner("Extrayendo el PDF y evaluando al candidato…"):
                    texto = extraer_texto_pdf(archivo_pdf)
                    st.session_state.analisis_cv = evaluar_candidato(texto, descripcion.strip())
            except (ErrorProcesamientoPDF, ErrorEvaluacionCV) as error:
                st.session_state.mensaje_analisis = ("error", str(error))

    mensaje = st.session_state.get("mensaje_analisis")
    if mensaje is not None:
        tipo, contenido = mensaje
        if tipo == "error":
            st.error(contenido)
        else:
            st.warning(contenido)
    analisis = st.session_state.get("analisis_cv")
    if analisis is not None:
        mostrar_analisis(analisis)

    st.divider()
    if st.button("Guardar Análisis", key="guardar", help="El almacenamiento no está disponible en esta versión."):
        st.info("Guardar Análisis es una funcionalidad en desarrollo. No se ha guardado ningún resultado.")
    st.button("Limpiar", key="limpiar", on_click=_limpiar_formulario)
    st.caption(
        "El resultado se conserva temporalmente en esta sesión. "
        "No hay almacenamiento duradero ni exportación. Solo se admite un CV por operación."
    )
