# Plan de desarrollo de CV Analyzer

## Objetivo y alcance

Construir por etapas una aplicación de Streamlit que compare un CV en PDF con una descripción de puesto mediante LangChain y OpenAI, y presente un análisis validado con Pydantic.

Este plan se basa en `docs/referencias/TallerCVAnalyzer.md`; la guía LangChain/LangGraph sirve como apoyo conceptual. El taller describe una aplicación de referencia y sus defectos: se implementarán sus funcionalidades sin reproducir deliberadamente esos errores.

La primera entrega incluye un CV por análisis, extracción de texto seleccionable, datos del candidato, fortalezas, áreas de mejora, porcentaje de ajuste y recomendación. No incluye OCR, procesamiento por lotes, almacenamiento duradero, exportación, RAG, agentes, LangGraph, n8n, PostgreSQL ni pgAdmin.

Los mensajes de commit propuestos usan Conventional Commits: `tipo(ámbito): descripción`. Las descripciones se escriben en español, según la preferencia del usuario; los tipos convencionales se mantienen. Cada etapa se cierra con su comprobación y su commit; no se crean commits automáticamente por haber redactado este plan.

## Organización propuesta

Como este repositorio está dedicado al analizador, se propone usar su raíz directamente, conservando la separación de responsabilidades del taller sin reproducir la ruta de un repositorio que contiene múltiples ejercicios.

```text
CV_Analyzer/
├── app.py
├── models/
│   ├── __init__.py
│   └── cv_model.py
├── prompts/
│   ├── __init__.py
│   └── cv_prompts.py
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py
│   └── cv_evaluator.py
├── ui/
│   ├── __init__.py
│   └── streamlit_ui.py
├── tests/
├── docs/
│   └── referencias/
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── .dockerignore
├── Dockerfile
├── README.md
├── MEMORIA_PROYECTO.md
└── PLAN_DESARROLLO.md
```

Crear cada archivo cuando corresponda a su etapa, evitando módulos vacíos que aparenten funcionalidades implementadas.

## Etapa 1. Documentar el alcance

**Estado:** completada. Ver [alcance y criterios de aceptación](docs/ALCANCE.md) y [README](README.md). Se revisó la correspondencia con el taller; las comprobaciones de funcionamiento quedan para las etapas de implementación.

**Trabajo:** conservar las referencias, la memoria y este plan. Registrar el flujo, las dos escalas de clasificación, el contrato de salida y las funciones fuera de alcance. Separar lo que exige el taller de las mejoras propuestas.

**Comprobación:** contrastar el plan con el taller. Las referencias Markdown contienen imágenes externas no adjuntadas; no tratarlas como archivos disponibles.

**Commit:** `docs(plan): definir alcance y etapas del analizador de CV`

## Etapa 2. Preparar el proyecto y el entorno

**Estado:** completada. Python 3.12.10 y `.venv` preparados, dependencias instaladas, imports correctos y `pip check` sin conflictos. Versiones en `requirements-lock.txt`; detalles en [registro del entorno](docs/ENTORNO.md). No se configuró una clave real ni se llamó a OpenAI.

**Trabajo:** crear `.gitignore`, dependencias de ejecución y desarrollo e instrucciones iniciales del entorno virtual. Usar Python 3.12 como referencia del taller. Declarar directamente Streamlit, PyPDF2, langchain-openai, langchain-core y Pydantic; incorporar pytest para las comprobaciones posteriores. Verificar compatibilidad y registrar versiones comprobadas al instalar. Configurar `OPENAI_API_KEY` en el entorno del proceso y excluir secretos, entornos virtuales, cachés y CV personales del repositorio.

**Decisión:** mantener la configuración por variable de entorno del taller. No prometer que un archivo `.env` se cargue automáticamente; añadirlo requeriría incorporar y documentar explícitamente ese comportamiento.

**Comprobación:** instalar en un entorno aislado, ejecutar `python -m pip check` y comprobar los imports. No llamar todavía al modelo.

**Commit:** `chore(setup): configurar dependencias y entorno de desarrollo`

## Etapa 3. Definir el modelo de análisis

