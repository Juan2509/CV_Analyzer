"""Contrato de salida para la evaluación estructurada de un candidato."""

from pydantic import BaseModel, Field


class AnalisisCV(BaseModel):
    """Información del CV y evaluación de su ajuste a una vacante."""

    nombre_candidato: str = Field(
        description="Nombre del candidato extraído del currículum."
    )
    experiencia_años: int = Field(
        description="Años de experiencia relevante para el puesto."
    )
    habilidades_clave: list[str] = Field(
        description="Habilidades del candidato relevantes para la vacante."
    )
    education: str = Field(
        description="Nivel educativo, especialización y formación del candidato."
    )
    experiencia_relevante: str = Field(
        description="Resumen de la experiencia relacionada con el puesto."
    )
    fortalezas: list[str] = Field(
        description="Fortalezas del candidato sustentadas en su currículum."
    )
    areas_mejora: list[str] = Field(
        description="Áreas de desarrollo frente a los requisitos de la vacante."
    )
    porcentaje_ajuste: int = Field(
        ge=0,
        le=100,
        description="Porcentaje estimado de ajuste al puesto, entre 0 y 100."
    )
