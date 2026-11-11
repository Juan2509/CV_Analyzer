"""Contrato del evaluador y adaptador Gemini sin tráfico de red."""

import json

import httpx2 as httpx
import pytest
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

from models.cv_model import AnalisisCV
from services import cv_evaluator
from services.cv_evaluator import (
    ErrorConfiguracionCV,
    ErrorEvaluacionCV,
    crear_evaluador_cv,
    evaluar_candidato,
)


@pytest.fixture
def datos():
    return {
        "nombre_candidato": "Perfil ficticio",
        "experiencia_años": 3,
        "habilidades_clave": ["Python"],
        "education": "No especificado",
        "experiencia_relevante": "Tres años desarrollando APIs.",
        "fortalezas": ["Desarrollo de APIs"],
        "areas_mejora": ["Verificar experiencia con Docker"],
        "porcentaje_ajuste": 65,
    }


@pytest.mark.parametrize("clave", [None, "", "   "])
def test_exige_clave_sin_construir_cliente(monkeypatch, clave):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    if clave is None:
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    else:
        monkeypatch.setenv("GOOGLE_API_KEY", clave)

    def cliente_no_esperado(**kwargs):
        pytest.fail("No debe construir el cliente sin una clave")

    monkeypatch.setattr(cv_evaluator, "ChatGoogleGenerativeAI", cliente_no_esperado)
    with pytest.raises(ErrorConfiguracionCV, match="GOOGLE_API_KEY"):
        crear_evaluador_cv()


@pytest.mark.parametrize(
    "google,gemini,esperada",
    [("clave-google", "clave-gemini", "clave-google"),
     ("", "clave-gemini", "clave-gemini"),
     ("   ", " clave-gemini ", "clave-gemini")],
)
def test_clave_alternativa_y_prioridad_de_google(monkeypatch, datos, google, gemini, esperada):
    configuracion = {}

    class ModeloSimulado:
        def with_structured_output(self, schema, **kwargs):
            assert schema is AnalisisCV
            assert kwargs == {"method": "json_schema"}
            return RunnableLambda(lambda _: datos)

    def construir(**kwargs):
        configuracion.update(kwargs)
        return ModeloSimulado()

    monkeypatch.setenv("GOOGLE_API_KEY", google)
    monkeypatch.setenv("GEMINI_API_KEY", gemini)
    monkeypatch.setattr(cv_evaluator, "ChatGoogleGenerativeAI", construir)
    resultado = evaluar_candidato("CV", "Vacante")
    assert resultado.porcentaje_ajuste == 65
    assert configuracion["api_key"] == esperada


def test_permite_configurar_modelo_sin_cambiar_el_contrato(monkeypatch, datos):
    respuesta = {"candidates": [{"index": 0, "finishReason": "STOP", "content": {
        "role": "model", "parts": [{"text": json.dumps(datos)}],
    }}]}
    cliente, _, configuraciones = preparar_transporte(monkeypatch, respuesta)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.6-flash")
    with cliente:
        resultado = evaluar_candidato("CV", "Vacante")
    assert configuraciones[0]["model"] == "gemini-3.6-flash"
    assert resultado.model_dump() == datos


@pytest.mark.parametrize("cv,puesto", [("", "Puesto"), ("  ", "Puesto"), ("CV", ""), ("CV", "  ")])
def test_rechaza_entradas_vacias_antes_de_invocar(cv, puesto):
    def no_invocar(entrada):
        pytest.fail("No debe invocar el modelo con entradas vacías")

    with pytest.raises(ErrorEvaluacionCV):
        evaluar_candidato(cv, puesto, evaluador=RunnableLambda(no_invocar))


def test_transmite_ambos_textos_y_valida_resultado(datos):
    recibidos = []

    def responder(entrada):
        recibidos.append(entrada)
        return datos

    resultado = evaluar_candidato("CV ficticio", "Vacante", evaluador=RunnableLambda(responder))

    assert isinstance(resultado, AnalisisCV)
    assert resultado.model_dump() == datos
    assert recibidos == [{"texto_cv": "CV ficticio", "descripcion_puesto": "Vacante"}]


@pytest.mark.parametrize("resultado", [None, {}, {"porcentaje_ajuste": -1}])
def test_no_fabrica_analisis_para_respuesta_invalida(resultado):
    with pytest.raises(ErrorEvaluacionCV, match="análisis válido") as error:
        evaluar_candidato("CV", "Vacante", evaluador=RunnableLambda(lambda _: resultado))
    assert error.value.__cause__ is not None


def test_conserva_causa_sin_exponer_su_contenido():
    causa = RuntimeError("datos privados de prueba")

    def fallar(_):
        raise causa

    with pytest.raises(ErrorEvaluacionCV) as error:
        evaluar_candidato("CV", "Vacante", evaluador=RunnableLambda(fallar))

    assert error.value.__cause__ is causa
    assert "datos privados" not in str(error.value)


