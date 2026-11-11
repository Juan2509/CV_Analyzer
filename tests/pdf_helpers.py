"""Generación de documentos PDF sintéticos en memoria."""

from io import BytesIO

from PyPDF2 import PdfWriter
from PyPDF2.generic import DecodedStreamObject, DictionaryObject, NameObject


def crear_pdf(textos, *, protegido=False):
    """Crea páginas con texto ASCII, páginas vacías o un PDF sin páginas."""
    escritor = PdfWriter()
    for texto in textos:
        escritor.add_blank_page(width=612, height=792)
        pagina = escritor.pages[-1]
        if texto is None:
            continue
        fuente = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        pagina[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): fuente})
        })
        contenido = DecodedStreamObject()
        contenido.set_data(f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode("ascii"))
        pagina[NameObject("/Contents")] = contenido
    if protegido:
        escritor.encrypt("clave-sintetica")
    archivo = BytesIO()
    escritor.write(archivo)
    archivo.seek(0)
    return archivo
