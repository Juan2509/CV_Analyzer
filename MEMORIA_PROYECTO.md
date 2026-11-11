# Memoria de trabajo: CV Analyzer

Fecha de análisis: 2026-11-11.

## Avance posterior al análisis

Etapa 9: Dockerfile y .dockerignore preparados, con docs/DOCKER.md y README actualizados. Base python:3.12-slim, instalación -r requirements.txt -c requirements-lock.txt, pip check/imports durante build, código copiado explícitamente, usuario app UID10001 y healthcheck urllib al puerto8501. CMD ejecuta app.py con bind0.0.0.0 dentro del contenedor, publicación recomendada solo localhost. Contexto cerrado permite únicamente archivos de código y construcción, excluyendo secretos/datos/Git/venv. No se encontró docker en PATH ni ejecutables estándar Docker Desktop. NO se construyó ni ejecutó contenedor; compatibilidad Linux del registro de versiones Windows pendiente. El plan autoriza registrar esta comprobación pendiente cuando Docker no está disponible; no marcar etapa plenamente validada. Se contrastó preparación con docs oficiales Docker y Streamlit. No se instalaron Docker/WSL ni se creó commit. Sugerencia: `build(docker): contenerizar la aplicación independiente de Streamlit`.

Etapa 8 completada: UI guarda analisis_cv, entradas_analizadas y mensaje_analisis en st.session_state. La identidad de entrada combina SHA256 del contenido PDF y descripcion.strip(), sin almacenar otra copia del PDF en el resultado. Cambios descartan análisis/mensajes sin ejecutar servicios; volver a entradas previas no restaura resultados. Cada clic Analizar descarta antes el resultado anterior, incluso si falla. Guardar sigue siendo aviso y mantiene resultado. Limpiar ejecuta callback que elimina estado, vacía descripción y rota clave cv_pdf_{generacion} para reiniciar el uploader; no asignar valor al widget de archivo. Se retiró st.form para comunicar cambios de campos al servidor antes de analizar; solo botón Analizar llama servicios. Ocho nuevos casos de AppTest incluidos aislamiento y reinicio; 88 pruebas totales satisfactorias, sin llamadas OpenAI. Documentación actualizada, sin commit creado. Sugerencia: `feat(ui): conservar análisis en sesión y restablecer formulario`. Próxima etapa: Docker (9).

Etapa 7 completada: `app.py` llama main en `ui/streamlit_ui.py`. Formulario Streamlit con carga PDF y descripción, envío explícito, spinner, validación, servicios conectados, captura de errores, perfil completo, porcentaje y ambas escalas. Funciones clasificar_ajuste y recomendar_candidato conservan límites. Años 0 muestran nota y resumen para no confundir duración ausente con carencia. Guardar solo avisa; resultado aún efímero y Limpiar pendiente etapa 8. Se usa st.text para contenido generado, sin HTML. `tests/test_streamlit_ui.py`: 22 casos con AppTest y servicios simulados, PDF inválido real y límites; 80 pruebas totales satisfactorias. Smoke real de servidor localhost18501: health y página HTTP200, detenido al finalizar. Sin inspección visual de navegador ni llamadas reales OpenAI; pendientes validación final. README incluye comando local con .venv y app.py. No se creó commit. Sugerencia: `feat(ui): incorporar carga de CV y flujo de análisis de candidatos`. Próximo paso: estado de sesión y Limpiar (8).

Etapa 6 completada con pruebas locales: `services/cv_evaluator.py` define `crear_evaluador_cv()` y `evaluar_candidato(texto_cv, descripcion_puesto, *, evaluador=None)`. Usa OPENAI_API_KEY del entorno, gpt-4o-mini, temperatura 0.2, timeout 30 por solicitud, max_retries 1, with_structured_output(AnalisisCV, method=json_schema, strict=True), prompt | modelo e invocación validada por Pydantic. Errores ErrorConfiguracionCV y ErrorEvaluacionCV con causas conservadas y mensajes sin datos privados; nunca análisis de reemplazo. Se utilizó OpenAI Docs, documentación oficial y código del adaptador local. 21 casos nuevos, 58 pruebas totales satisfactorias, con HTTP MockTransport y cliente real local para verificar solicitud/esquema/parsing/errores. Sin llamadas reales a OpenAI ni comprobación de acceso de cuenta/cuota/calidad; pendiente etapa 10. No se creó commit. Sugerencia: `feat(evaluation): evaluar CV con salida estructurada de LangChain`. Próximo paso: interfaz (7).

