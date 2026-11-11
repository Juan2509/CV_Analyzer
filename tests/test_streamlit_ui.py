"""Escalas y recorrido de la interfaz con servicios de evaluación simulados."""

from unittest.mock import Mock
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from models.cv_model import AnalisisCV
from services.cv_evaluator import ErrorConfiguracionCV, ErrorEvaluacionCV
from ui import streamlit_ui
from ui.streamlit_ui import clasificar_ajuste, recomendar_candidato


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize(
    "porcentaje,principal,recomendacion",
    [(0, "Bajo", "Candidato no recomendado"),
     (39, "Bajo", "Candidato no recomendado"),
     (40, "Regular", "Candidato no recomendado"),
     (49, "Regular", "Candidato no recomendado"),
     (50, "Regular", "Candidato con potencial"),
     (59, "Regular", "Candidato con potencial"),
     (60, "Bueno", "Candidato con potencial"),
     (65, "Bueno", "Candidato con potencial"),
     (69, "Bueno", "Candidato con potencial"),
     (70, "Bueno", "Candidato recomendado"),
     (79, "Bueno", "Candidato recomendado"),
     (80, "Excelente", "Candidato recomendado"),
     (100, "Excelente", "Candidato recomendado")],
)
def test_limites_de_ambas_escalas(porcentaje, principal, recomendacion):
    assert clasificar_ajuste(porcentaje) == principal
    assert recomendar_candidato(porcentaje) == recomendacion


@pytest.fixture
def servicios(monkeypatch):
    extraer = Mock(return_value="CV ficticio Python")
    evaluar = Mock(return_value=AnalisisCV(
        nombre_candidato="Perfil de prueba", experiencia_años=0,
        habilidades_clave=["Python"], education="No especificado",
        experiencia_relevante="La duración de la experiencia no está especificada.",
        fortalezas=["Desarrollo de APIs"], areas_mejora=["Verificar Docker"],
        porcentaje_ajuste=65,
    ))
    monkeypatch.setattr(streamlit_ui, "extraer_texto_pdf", extraer)
    monkeypatch.setattr(streamlit_ui, "evaluar_candidato", evaluar)
    return extraer, evaluar


def iniciar_con_entradas():
    app = AppTest.from_file(APP_PATH).run()
    app.file_uploader[0].set_value(("cv.pdf", b"PDF de prueba", "application/pdf"))
    app.text_area[0].set_value("  Vacante Python  ")
    return app


def test_inicio_no_invoca_servicios_y_explica_envio_a_gemini(servicios):
    app = AppTest.from_file(APP_PATH).run()
    assert not app.exception
    assert "se envían a Google Gemini" in app.info[0].value
    assert not app.metric
    for servicio in servicios:
        servicio.assert_not_called()


def test_rechaza_ausencia_de_pdf(servicios):
    app = AppTest.from_file(APP_PATH).run()
    app.text_area[0].set_value("Vacante")
    app.button[0].click().run()
    assert "Carga un CV" in app.warning[0].value
    for servicio in servicios:
        servicio.assert_not_called()


@pytest.mark.parametrize("descripcion", ["", "   "])
def test_rechaza_vacante_vacia(servicios, descripcion):
    app = iniciar_con_entradas()
    app.text_area[0].set_value(descripcion)
    app.button[0].click().run()
    assert "descripción del puesto" in app.warning[0].value
    for servicio in servicios:
        servicio.assert_not_called()


def test_conecta_extraccion_evaluacion_y_presentacion(servicios):
    extraer, evaluar = servicios
    app = iniciar_con_entradas()
    app.button[0].click().run()

    assert not app.exception
    extraer.assert_called_once()
    assert extraer.call_args.args[0].name == "cv.pdf"
    evaluar.assert_called_once_with("CV ficticio Python", "Vacante Python")
    assert [m.value for m in app.metric] == ["65 %", "Bueno"]
    assert any(i.value == "Candidato con potencial" for i in app.info)
    textos = "\n".join(t.value for t in app.text)
    for esperado in ["Perfil de prueba", "No especificado", "Python", "Desarrollo de APIs", "Verificar Docker", "duración"]:
        assert esperado in textos
    assert any("no implica por sí solo" in c.value for c in app.caption)


def test_pdf_invalido_detiene_el_flujo(monkeypatch):
    evaluar = Mock()
    monkeypatch.setattr(streamlit_ui, "evaluar_candidato", evaluar)
    app = iniciar_con_entradas()
    app.button[0].click().run()
    assert not app.exception
    assert "No se pudo leer el PDF" in app.error[0].value
    assert not app.metric
    evaluar.assert_not_called()