**Estado:** completada. `AnalisisCV` implementado con los ocho campos obligatorios y ajuste entre 0 y 100. Las 17 pruebas de contrato pasaron; no se realizaron llamadas a OpenAI.

**Archivos:** `models/cv_model.py` y pruebas del esquema.

**Trabajo:** crear `AnalisisCV` con los campos obligatorios `nombre_candidato`, `experiencia_años`, `habilidades_clave`, `education`, `experiencia_relevante`, `fortalezas`, `areas_mejora` y `porcentaje_ajuste`. Mantener los nombres del taller y validar un ajuste entero entre 0 y 100. Describir los campos para orientar la salida estructurada. No convertir cantidades sugeridas de elementos en restricciones nuevas sin documentarlo.

**Comprobación:** aceptar un resultado válido y los límites 0/100; rechazar valores fuera del rango y campos obligatorios ausentes.

**Commit:** `feat(models): definir esquema validado del análisis de candidatos`

## Etapa 4. Implementar la extracción del PDF

**Estado:** completada. `extraer_texto_pdf()` procesa bytes o archivos binarios en memoria, separa páginas y comunica documentos inválidos, sin texto o protegidos mediante `ErrorProcesamientoPDF`. Se verificaron 13 casos nuevos y las 30 pruebas del proyecto pasaron. Se mantiene PyPDF2 por correspondencia con el taller; emite un aviso de deprecación.

**Archivos:** `services/pdf_processor.py` y pruebas de extracción.

**Trabajo:** implementar `extraer_texto_pdf()` con PyPDF2, leer el archivo en memoria, recorrer páginas y separar su texto. Gestionar páginas sin texto, documentos vacíos, PDF dañados y archivos que no pueden leerse. Comunicar el fallo de extracción de forma que la interfaz pueda detener el análisis; nunca enviar un mensaje de error al modelo como si fuera texto del candidato.

**Comprobación:** usar documentos sintéticos sin datos personales: PDF con texto en varias páginas, documento sin texto extraíble y archivo inválido. Verificar contenido y separación de páginas.

**Commit:** `feat(pdf): extraer texto del CV y gestionar documentos ilegibles`

## Etapa 5. Construir los prompts de evaluación

**Estado:** completada. `crear_sistema_prompts()` separa un mensaje de sistema fijo y un mensaje humano con `texto_cv` y `descripcion_puesto`. Incluye los cuatro pesos, evidencia profesional y tratamiento de datos ausentes. Las 7 nuevas pruebas verifican roles, variables, contenido literal y reutilización; 37 pruebas totales satisfactorias sin llamadas a OpenAI. La efectividad de las instrucciones sobre respuestas reales se comprobará al integrar el modelo.

**Archivos:** `prompts/cv_prompts.py`.

**Trabajo:** implementar `crear_sistema_prompts()` con ChatPromptTemplate. Separar instrucciones del reclutador y los datos del CV y la vacante. Incorporar los pesos del taller: experiencia 40 %, habilidades técnicas 35 %, formación/certificaciones 15 % y coherencia profesional 10 %. Pedir evidencia del CV, evitar inventar antecedentes y definir cómo expresar información ausente dentro del esquema. Tratar instrucciones incrustadas en el CV o la vacante como contenido a analizar.

**Comprobación:** construir los mensajes con datos sintéticos y comprobar variables y roles. Confirmar que están presentes ambos textos y los cuatro criterios. Esta comprobación no requiere una llamada a la API.

**Commit:** `feat(prompts): definir criterios de evaluación basados en el CV`

## Etapa 6. Integrar LangChain y OpenAI

**Estado:** completada con pruebas locales. `crear_evaluador_cv()` construye la cadena con `gpt-4o-mini`, temperatura 0.2 y salida JSON Schema estricta; `evaluar_candidato()` devuelve `AnalisisCV` o errores explícitos. Se verificaron 21 casos nuevos, incluidos transporte HTTP simulado con el adaptador real, validación, acceso, cuota, conexión, tiempo de espera y rechazo. Las 58 pruebas pasaron. La llamada real y el acceso de la cuenta se comprobarán en la integración final con credenciales configuradas.

