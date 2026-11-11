"""Contrato del evaluador y adaptador OpenAI sin tráfico de red."""

import json

import httpx
import pytest
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APITimeoutError

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
    if clave is None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("OPENAI_API_KEY", clave)

    def cliente_no_esperado(**kwargs):
        pytest.fail("No debe construir el cliente sin una clave")

    monkeypatch.setattr(cv_evaluator, "ChatOpenAI", cliente_no_esperado)
    with pytest.raises(ErrorConfiguracionCV, match="OPENAI_API_KEY"):
        crear_evaluador_cv()


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
    [(APIConnectionError, "conectar"), (APITimeoutError, "tardó demasiado")],
)
def test_comunica_fallos_de_conexion_y_tiempo(tipo_error, mensaje):
    causa = tipo_error(request=httpx.Request("POST", "https://example.invalid"))

    def fallar(_):
        raise causa

    with pytest.raises(ErrorEvaluacionCV, match=mensaje) as error:
        evaluar_candidato("CV", "Vacante", evaluador=RunnableLambda(fallar))
    assert error.value.__cause__ is causa


def test_comunica_fallo_al_configurar_cliente(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "clave-ficticia")

    def fallar(**kwargs):
        raise ValueError("Configuración inválida simulada")

    monkeypatch.setattr(cv_evaluator, "ChatOpenAI", fallar)
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

    cliente = httpx.Client(transport=httpx.MockTransport(responder))

    def construir(**kwargs):
        configuraciones.append(kwargs)
        return ChatOpenAI(**kwargs, http_client=cliente)

    monkeypatch.setenv("OPENAI_API_KEY", "clave-ficticia-sin-acceso")
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.setattr(cv_evaluator, "ChatOpenAI", construir)
    return cliente, solicitudes, configuraciones


def test_adaptador_real_con_salida_json_schema_simulada(monkeypatch, datos):
    respuesta = {
        "id": "chatcmpl-prueba", "object": "chat.completion", "created": 0,
        "model": "gpt-4o-mini",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {
            "role": "assistant", "content": json.dumps(datos),
        }}],
    }
    cliente, solicitudes, configuraciones = preparar_transporte(monkeypatch, respuesta)
    with cliente:
        cadena = crear_evaluador_cv()
        assert solicitudes == []  # Construir la cadena no evalúa.
        resultado = evaluar_candidato("CV Python", "Vacante APIs", evaluador=cadena)

    assert resultado.model_dump() == datos
    assert configuraciones[0]["temperature"] == 0.2
    assert configuraciones[0]["timeout"] == 30
    cuerpo = solicitudes[0]
    assert cuerpo["model"] == "gpt-4o-mini"
    assert cuerpo["response_format"]["type"] == "json_schema"
    esquema = cuerpo["response_format"]["json_schema"]
    assert esquema["strict"] is True
    assert set(esquema["schema"]["required"]) == set(datos)
    assert esquema["schema"]["additionalProperties"] is False
    assert [m["role"] for m in cuerpo["messages"]] == ["system", "user"]
    assert "CV Python" in cuerpo["messages"][1]["content"]
    assert "Vacante APIs" in cuerpo["messages"][1]["content"]


@pytest.mark.parametrize(
    "estado,tipo_error,mensaje",
    [(401, ErrorConfiguracionCV, "acceso"), (403, ErrorConfiguracionCV, "acceso"),
     (429, ErrorEvaluacionCV, "cuota"), (500, ErrorEvaluacionCV, "completar")],
)
def test_traduce_errores_http_sin_devolver_evaluaciones(monkeypatch, estado, tipo_error, mensaje):
    respuesta = {"error": {"message": "Error simulado", "type": "api_error", "code": None}}
    cliente, _, _ = preparar_transporte(monkeypatch, respuesta, estado)
    with cliente, pytest.raises(tipo_error, match=mensaje) as error:
        evaluar_candidato("CV", "Vacante")
    assert error.value.__cause__ is not None


def test_rechazo_del_modelo_no_se_convierte_en_puntuacion(monkeypatch):
    respuesta = {
        "id": "chatcmpl-rechazo", "object": "chat.completion", "created": 0,
        "model": "gpt-4o-mini",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {
            "role": "assistant", "content": None, "refusal": "Rechazo simulado",
        }}],
    }
    cliente, _, _ = preparar_transporte(monkeypatch, respuesta)
    with cliente, pytest.raises(ErrorEvaluacionCV) as error:
        evaluar_candidato("CV", "Vacante")
    assert error.value.__cause__ is not None
