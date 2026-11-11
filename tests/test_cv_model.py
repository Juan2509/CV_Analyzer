"""Comprobaciones del contrato de análisis definido en el taller."""

import pytest
from pydantic import ValidationError

from models.cv_model import AnalisisCV


@pytest.fixture
def datos_candidato():
    """Datos ficticios sin información de personas reales."""
    return {
        "nombre_candidato": "Candidata de prueba",
        "experiencia_años": 3,
        "habilidades_clave": ["Python", "APIs REST"],
        "education": "Ingeniería de Sistemas",
        "experiencia_relevante": "Desarrollo de servicios web con Python.",
        "fortalezas": ["Experiencia en integración de APIs"],
        "areas_mejora": ["Ampliar experiencia con Docker"],
        "porcentaje_ajuste": 65,
    }


@pytest.mark.parametrize("porcentaje", [0, 65, 100])
def test_acepta_analisis_valido_y_limites(datos_candidato, porcentaje):
    datos_candidato["porcentaje_ajuste"] = porcentaje

    analisis = AnalisisCV.model_validate(datos_candidato)

    assert analisis.model_dump() == datos_candidato


@pytest.mark.parametrize("porcentaje", [-1, 101, 65.5])
def test_rechaza_ajuste_fuera_del_contrato(datos_candidato, porcentaje):
    datos_candidato["porcentaje_ajuste"] = porcentaje

    with pytest.raises(ValidationError) as error:
        AnalisisCV.model_validate(datos_candidato)

    assert error.value.errors()[0]["loc"] == ("porcentaje_ajuste",)


@pytest.mark.parametrize(
    "campo",
    [
        "nombre_candidato",
        "experiencia_años",
        "habilidades_clave",
        "education",
        "experiencia_relevante",
        "fortalezas",
        "areas_mejora",
        "porcentaje_ajuste",
    ],
)
def test_rechaza_cualquier_campo_obligatorio_ausente(datos_candidato, campo):
    del datos_candidato[campo]

    with pytest.raises(ValidationError) as error:
        AnalisisCV.model_validate(datos_candidato)

    assert any(
        detalle["loc"] == (campo,) and detalle["type"] == "missing"
        for detalle in error.value.errors()
    )


@pytest.mark.parametrize("campo", ["habilidades_clave", "fortalezas", "areas_mejora"])
def test_rechaza_elementos_que_no_son_texto(datos_candidato, campo):
    datos_candidato[campo] = [123]

    with pytest.raises(ValidationError) as error:
        AnalisisCV.model_validate(datos_candidato)

    assert error.value.errors()[0]["loc"] == (campo, 0)