@pytest.mark.parametrize("error", [ErrorConfiguracionCV("Configura la clave"), ErrorEvaluacionCV("Fallo de API")])
def test_fallo_del_evaluador_no_muestra_recomendacion(servicios, error):
    servicios[1].side_effect = error
    app = iniciar_con_entradas()
    app.button[0].click().run()
    assert not app.exception
    assert app.error[0].value == str(error)
    assert not app.metric
    assert not any(i.value.startswith("Candidato ") for i in app.info)


def test_guardar_solo_muestra_aviso_sin_evaluar(servicios):
    app = AppTest.from_file(APP_PATH).run()
    app.button[1].click().run()
    assert not app.exception
    assert any("No se ha guardado ningún resultado" in i.value for i in app.info)
    for servicio in servicios:
        servicio.assert_not_called()


def test_resultado_permanece_en_reruns_y_guardar_sin_repetir_llamadas(servicios):
    app = iniciar_con_entradas()
    app.button(key="analizar").click().run()
    app.run()
    assert [m.value for m in app.metric] == ["65 %", "Bueno"]

    app.button(key="guardar").click().run()
    assert not app.exception
    assert [m.value for m in app.metric] == ["65 %", "Bueno"]
    assert any("No se ha guardado ningún resultado" in i.value for i in app.info)
    for servicio in servicios:
        servicio.assert_called_once()


@pytest.mark.parametrize("cambio", ["vacante", "contenido_pdf", "quitar_pdf"])
def test_cambios_invalidan_resultado_sin_reevaluar(servicios, cambio):
    app = iniciar_con_entradas()
    app.button(key="analizar").click().run()
    if cambio == "vacante":
        app.text_area[0].set_value("Puesto diferente").run()
    elif cambio == "contenido_pdf":
        # El nombre no cambia: la identidad depende del contenido.
        app.file_uploader[0].set_value(("cv.pdf", b"Otro CV", "application/pdf")).run()
    else:
        app.file_uploader[0].clear().run()

    assert not app.exception
    assert not app.metric
    assert "analisis_cv" not in app.session_state
    for servicio in servicios:
        servicio.assert_called_once()


def test_volver_a_entradas_previas_no_recupera_analisis_descartado(servicios):
    app = iniciar_con_entradas()
    app.button(key="analizar").click().run()
    app.text_area[0].set_value("Otra vacante").run()
    app.text_area[0].set_value("Vacante Python").run()
    assert not app.metric
    servicios[1].assert_called_once()


def test_limpiar_reinicia_entradas_resultado_y_no_reevalua(servicios):
    app = iniciar_con_entradas()
    app.button(key="analizar").click().run()
    app.button(key="guardar").click().run()
    app.button(key="limpiar").click().run()

    assert not app.exception
    assert app.file_uploader[0].value is None
    assert app.text_area[0].value == ""
    assert not app.metric
    assert not app.error
    assert not app.warning
    assert not any("No se ha guardado" in i.value for i in app.info)
    assert "analisis_cv" not in app.session_state
    for servicio in servicios:
        servicio.assert_called_once()

    app.file_uploader[0].set_value(("nuevo.pdf", b"Nuevo CV", "application/pdf"))
    app.text_area[0].set_value("Nuevo puesto")
    app.button(key="analizar").click().run()
    assert not app.exception
    assert len(app.metric) == 2
    assert servicios[1].call_count == 2


def test_fallo_en_reanalisis_descarta_resultado_anterior_y_limpiar_borra_error(servicios):
    app = iniciar_con_entradas()
    app.button(key="analizar").click().run()
    servicios[1].side_effect = ErrorEvaluacionCV("Error de prueba")
    app.button(key="analizar").click().run()

    assert not app.metric
    assert app.error[0].value == "Error de prueba"
    app.run()
    assert app.error[0].value == "Error de prueba"
    assert servicios[1].call_count == 2
    app.button(key="limpiar").click().run()
    assert not app.error
    assert not app.metric


def test_sesiones_no_comparten_resultados(servicios):
    primera = iniciar_con_entradas()
    primera.button(key="analizar").click().run()
    segunda = AppTest.from_file(APP_PATH).run()
    assert len(primera.metric) == 2
    assert not segunda.metric
    assert segunda.file_uploader[0].value is None
    assert segunda.text_area[0].value == ""
    servicios[1].assert_called_once()
