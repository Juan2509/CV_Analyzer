# CV Analyzer

Proyecto académico para comparar un CV en PDF con la descripción de un puesto mediante Streamlit, LangChain y OpenAI, y presentar un análisis estructurado con Pydantic.

**Estado actual:** etapas 1 a 8 completadas con pruebas locales, incluida la interfaz Streamlit con resultados temporales por sesión y limpieza del formulario. Docker y la verificación con una cuenta real aún están pendientes.

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

## Iniciar la aplicación

Desde la raíz del repositorio, con la clave configurada en esa terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false
```

Abre <http://localhost:8501>. Para detenerla, pulsa `Ctrl+C` en la terminal. Si el puerto está ocupado, cambia `--server.port`.

1. Carga un PDF con texto seleccionable.
2. Describe requisitos, responsabilidades y habilidades deseables de la vacante.
3. Pulsa **Analizar Candidato**. La aplicación extrae el PDF y solicita la evaluación a OpenAI.
4. Revisa el perfil, la experiencia, la formación, las listas y ambas clasificaciones.

El formulario valida las entradas y muestra los fallos de extracción o evaluación sin inventar puntuaciones. El ajuste principal y la recomendación usan escalas diferentes: 65 % se presenta como **Bueno** y **Candidato con potencial**. El aviso previo explica que los textos se envían a OpenAI y que el análisis apoya la revisión humana.

**Guardar Análisis** solo muestra un aviso de funcionalidad en desarrollo y conserva el resultado visible. **Limpiar** borra el PDF cargado, la descripción, el resultado y los mensajes del análisis. No existe exportación ni almacenamiento duradero.

El análisis se mantiene en `st.session_state`, separado para cada sesión. Se asocia al contenido del PDF mediante SHA-256 y a la descripción del puesto sin espacios iniciales o finales. Al cambiar esas entradas se descarta el resultado anterior; volver a los valores previos no recupera un análisis descartado. Un nuevo análisis fallido tampoco mantiene una recomendación anterior.

Los controles envían sus cambios al servidor mediante las interacciones habituales de Streamlit (por ejemplo, al salir del campo de texto). Se retiró `st.form` para detectar estos cambios sin esperar al envío del formulario. Solo **Analizar Candidato** ejecuta la extracción y la evaluación; las demás interacciones no repiten llamadas al modelo. La conservación es temporal: no garantiza recuperar resultados al cerrar o restablecer la sesión.

La ejecución con Docker se documentará y comprobará en la etapa 9.

## Verificación del entorno

Se comprobó `pip check` sin conflictos y la importación de Streamlit, PyPDF2, LangChain OpenAI, LangChain Core, Pydantic y pytest. Consulta el [registro de la etapa 2](docs/ENTORNO.md). Esta comprobación no valida todavía el análisis de CV ni el acceso a la API.

## Modelo y pruebas

`models/cv_model.py` define `AnalisisCV` con los ocho campos obligatorios del taller y valida que el porcentaje de ajuste esté entre 0 y 100. Conserva los nombres `education` y `experiencia_años` del contrato de referencia. Las listas contienen textos y no tienen restricciones adicionales de longitud.

Para ejecutar las pruebas desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

La etapa 3 se verificó con 17 pruebas satisfactorias de datos válidos, límites, campos ausentes y tipos de elementos de listas. No requieren credenciales ni llamadas a OpenAI.

## Extracción de PDF

`services/pdf_processor.py` implementa `extraer_texto_pdf(archivo_pdf)`: acepta bytes o un archivo binario abierto (como UploadedFile de Streamlit), extrae texto en memoria y separa páginas con dos saltos de línea. No cierra el archivo recibido ni realiza OCR.

Los documentos ilegibles, sin texto extraíble o protegidos generan `ErrorProcesamientoPDF`. La futura interfaz deberá capturar esa excepción, mostrar su mensaje y detener el flujo antes de evaluar. A diferencia de la referencia, los mensajes de error no se devuelven como si fueran texto extraído.

La etapa 4 añade 13 pruebas con PDF sintéticos generados en memoria: texto en varias páginas, páginas vacías, entrada como bytes, cursor al final, ausencia de texto, datos dañados, protección con contraseña y fallos de lectura. El conjunto completo suma **30 pruebas satisfactorias**. PyPDF2 emite un aviso de deprecación; se conserva la dependencia indicada en el taller.

## Prompts de evaluación

`prompts/cv_prompts.py` ofrece `crear_sistema_prompts()`, una `ChatPromptTemplate` con dos variables: `texto_cv` y `descripcion_puesto`. Las instrucciones del reclutador ocupan un mensaje de sistema fijo y los documentos se insertan en un mensaje humano separado.

La plantilla orienta el ajuste con los pesos del taller: experiencia 40 %, habilidades técnicas 35 %, formación/certificaciones 15 % y coherencia profesional 10 %. Solicita evidencia profesional, diferencia datos no acreditados de carencias demostradas y ordena tratar las instrucciones incrustadas en documentos como datos. Esta separación no garantiza por sí sola resistencia a instrucciones maliciosas; las pruebas actuales verifican la construcción de mensajes, no el comportamiento de un modelo real.

Para nombre y formación ausentes se indica `No especificado`. Las listas de habilidades y fortalezas pueden quedar vacías. Como el contrato exige un entero, si los años no pueden determinarse se utiliza `0` como marcador, acompañado de una aclaración en `experiencia_relevante`; no debe interpretarse aisladamente como ausencia de experiencia. La futura interfaz deberá mostrar esa aclaración junto al dato.

La etapa 5 añade 7 pruebas de roles, variables obligatorias, texto literal (incluidas llaves y etiquetas) y reutilización sin retener documentos. **37 pruebas totales pasaron**, sin credenciales ni llamadas a OpenAI. La calidad de las evaluaciones reales queda pendiente de la integración.

## Evaluador de candidatos

`services/cv_evaluator.py` expone:

- `crear_evaluador_cv()`: lee `OPENAI_API_KEY` y construye `chat_prompt | modelo_estructurado`. No realiza una solicitud por sí misma.
- `evaluar_candidato(texto_cv, descripcion_puesto)`: valida las entradas, invoca la cadena y devuelve `AnalisisCV`. Admite una cadena opcional mediante `evaluador=` para reutilización y pruebas.

Se mantiene `gpt-4o-mini` y temperatura 0.2 según el taller. Se configura `with_structured_output(AnalisisCV, method="json_schema", strict=True)`, tiempo de espera de 30 segundos por solicitud y un máximo de un reintento del cliente (no un límite global de duración). Se contrastó el enfoque con la [documentación oficial de OpenAI sobre salidas estructuradas](https://developers.openai.com/api/docs/guides/structured-outputs) y el adaptador instalado de LangChain. El acceso efectivo de una cuenta al modelo solo se confirma mediante una llamada real.

`ErrorConfiguracionCV` comunica falta de clave, fallos de configuración y acceso rechazado. `ErrorEvaluacionCV` comunica respuestas inválidas, cuota, conexión, tiempos de espera y otros fallos. La futura interfaz deberá capturar estos errores y detener el flujo; no se genera una puntuación alternativa. Las causas originales se conservan para diagnóstico; los mensajes destinados a la interfaz no incluyen la respuesta original ni credenciales.

La etapa 6 añade 21 pruebas, incluidas solicitudes y respuestas HTTP simuladas que recorren el adaptador real de LangChain/OpenAI. **58 pruebas totales pasaron**. No se hizo tráfico hacia OpenAI ni se comprobó cuota, acceso real o calidad de evaluaciones; esa validación queda para la etapa 10. Permanece el aviso de deprecación de PyPDF2.

## Verificación de la interfaz

La etapa 7 añade 22 casos para las dos escalas y el flujo de interfaz con Streamlit AppTest. Se verificaron entradas ausentes, vacante con espacios, presentación del perfil y aclaración de años indeterminados, PDF inválido con el extractor real, fallos de configuración/API y el aviso de Guardar. El recorrido satisfactorio usa extracción y evaluación simuladas; los servicios se prueban también por separado. **80 pruebas totales pasaron**.

Además, se inició temporalmente el servidor en `127.0.0.1:18501`: `/_stcore/health` respondió `200 / ok` y la página principal respondió HTTP 200. Se detuvo al terminar. Esta comprobación y AppTest no sustituyen una revisión visual de navegador ni una evaluación real con OpenAI, ambas pendientes de la validación final.

La etapa 8 añade 8 casos de AppTest: conservación tras reruns y Guardar, invalidación por nueva vacante, cambio de contenido del PDF con el mismo nombre o retirada del archivo, ausencia de recuperación de análisis descartados, limpieza y nueva carga, fallos de reevaluación y aislamiento de sesiones. **88 pruebas totales pasaron**, sin llamadas reales a OpenAI. Permanece el aviso de deprecación de PyPDF2.
