# CV Analyzer

Proyecto académico para comparar un CV en PDF con la descripción de un puesto mediante Streamlit, LangChain y OpenAI, y presentar un análisis estructurado con Pydantic.

**Estado actual:** etapas 1 y 2 completadas: alcance documentado y entorno instalado y verificado. La aplicación aún no está implementada.

## Documentación

- [Alcance, contrato de salida y criterios de aceptación](docs/ALCANCE.md).
- [Plan de desarrollo por etapas y commits](PLAN_DESARROLLO.md).
- [Memoria de trabajo](MEMORIA_PROYECTO.md).
- [Taller de referencia](docs/referencias/TallerCVAnalyzer.md).
- [Guía LangChain/LangGraph](docs/referencias/LangChain_LangGraph2026.md).

## Funcionalidad prevista

1. Cargar un CV PDF con texto seleccionable y escribir una vacante.
2. Extraer el texto del documento y solicitar una evaluación al modelo.
3. Mostrar perfil, experiencia, formación, habilidades, fortalezas, áreas de mejora, ajuste y recomendación.

El CV y la vacante se enviarán a OpenAI al evaluar. El porcentaje será una estimación generada como apoyo a la revisión humana. La primera entrega no incluye OCR, procesamiento por lotes, exportación ni almacenamiento duradero.

## Preparar el entorno en Windows PowerShell

Usar Python 3.12. Si acabas de instalarlo, abre una terminal nueva para cargar el PATH actualizado. Ejecuta los comandos desde la raíz del repositorio.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

`requirements.txt` declara las dependencias de ejecución; `requirements-dev.txt` añade pytest. `requirements-lock.txt` registra las versiones directas y transitivas comprobadas con Python 3.12.10 en Windows de 64 bits. Se aplica como archivo de restricciones para repetir esa resolución; otros sistemas deberán verificar su compatibilidad. Para instalar solo las dependencias de ejecución, usa `-r requirements.txt -c requirements-lock.txt`.

Se utiliza directamente el intérprete del entorno, por lo que no es necesario activar PowerShell ni modificar su política de ejecución.

Si `python` no aparece en el PATH, una instalación por usuario puede invocarse de esta forma:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
```

## Configurar OpenAI

En la terminal que posteriormente ejecutará la aplicación:

```powershell
$env:OPENAI_API_KEY = "tu_clave_de_openai"
```

La clave se configura en el entorno del proceso. Un archivo `.env` no se carga automáticamente. No incluyas credenciales reales en el código o los commits. La instalación y comprobación de paquetes no requieren la clave ni realizan evaluaciones.

## Archivos locales excluidos de Git

`.gitignore` excluye entornos virtuales, cachés, secretos, instaladores locales en `.tools/`, PDF y las carpetas `uploads/`, `outputs/` y `data/`. Guarda los CV y resultados locales dentro de esas carpetas. Los datos sintéticos necesarios para pruebas se incorporarán expresamente en su etapa.

Las instrucciones para iniciar la aplicación y ejecutarla con Docker se incorporarán cuando existan y se hayan comprobado sus puntos de entrada.

## Verificación del entorno

Se comprobó `pip check` sin conflictos y la importación de Streamlit, PyPDF2, LangChain OpenAI, LangChain Core, Pydantic y pytest. Consulta el [registro de la etapa 2](docs/ENTORNO.md). Esta comprobación no valida todavía el análisis de CV ni el acceso a la API.
