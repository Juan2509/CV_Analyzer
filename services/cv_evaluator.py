"""Evaluación estructurada de candidatos mediante LangChain y Google Gemini."""

import os

import httpx2
from google.genai.errors import APIError
from langchain_core.exceptions import (
    ModelAuthenticationError,
    ModelInvalidRequestError,
    ModelNotFoundError,
    ModelPermissionDeniedError,
    ModelRateLimitError,
    OutputParserException,
)
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
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
    clave = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not clave:
        raise ErrorConfiguracionCV(
            "Configura GOOGLE_API_KEY o GEMINI_API_KEY en el entorno antes de analizar un CV."
        )

    try:
        modelo = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "").strip() or "gemini-3.5-flash-lite",
            api_key=clave,
            vertexai=False,
            timeout=30,
            max_retries=1,
        )
        modelo_estructurado = modelo.with_structured_output(
            AnalisisCV, method="json_schema"
        )
        return crear_sistema_prompts() | modelo_estructurado
    except Exception as error:
        raise ErrorConfiguracionCV(
            "No se pudo preparar el evaluador. Revisa la configuración de Gemini."
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
    except (ModelAuthenticationError, ModelPermissionDeniedError) as error:
        raise ErrorConfiguracionCV(
            "Gemini rechazó el acceso. Revisa la clave y los permisos del modelo."
        ) from error
    except ModelNotFoundError as error:
        raise ErrorConfiguracionCV(
            "El modelo de Gemini no está disponible. Revisa GEMINI_MODEL y el acceso de la cuenta."
        ) from error
    except ModelInvalidRequestError as error:
        raise ErrorEvaluacionCV(
            "Gemini rechazó la solicitud. Revisa la clave, el modelo y el tamaño del documento."
        ) from error
    except ModelRateLimitError as error:
        raise ErrorEvaluacionCV(
            "Gemini alcanzó un límite de uso o cuota. Revisa la cuota y reintenta más tarde."
        ) from error
    except (httpx2.TimeoutException, TimeoutError) as error:
        raise ErrorEvaluacionCV(
            "Gemini tardó demasiado en responder. Intenta nuevamente."
        ) from error
    except (httpx2.RequestError, ConnectionError) as error:
        raise ErrorEvaluacionCV(
            "No se pudo conectar con Gemini. Revisa la conexión e intenta nuevamente."
        ) from error
    except APIError as error:
        mensaje = (
            "Gemini tardó demasiado en responder. Intenta nuevamente."
            if error.code == 504 else
            "Gemini no pudo completar la evaluación. Revisa el acceso al modelo o intenta más tarde."
        )
        raise ErrorEvaluacionCV(mensaje) from error
    except Exception as error:
        # Incluye rechazos del modelo y fallos inesperados del adaptador.
        # Se conserva la causa sin exponer datos del CV o credenciales en la UI.
        raise ErrorEvaluacionCV(
            "No se pudo obtener un análisis del candidato. Intenta nuevamente."
        ) from error
