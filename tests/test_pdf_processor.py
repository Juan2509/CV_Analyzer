"""PDF sintéticos generados en memoria, sin datos personales ni archivos."""

import pytest

from services.pdf_processor import ErrorProcesamientoPDF, extraer_texto_pdf
from tests.pdf_helpers import crear_pdf


def test_extrae_texto_en_orden_y_separa_paginas():
    archivo = crear_pdf(["Perfil de prueba", "Experiencia Python"])

    assert extraer_texto_pdf(archivo) == "Perfil de prueba\n\nExperiencia Python"
    assert not archivo.closed


def test_acepta_bytes_del_pdf():
    assert extraer_texto_pdf(crear_pdf(["Perfil"]).getvalue()) == "Perfil"


def test_lee_archivo_aunque_su_cursor_este_al_final():
    archivo = crear_pdf(["Perfil"])
    archivo.seek(0, 2)

    assert extraer_texto_pdf(archivo) == "Perfil"


def test_conserva_orden_con_paginas_sin_texto():
    archivo = crear_pdf(["Perfil", None, "Experiencia"])

    assert extraer_texto_pdf(archivo) == "Perfil\n\n\n\nExperiencia"


@pytest.mark.parametrize("textos", [[], [None], ["   "], [None, None]])
def test_rechaza_documentos_sin_texto_extraible(textos):
    with pytest.raises(ErrorProcesamientoPDF, match="no contiene texto extraíble"):
        extraer_texto_pdf(crear_pdf(textos))


@pytest.mark.parametrize("contenido", [b"", b"archivo que no es PDF", b"%PDF-1.7\n"])
def test_rechaza_archivos_vacios_invalidos_o_danados(contenido):
    with pytest.raises(ErrorProcesamientoPDF, match="No se pudo leer") as error:
        extraer_texto_pdf(contenido)

    assert error.value.__cause__ is not None


def test_rechaza_pdf_protegido():
    with pytest.raises(ErrorProcesamientoPDF, match="protegido"):
        extraer_texto_pdf(crear_pdf(["Perfil"], protegido=True))


def test_comunica_error_de_lectura_del_archivo():
    archivo = crear_pdf(["Perfil"])
    archivo.close()

    with pytest.raises(ErrorProcesamientoPDF, match="No se pudo leer"):
        extraer_texto_pdf(archivo)