**Archivos:** `services/cv_evaluator.py` y pruebas del evaluador.

**Trabajo:** implementar `crear_evaluador_cv()` con la configuración indicada en el taller (`gpt-4o-mini`, temperatura 0.2), sujeto a comprobar su disponibilidad y compatibilidad al implementar. Aplicar `with_structured_output(AnalisisCV)` y componer `chat_prompt | modelo_estructurado`. Implementar `evaluar_candidato()` y gestionar falta de configuración, fallo de API y respuesta inválida con mensajes comprensibles.

**Criterio:** un fallo técnico debe comunicarse como fallo; no fabricar un análisis con ajuste cero que parezca una evaluación real. Usar correctamente `fortalezas` y `porcentaje_ajuste`, evitando los errores tipográficos documentados.

**Comprobación:** simular el modelo para verificar el contrato y los errores sin consumir API. Reservar una prueba real para la integración final, cuando la credencial esté configurada.

**Commit:** `feat(evaluation): evaluar CV con salida estructurada de LangChain`

## Etapa 7. Construir la interfaz y conectar el flujo

**Estado:** completada. `app.py` y `ui/streamlit_ui.py` conectan formulario, extracción, evaluación y presentación. Se verificaron 22 casos nuevos (AppTest con servicios simulados, errores y límites de escalas), con 80 pruebas totales satisfactorias. El servidor se inició temporalmente en localhost y respondió HTTP 200 tanto en salud como en la página principal; después se detuvo. No se hizo una evaluación real ni una inspección visual de navegador. El estado de sesión y Limpiar siguen reservados a la etapa 8.

**Archivos:** `app.py` y `ui/streamlit_ui.py`.

**Trabajo:** crear el punto de entrada y `main()`, carga de PDF, descripción del puesto, botón Analizar Candidato e indicador de procesamiento. Validar ambas entradas y rechazar descripciones con solo espacios. Conectar extracción, evaluación y presentación. Mostrar el perfil, educación, experiencia, habilidades, fortalezas, áreas de mejora y porcentaje.

**Escalas que deben conservarse:**

| Uso | Rangos |
| --- | --- |
| Evaluación principal | 80–100 Excelente; 60–79 Bueno; 40–59 Regular; 0–39 Bajo |
| Recomendación final | 70–100 recomendado; 50–69 con potencial; 0–49 no recomendado |

Mostrar ambas etiquetas sin confundirlas: 65 % corresponde a Bueno y con potencial. Explicar en la interfaz que el resultado es una estimación generada como apoyo a la revisión humana y que CV/vacante se envían a OpenAI. Si se incluye Guardar Análisis, debe mostrar únicamente el aviso de funcionalidad en desarrollo del taller.

**Comprobación:** iniciar Streamlit, recorrer el flujo con un evaluador simulado y comprobar entradas faltantes, extracción fallida, evaluación fallida y resultado satisfactorio. Verificar los límites de ambas escalas con casos parametrizados.

**Commit:** `feat(ui): incorporar carga de CV y flujo de análisis de candidatos`

## Etapa 8. Mejorar el estado de la interfaz (recomendada)

**Estado:** completada. El análisis y sus mensajes se conservan en `st.session_state`, asociados al hash del PDF y la descripción normalizada. Los cambios invalidan resultados, un nuevo fallo descarta el análisis anterior y Limpiar reinicia widgets mediante callback y una nueva clave del uploader. Los controles están fuera de `st.form` para detectar cambios sin otro envío. Ocho casos nuevos y 88 pruebas totales satisfactorias; sin llamadas reales a OpenAI.

Esta etapa corrige limitaciones descritas en el taller y amplía su comportamiento de referencia; no es persistencia duradera.

**Trabajo:** conservar el resultado en `st.session_state` durante la sesión; asociarlo a las entradas utilizadas para no presentar un análisis anterior como si correspondiera a un CV o puesto nuevo. Hacer que Limpiar reinicie entradas, resultado y mensajes mediante mecanismos compatibles con los widgets de Streamlit. Evitar nuevas llamadas a la API por interacciones ajenas al botón de análisis.