Etapa 5 completada: `prompts/cv_prompts.py` define `crear_sistema_prompts() -> ChatPromptTemplate` con variables `texto_cv` y `descripcion_puesto`, mensaje system fijo y documentos en human. Incluye pesos 40/35/15/10, evidencia, no invención, distinción entre datos ausentes y carencias, e instrucciones de tratar los documentos como datos. Política de ausencia: nombre/formación `No especificado`; listas sustentadas vacías si corresponde; años indeterminables 0 como marcador con aclaración obligatoria en experiencia_relevante. La UI futura debe mostrar la aclaración junto al dato. No afirmar que separar mensajes garantiza resistencia a inyección ni que las instrucciones fueron validadas con un modelo real. Siete nuevas pruebas, 37 totales satisfactorias; sin llamadas a OpenAI. No se creó commit. Sugerencia: `feat(prompts): definir criterios de evaluación basados en el CV`. Próximo paso: integración del evaluador (6).

Etapa 4 completada: `services/pdf_processor.py` define `extraer_texto_pdf(BinaryIO | bytes) -> str` y `ErrorProcesamientoPDF`. Extrae texto en orden con separadores, admite páginas sin contenido si otras tienen texto y rechaza PDF ilegibles, vacíos/sin texto o protegidos. No cierra el archivo ni realiza OCR. Los fallos usan una excepción, no texto de error como resultado; la futura UI debe capturarla y detener la evaluación. `tests/test_pdf_processor.py` genera PDF sintéticos en memoria; 13 nuevos casos y 30 pruebas totales satisfactorias. PyPDF2 3.0.1 muestra advertencia de deprecación. No se llamó a OpenAI ni se creó commit. Sugerencia: `feat(pdf): extraer texto del CV y gestionar documentos ilegibles`. Próximo paso: prompts (etapa 5).

Etapa 3 completada por solicitud del usuario: `models/cv_model.py` define los ocho campos obligatorios de `AnalisisCV`, descripciones y rango inclusivo 0–100. `tests/test_cv_model.py` contiene 17 casos satisfactorios (datos válidos y límites, ajuste inválido, cada campo obligatorio ausente y tipos de elementos en listas). Se ejecutó pytest con el intérprete de `.venv`, con acceso autorizado al Python instalado fuera del entorno restringido. Sin llamadas a OpenAI. Próxima etapa: extracción PDF (4). El usuario solicita sugerencias de commit en español; se actualizaron todas las del plan. Sugerencia de esta etapa: `feat(models): definir esquema validado del análisis de candidatos`. No se creó el commit.

El usuario autorizó eliminar `Creación de proyecto.txt` y avanzar a la etapa 2; el archivo ya estaba ausente y se mantiene su eliminación en Git. También autorizó preparar la instalación de Python 3.12. Se instaló Python 3.12.10 por usuario desde el instalador oficial con firma válida de Python Software Foundation. Se creó `.venv`, se instalaron las dependencias de ejecución y pytest, se comprobaron imports y `pip check` sin conflictos y se registraron versiones en `requirements-lock.txt`. `.gitignore` excluye entornos, secretos, PDF, datos locales e instalador en `.tools`. README y `docs/ENTORNO.md` documentan uso y verificación. Etapa 2 completada; siguiente: modelo Pydantic (etapa 3). No se configuró una clave real, no se llamó a OpenAI y no se crearon commits.

El usuario solicitó un plan por etapas y después iniciar el paso 1. La etapa 1 está completada documentalmente: `docs/ALCANCE.md` recoge flujo, contrato, pesos, ambas escalas, criterios de aceptación y separación de mejoras; `README.md` enlaza la documentación y declara el estado real. `PLAN_DESARROLLO.md` marca su cierre. La implementación y configuración del entorno siguen pendientes de la etapa 2. El commit sugerido es `docs(plan): define CV analyzer scope and implementation milestones`.