@pytest.mark.parametrize(
    "tipo_error,mensaje",
    [(httpx.ConnectError, "conectar"), (httpx.ReadTimeout, "tardó demasiado")],
)
def test_comunica_fallos_de_conexion_y_tiempo(tipo_error, mensaje):
    causa = tipo_error("Error simulado", request=httpx.Request("POST", "https://example.invalid"))

    def fallar(_):
        raise causa

    with pytest.raises(ErrorEvaluacionCV, match=mensaje) as error:
        evaluar_candidato("CV", "Vacante", evaluador=RunnableLambda(fallar))
    assert error.value.__cause__ is causa


def test_comunica_fallo_al_configurar_cliente(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-ficticia")

    def fallar(**kwargs):
        raise ValueError("Configuración inválida simulada")

    monkeypatch.setattr(cv_evaluator, "ChatGoogleGenerativeAI", fallar)
    with pytest.raises(ErrorConfiguracionCV, match="preparar") as error:
        crear_evaluador_cv()
    assert error.value.__cause__ is not None


def preparar_transporte(monkeypatch, respuesta, estado=200):
    """Usa el cliente LangChain real con respuestas HTTP locales simuladas."""
    solicitudes = []
    configuraciones = []

    def responder(request):
        solicitudes.append(json.loads(request.content))
        return httpx.Response(estado, json=respuesta)

    cliente = httpx.MockTransport(responder)

    def construir(**kwargs):
        configuraciones.append(kwargs)
        return ChatGoogleGenerativeAI(**kwargs, client_args={"transport": cliente})

    monkeypatch.setenv("GOOGLE_API_KEY", "clave-ficticia-sin-acceso")
    monkeypatch.setenv("GOOGLE_GENAI_HTTP_CLIENT", "httpx2")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.setattr(cv_evaluator, "ChatGoogleGenerativeAI", construir)
    return cliente, solicitudes, configuraciones


def test_adaptador_real_con_salida_json_schema_simulada(monkeypatch, datos):
    respuesta = {
        "candidates": [{"index": 0, "finishReason": "STOP", "content": {
            "role": "model", "parts": [{"text": json.dumps(datos)}],
        }}],
    }
    cliente, solicitudes, configuraciones = preparar_transporte(monkeypatch, respuesta)
    with cliente:
        cadena = crear_evaluador_cv()
        assert solicitudes == []  # Construir la cadena no evalúa.
        resultado = evaluar_candidato("CV Python", "Vacante APIs", evaluador=cadena)

    assert resultado.model_dump() == datos
    assert "temperature" not in configuraciones[0]
    assert configuraciones[0]["timeout"] == 30
    cuerpo = solicitudes[0]
    assert configuraciones[0]["model"] == "gemini-3.5-flash-lite"
    assert configuraciones[0]["vertexai"] is False
    assert cuerpo["generationConfig"]["responseMimeType"] == "application/json"
    esquema = cuerpo["generationConfig"]["responseJsonSchema"]
    assert set(esquema["required"]) == set(datos)
    assert "systemInstruction" in cuerpo
    assert cuerpo["contents"][0]["role"] == "user"
    assert "CV Python" in cuerpo["contents"][0]["parts"][0]["text"]
    assert "Vacante APIs" in cuerpo["contents"][0]["parts"][0]["text"]


@pytest.mark.parametrize(
    "estado,tipo_error,mensaje",
    [(401, ErrorConfiguracionCV, "acceso"), (403, ErrorConfiguracionCV, "acceso"),
     (404, ErrorConfiguracionCV, "GEMINI_MODEL"),
     (400, ErrorEvaluacionCV, "solicitud"),
     (429, ErrorEvaluacionCV, "cuota"), (500, ErrorEvaluacionCV, "completar"),
     (504, ErrorEvaluacionCV, "tardó demasiado")],
)
def test_traduce_errores_http_sin_devolver_evaluaciones(monkeypatch, estado, tipo_error, mensaje):
    respuesta = {"error": {"message": "Error simulado", "status": "ERROR", "code": estado}}
    cliente, _, _ = preparar_transporte(monkeypatch, respuesta, estado)
    with cliente, pytest.raises(tipo_error, match=mensaje) as error:
        evaluar_candidato("CV", "Vacante")
    assert error.value.__cause__ is not None


def test_rechazo_del_modelo_no_se_convierte_en_puntuacion(monkeypatch):
    respuesta = {
        "candidates": [], "promptFeedback": {"blockReason": "SAFETY"},
    }
    cliente, _, _ = preparar_transporte(monkeypatch, respuesta)
    with cliente, pytest.raises(ErrorEvaluacionCV) as error:
        evaluar_candidato("CV", "Vacante")
    assert error.value.__cause__ is not None