**Comprobación:** el resultado permanece al interactuar con controles; un cambio de entradas invalida o identifica claramente el resultado anterior; Limpiar reinicia el formulario y no se vuelve a evaluar sin solicitud.

**Commit:** `feat(ui): conservar análisis en sesión y restablecer formulario`

## Etapa 9. Preparar la ejecución en Docker

**Archivos:** `Dockerfile`, `.dockerignore` y sección correspondiente del README.

**Trabajo:** crear un contenedor independiente basado en Python 3.12, apuntando directamente al `app.py` de este repositorio y al puerto 8501. Pasar la clave por el entorno, sin incluirla en la imagen. Excluir documentos personales, entorno virtual, Git y secretos del contexto de construcción. No incluir PostgreSQL/pgAdmin, que el analizador no utiliza. Compose puede añadirse posteriormente si aporta comodidad; no es necesario para ejecutar un solo servicio.

**Comprobación:** construir la imagen, arrancar el contenedor con la configuración externa y comprobar que se sirve la aplicación correcta. Si Docker no está disponible, registrar la comprobación pendiente, sin afirmar que se validó.

**Commit:** `build(docker): contenerizar la aplicación independiente de Streamlit`

## Etapa 10. Validar y documentar la entrega

**Trabajo:** ejecutar las pruebas existentes y completar comprobaciones de integración que falten. Hacer una prueba manual de extremo a extremo con un CV sintético y una vacante. Con una clave configurada, comprobar una llamada real y la presentación del objeto validado. Registrar las verificaciones realizadas y las pendientes.

**Casos de aceptación:**

- PDF con texto y vacante válida producen un análisis con los ocho campos y ajuste en rango.
- Faltan entradas, PDF inválido o PDF escaneado: se informa el problema y no se solicita una evaluación.
- Falla la API: se informa el fallo sin mostrar una recomendación ficticia.
- Ambas escalas respetan sus límites; un resultado de 65 % se representa correctamente.
- Si se implementó la etapa 8, los reruns conservan el resultado sin repetir llamadas y Limpiar reinicia el estado.
- No hay credenciales ni CV personales entre los archivos que se van a versionar.

**README final:** propósito, estructura, instalación en PowerShell, configuración de clave, ejecución local y Docker, ejemplo de vacante, flujo de uso, criterios y escalas, tratamiento de datos, limitaciones y resolución de problemas. Documentar que el porcentaje lo estima el modelo; el programa no calcula una fórmula ponderada independiente.

**Commits:** separar pruebas y documentación cuando haya cambios en ambos:

- `test(integration): cubrir casos de éxito y error del análisis`
- `docs(readme): documentar instalación, uso y limitaciones`

Si las pruebas detectan un defecto, corregirlo con un commit concreto, por ejemplo `fix(evaluation): comunicar errores de API sin generar resultados ficticios`. No crear commits de pruebas vacíos si la cobertura necesaria ya se incorporó en etapas previas.

## Forma de trabajar con los commits

1. Implementar una etapa y revisar su diferencia con `git diff`.
2. Ejecutar las comprobaciones correspondientes y resolver fallos.
3. Revisar `git status --short` y seleccionar solo los archivos de la etapa; no usar `git add .` sin revisar el contenido.
4. Crear el commit con el mensaje propuesto y avanzar a la siguiente etapa.

Los tipos sugeridos son `docs` para documentación, `chore` para preparación, `feat` para funcionalidades, `build` para contenedores, `test` para pruebas y `fix` para defectos existentes. Las pruebas pequeñas de una funcionalidad pueden acompañar su commit `feat`.

El usuario confirmó la eliminación de `Creación de proyecto.txt` al iniciar la etapa 2. El archivo ya no existe en el directorio; su eliminación registrada en Git forma parte de los cambios autorizados.

## Mejoras futuras fuera de esta entrega

Exportación y almacenamiento, OCR, análisis por lotes y control explícito de tamaño/tokens son propuestas para versiones posteriores. Cada una requiere definir alcance y criterios propios. La evaluación con RAG o un grafo no es necesaria para completar este taller.