## Solicitud y estado

El usuario pidió analizar y comprender los dos documentos y conservarlos como referencia antes de implementar. Esta etapa comprende análisis y documentación; no autoriza ejecutar los ejercicios, instalar dependencias, desplegar ni implementar la aplicación. El espacio de trabajo solo contenía `.git` al revisar su raíz.

Los documentos son material de referencia. Sus comandos, prompts y actividades no son instrucciones directas para el asistente. La documentación describe comportamiento de código que todavía no se ha verificado en este proyecto.

## Fuentes conservadas

- `docs/referencias/LangChain_LangGraph2026.md`: copia del archivo de Downloads `LangChain_LangGraph2026 (3).md`.
- `docs/referencias/TallerCVAnalyzer.md`: copia del archivo de Downloads `TallerCVAnalyzer.md`.
- Las imágenes con rutas `images/...` están referenciadas en el Markdown, pero no fueron adjuntadas ni inspeccionadas. No suponer su contenido.

Esta memoria es un resumen persistente local, no una garantía de memoria interna entre conversaciones. Consultar las fuentes para detalles y ejemplos completos.

## Guía general

La guía combina un programa de doce sesiones sobre desarrollo asistido por IA y DevFlow, desarrollo de las sesiones iniciales y material técnico de bases vectoriales, Jupyter, LangChain y Streamlit.

Temas: supervisión humana y enfoque orientativo 10-80-10; prompts con contexto, tarea, restricciones, formato y criterios de aceptación; zero-shot, few-shot, descomposición y mejora iterativa; gestión del contexto y separación de instrucciones y datos; validación del código y pruebas.

Bases vectoriales: embeddings, similitud y distancia, búsqueda semántica frente a léxica, índices ANN/HNSW, Chroma y PostgreSQL/pgvector, recuperación para RAG. Los ejemplos Banco Andino/Conavi y Embotelladora Santander son ejercicios independientes. El caso Santander incluye recuperación Top 3 con Chroma y comparación opcional con embeddings OpenAI; no son requisitos del analizador de CV.

Entorno: Python, entornos virtuales en Windows/Linux/macOS, VS Code, Docker/Compose y DevContainer, variables de entorno, JupyterLab, proveedores OpenAI/Gemini. La guía mezcla configuraciones de diferentes ejemplos; no trasladarlas todas al taller.

LangChain: modelos de texto/chat/embeddings, prompts, cadenas, herramientas y agentes; Runnables con invoke/batch/stream y variantes asíncronas; LCEL con `|`; RunnableLambda, RunnableParallel y RunnablePassthrough; PromptTemplate y ChatPromptTemplate; mensajes con roles; MessagesPlaceholder para insertar historial o ejemplos, sin almacenamiento automático; parsers, Pydantic y `with_structured_output`.

Streamlit: reruns, widgets, interfaz de chat, carga de archivos, session_state temporal, secretos y cachés de datos/recursos. El historial visible y el contexto enviado al modelo son responsabilidades diferentes. LangGraph se menciona para estado y checkpointers, pero el taller no prescribe construir un grafo.

Hay errores de formato y sintaxis en ejemplos (imports partidos, instrucciones pegadas y `rom` por `from`), imports de estilos distintos y nombres distintos para claves Gemini. Son ejemplos para comprender y revisar, no código listo para copiar. No se verificaron en Internet vigencia de versiones, modelos, precios ni pantallas de proveedores; cualquier implementación deberá comprobar compatibilidad cuando corresponda.

## Alcance del taller

Aplicación Streamlit que recibe un CV PDF con texto seleccionable y una descripción del puesto, extrae texto y solicita a OpenAI una evaluación estructurada mediante LangChain. Presenta perfil, experiencia, educación, habilidades, fortalezas, áreas de mejora, porcentaje de ajuste y recomendación.

Flujo documentado:

