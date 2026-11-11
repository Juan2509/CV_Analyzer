"""PDF sintéticos generados en memoria, sin datos personales ni archivos."""

from io import BytesIO

import pytest
from PyPDF2 import PdfWriter
from PyPDF2.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

from services.pdf_processor import ErrorProcesamientoPDF, extraer_texto_pdf


def crear_pdf(textos, *, protegido=False):
    """Crea páginas con texto ASCII, páginas vacías o un PDF sin páginas."""
    escritor = PdfWriter()
    for texto in textos:
        escritor.add_blank_page(width=612, height=792)
        pagina = escritor.pages[-1]
        if texto is None:
            continue

        fuente = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        pagina[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): fuente})}
        )
        contenido = DecodedStreamObject()
        contenido.set_data(
            f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode("ascii")
        )
        pagina[NameObject("/Contents")] = contenido

    if protegido:
        escritor.encrypt("clave-sintetica")
    archivo = BytesIO()
    escritor.write(archivo)
    archivo.seek(0)
    return archivo


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
