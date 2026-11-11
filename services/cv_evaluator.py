"""Evaluación estructurada de candidatos mediante LangChain y OpenAI."""

import os

from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import ValidationError

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts


class ErrorEvaluacionCV(RuntimeError):
    """No se obtuvo un análisis válido; no constituye una evaluación negativa."""


class ErrorConfiguracionCV(ErrorEvaluacionCV):
    """La configuración del proveedor falta o no permite evaluar."""


def crear_evaluador_cv() -> Runnable:
    """Construye la cadena; no realiza una solicitud a la API.

    La credencial se lee del entorno del proceso, sin cargar archivos .env.
    """
    clave = os.getenv("OPENAI_API_KEY", "").strip()
    if not clave:
        raise ErrorConfiguracionCV(
            "Configura OPENAI_API_KEY en el entorno antes de analizar un CV."
        )

    try:
        modelo = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=clave,
            timeout=30,
            max_retries=1,
        )
        modelo_estructurado = modelo.with_structured_output(
            AnalisisCV, method="json_schema", strict=True
        )
        return crear_sistema_prompts() | modelo_estructurado
    except Exception as error:
        raise ErrorConfiguracionCV(
            "No se pudo preparar el evaluador. Revisa la configuración de OpenAI."
        ) from error


def evaluar_candidato(
    texto_cv: str,
    descripcion_puesto: str,
    *,
    evaluador: Runnable | None = None,
) -> AnalisisCV:
    """Evalúa ambos textos y devuelve un análisis validado o un error explícito.

    Permite proporcionar una cadena para reutilizarla o probarla sin red.
    Nunca devuelve puntuaciones ficticias como alternativa a un fallo técnico.
    """
    if not isinstance(texto_cv, str) or not texto_cv.strip():
        raise ErrorEvaluacionCV("El CV debe contener texto antes de evaluar.")
    if not isinstance(descripcion_puesto, str) or not descripcion_puesto.strip():
        raise ErrorEvaluacionCV("Escribe la descripción del puesto antes de evaluar.")

    cadena = evaluador if evaluador is not None else crear_evaluador_cv()
    try:
        resultado = cadena.invoke(
            {"texto_cv": texto_cv, "descripcion_puesto": descripcion_puesto}
        )
        return AnalisisCV.model_validate(resultado)
    except (ValidationError, OutputParserException) as error:
        raise ErrorEvaluacionCV(
            "El modelo no devolvió un análisis válido. Intenta analizar nuevamente."
        ) from error
    except (AuthenticationError, PermissionDeniedError) as error:
        raise ErrorConfiguracionCV(
            "OpenAI rechazó el acceso. Revisa la clave y los permisos del modelo."
        ) from error
    except RateLimitError as error:
        raise ErrorEvaluacionCV(
            "OpenAI alcanzó un límite de uso o cuota. Revisa la cuota y reintenta más tarde."
        ) from error
    except APITimeoutError as error:
        raise ErrorEvaluacionCV(
            "OpenAI tardó demasiado en responder. Intenta nuevamente."
        ) from error
    except APIConnectionError as error:
        raise ErrorEvaluacionCV(
            "No se pudo conectar con OpenAI. Revisa la conexión e intenta nuevamente."
        ) from error
    except APIError as error:
        raise ErrorEvaluacionCV(
            "OpenAI no pudo completar la evaluación. Revisa el acceso al modelo "
            "o intenta más tarde."
        ) from error
    except Exception as error:
        # Incluye rechazos del modelo y fallos inesperados del adaptador.
        # Se conserva la causa sin exponer datos del CV o credenciales en la UI.
        raise ErrorEvaluacionCV(
            "No se pudo obtener un análisis del candidato. Intenta nuevamente."
        ) from error