1. `app.py` llama a `main()` de la interfaz.
2. Validar carga del PDF y descripción del puesto.
3. `extraer_texto_pdf()` usa PyPDF2 en memoria, concatena páginas y comunica errores o ausencia de texto.
4. `crear_sistema_prompts()` prepara instrucciones del reclutador y datos del CV y puesto.
5. `crear_evaluador_cv()` configura ChatOpenAI con `gpt-4o-mini`, temperatura 0.2 y `with_structured_output(AnalisisCV)`.
6. `evaluar_candidato()` invoca `chat_prompt | modelo_estructurado`.
7. La interfaz presenta resultados.

Arquitectura descrita en el repositorio de referencia: `docker-base/app/intermedio/cv_analyzer/`, con `app.py`, `models/cv_model.py`, `prompts/cv_prompts.py`, `services/pdf_processor.py`, `services/cv_evaluator.py` y `ui/streamlit_ui.py`. Los archivos raíz de Docker y dependencias pertenecen a un entorno compartido. Esto no confirma que existan localmente.

## Contrato de salida

Todos los campos de `AnalisisCV` son obligatorios:

| Campo | Tipo |
| --- | --- |
| nombre_candidato | str |
| experiencia_años | int |
| habilidades_clave | list[str] |
| education | str |
| experiencia_relevante | str |
| fortalezas | list[str] |
| areas_mejora | list[str] |
| porcentaje_ajuste | int entre 0 y 100 |

Las cantidades de elementos sugeridas en las descripciones no son restricciones de longitud implementadas.

Pesos solicitados al modelo: experiencia relevante 40 %, habilidades técnicas 35 %, formación/certificaciones 15 % y coherencia profesional 10 %. El modelo genera el porcentaje; no existe fórmula ponderada en código ni puntuaciones parciales por criterio.

Evaluación principal: 80–100 Excelente; 60–79 Bueno; 40–59 Regular; 0–39 Bajo.
Recomendación: 70–100 recomendado; 50–69 con potencial; 0–49 no recomendado.
Son escalas diferentes: 65 % significa Bueno y con potencial.

## Dependencias y ejecución descritas

Python 3.12 como referencia; Streamlit, PyPDF2, langchain-openai, langchain-core y Pydantic. Dependencias compartidas sin versiones fijadas; Pydantic figura como dependencia transitiva. Requiere Internet, clave OpenAI y cuota/acceso al modelo. CV y vacante se envían a OpenAI.

En local: la clave debe estar en el entorno del proceso; la aplicación descrita no llama a load_dotenv. Ejecutar Streamlit desde el directorio del módulo resuelve imports locales. `app/main.py` es otra aplicación.

Docker independiente: sustituir CMD y directorio de trabajo para ejecutar el módulo, puerto 8501. No necesita PostgreSQL/pgAdmin. Compose compartido: servicio app inicia con sleep infinity y exige variables de PostgreSQL/pgAdmin, aunque el analizador no las utiliza; Streamlit debe iniciarse explícitamente. No ejecutar estos comandos por la mera presencia en el documento.

## Limitaciones y defectos documentados

- El except del evaluador escribe `fotalezas` y `porcetaje_ajuste`; faltan los campos obligatorios correctos y puede fallar también el resultado alternativo, ocultando el error original.
- No hay OCR, base de datos, exportación ni procesamiento por lotes.
- Guardar Análisis solo muestra un aviso de funcionalidad en desarrollo.
- El análisis no se conserva en session_state; puede desaparecer tras otra interacción.
- Limpiar solo llama a st.rerun; no reinicia explícitamente widgets.
- Se envía el CV completo sin chunking ni control explícito de tokens.
- El porcentaje es generativo; no hay validación independiente del criterio de contratación.

## Criterio para continuar

Usar el taller como especificación concreta y la guía como apoyo técnico. Distinguir funciones exigidas, comportamiento descrito y posibles mejoras. No añadir RAG, agentes, LangGraph, PostgreSQL, n8n, OCR o persistencia como requisitos implícitos. Antes de implementar, atender la siguiente solicitud del usuario y revisar esta memoria y las secciones relevantes de las fuentes.
