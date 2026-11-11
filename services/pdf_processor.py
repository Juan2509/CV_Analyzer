"""Extracción en memoria de documentos PDF con texto seleccionable."""

from io import BytesIO
from typing import BinaryIO

from PyPDF2 import PdfReader


class ErrorProcesamientoPDF(ValueError):
    """El documento no puede proporcionar texto para la evaluación."""


def extraer_texto_pdf(archivo_pdf: BinaryIO | bytes) -> str:
    """Extrae el texto de las páginas, separándolas con dos saltos de línea.

    Acepta bytes o un archivo binario con soporte de lectura y búsqueda,
    incluido UploadedFile de Streamlit. No cierra el archivo recibido.
    Los errores se comunican con ErrorProcesamientoPDF, nunca como texto
    que pueda confundirse con el contenido del currículum. No realiza OCR.
    """
    archivo = BytesIO(archivo_pdf) if isinstance(archivo_pdf, bytes) else archivo_pdf

    try:
        lector = PdfReader(archivo)
        if lector.is_encrypted:
            raise ErrorProcesamientoPDF(
                "El PDF está protegido. Carga una copia sin contraseña."
            )

        paginas = [
            (pagina.extract_text() or "").strip() if "/Contents" in pagina else ""
            for pagina in lector.pages
        ]
    except ErrorProcesamientoPDF:
        raise
    except Exception as error:
        # Los PDF dañados pueden producir distintas excepciones en el parser.
        # Se unifica el error en el límite del servicio conservando su causa.
        raise ErrorProcesamientoPDF(
            "No se pudo leer el PDF. Comprueba que sea un documento válido "
            "y que no esté dañado."
        ) from error

    if not any(paginas):
        raise ErrorProcesamientoPDF(
            "El PDF no contiene texto extraíble. Carga un CV con texto "
            "seleccionable; los documentos escaneados requieren OCR."
        )

    return "\n\n".join(paginas).strip()
