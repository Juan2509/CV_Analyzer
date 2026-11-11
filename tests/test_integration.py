"""Flujo real PDF → prompts → adaptador → Pydantic → UI con HTTP simulado."""

import json
from pathlib import Path

import httpx2 as httpx
import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit.testing.v1 import AppTest

from services import cv_evaluator
from tests.pdf_helpers import crear_pdf


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def transporte(monkeypatch):
    solicitudes = []
    estado = {"codigo": 200, "invalido": False}

    def responder(request):
        solicitudes.append(json.loads(request.content))
        if estado["codigo"] != 200:
            return httpx.Response(estado["codigo"], json={"error": {
                "message": "Fallo sintético", "status": "ERROR", "code": estado["codigo"],
            }})
        datos = {
            "nombre_candidato": "Perfil sintetico", "experiencia_años": 3,
            "habilidades_clave": ["Python", "APIs REST"],
            "education": "Ingenieria de Sistemas",
            "experiencia_relevante": "Tres años desarrollando servicios Python.",
            "fortalezas": ["Integracion de APIs"], "areas_mejora": ["Verificar Docker"],
            "porcentaje_ajuste": 101 if estado["invalido"] else 65,
        }
        return httpx.Response(200, json={
            "candidates": [{"index": 0, "finishReason": "STOP", "content": {
                "role": "model", "parts": [{"text": json.dumps(datos)}],
            }}],
        })

    with httpx.MockTransport(responder) as transporte_http:
        def construir(**kwargs):
            # No esperar entre reintentos en pruebas de error HTTP simulado.
            kwargs["max_retries"] = 1
            return ChatGoogleGenerativeAI(**kwargs, client_args={"transport": transporte_http})

        monkeypatch.setattr(cv_evaluator, "ChatGoogleGenerativeAI", construir)
        monkeypatch.setenv("GOOGLE_API_KEY", "clave-sintetica-sin-acceso")
        monkeypatch.setenv("GOOGLE_GENAI_HTTP_CLIENT", "httpx2")
        monkeypatch.setenv("LANGSMITH_TRACING", "false")
        monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
        yield solicitudes, estado


def cargar_cv(textos=None):
    app = AppTest.from_file(APP_PATH).run()
    contenido = crear_pdf(textos if textos is not None else [
        "Perfil sintetico - Ingenieria de Sistemas", "3 anos de Python y APIs REST",
    ]).getvalue()
    app.file_uploader[0].set_value(("cv-sintetico.pdf", contenido, "application/pdf"))
    app.text_area[0].set_value("Vacante Python: APIs REST, 3 años. Deseable Docker.")
    app.button(key="analizar").click().run()
    return app


def test_recorrido_completo_con_pdf_y_adaptador_reales(transporte):
    solicitudes, _ = transporte
    app = cargar_cv()
    assert not app.exception
    assert not app.error
    assert [m.value for m in app.metric] == ["65 %", "Bueno"]
    assert any(i.value == "Candidato con potencial" for i in app.info)
    assert len(solicitudes) == 1
    datos_enviados = solicitudes[0]["contents"][0]["parts"][0]["text"]
    assert "Perfil sintetico - Ingenieria de Sistemas\n\n3 anos de Python" in datos_enviados
    assert "Vacante Python: APIs REST" in datos_enviados
    app.button(key="guardar").click().run()
    assert len(solicitudes) == 1
    assert len(app.metric) == 2
    app.button(key="limpiar").click().run()
    assert not app.metric
    assert app.file_uploader[0].value is None


@pytest.mark.parametrize("codigo,mensaje", [(401, "acceso"), (429, "cuota")])
def test_error_http_llega_a_interfaz_sin_puntuacion(transporte, codigo, mensaje):
    solicitudes, estado = transporte
    estado["codigo"] = codigo
    app = cargar_cv()
    assert not app.exception
    assert mensaje in app.error[0].value
    assert not app.metric
    assert len(solicitudes) == 1


def test_respuesta_fuera_de_rango_no_se_presenta_como_analisis(transporte):
    _, estado = transporte
    estado["invalido"] = True
    app = cargar_cv()
    assert not app.exception
    assert "análisis válido" in app.error[0].value
    assert not app.metric


def test_pdf_sin_texto_no_llega_al_transporte(transporte):
    solicitudes, _ = transporte
    app = cargar_cv([None])
    assert not app.exception
    assert "no contiene texto extraíble" in app.error[0].value
    assert not app.metric
    assert solicitudes == []


def test_ausencia_de_clave_llega_a_interfaz_sin_solicitud(transporte, monkeypatch):
    solicitudes, _ = transporte
    monkeypatch.delenv("GOOGLE_API_KEY")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app = cargar_cv()
    assert not app.exception
    assert "GOOGLE_API_KEY" in app.error[0].value
    assert not app.metric
    assert solicitudes == []
