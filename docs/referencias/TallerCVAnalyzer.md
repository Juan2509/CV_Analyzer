# Analizador de currículums con IA

Aplicación de Streamlit que compara un currículum en PDF con la descripción de un puesto. Extrae el texto del documento, lo envía a un modelo de OpenAI mediante LangChain y muestra un análisis estructurado del candidato.

## Funcionalidades

- Carga de un CV en formato PDF con texto seleccionable.
- Entrada de requisitos y responsabilidades del puesto.
- Extracción de nombre, experiencia, educación y habilidades relevantes.
- Identificación de fortalezas y áreas de mejora.
- Estimación del porcentaje de ajuste al puesto, entre 0 y 100.
- Presentación de una recomendación de contratación según el resultado.

El módulo no utiliza una base de datos ni implementa persistencia o exportación de análisis. El botón **Guardar Análisis** solo muestra un aviso de funcionalidad en desarrollo.

## Funcionamiento

1. `app.py` llama a `main()` de la interfaz de Streamlit.
2. El usuario carga un PDF y escribe la descripción del puesto.
3. Al pulsar **Analizar Candidato**, la interfaz comprueba que existan ambas entradas.
4. `extraer_texto_pdf()` lee el archivo en memoria con `PyPDF2`, recorre sus páginas y concatena el texto con separadores de página. Si no encuentra texto o falla la lectura, devuelve un mensaje de error que la interfaz muestra antes de detener el proceso.
5. `crear_sistema_prompts()` combina las instrucciones del reclutador y el mensaje que contiene el CV y la descripción del puesto.
6. `crear_evaluador_cv()` configura `ChatOpenAI` con `model="gpt-4o-mini"` y `temperature=0.2`. Usa `with_structured_output(AnalisisCV)` para obtener una respuesta conforme al modelo Pydantic.
7. `evaluar_candidato()` invoca la cadena `chat_prompt | modelo_estructurado` y devuelve el análisis.
8. La interfaz muestra el porcentaje de ajuste, el perfil del candidato, las habilidades, las fortalezas, las áreas de desarrollo y la recomendación final.

El texto extraído del CV y la descripción del puesto se envían a OpenAI durante la evaluación.

### Criterios de evaluación

El prompt solicita los siguientes pesos:

| Criterio | Peso solicitado |
| --- | --- |
| Experiencia relevante | 40 % |
| Habilidades técnicas | 35 % |
| Formación y certificaciones | 15 % |
| Coherencia profesional | 10 % |

El porcentaje lo genera el modelo a partir de estas instrucciones; el código no calcula una fórmula ponderada ni devuelve puntuaciones parciales por criterio.

La interfaz utiliza dos conjuntos de umbrales:

| Porcentaje | Evaluación principal |
| --- | --- |
| 80–100 | Excelente |
| 60–79 | Bueno |
| 40–59 | Regular |
| 0–39 | Bajo |

| Porcentaje | Recomendación final |
| --- | --- |
| 70–100 | Candidato recomendado |
| 50–69 | Candidato con potencial |
| 0–49 | Candidato no recomendado |

Por ejemplo, un resultado de 65 % aparece como **Bueno** en la evaluación principal y como **Candidato con potencial** en la recomendación final.

## Estructura

```text
docker-base/
├── requirements.txt                 # Dependencias compartidas del repositorio
├── Dockerfile                       # Imagen base con Python 3.12 y dependencias
├── docker-compose.yml               # Entorno compartido: app, PostgreSQL y pgAdmin
└── app/intermedio/cv_analyzer/
    ├── README.md
    ├── app.py                       # Punto de entrada de Streamlit
    ├── models/
    │   └── cv_model.py              # Esquema Pydantic AnalisisCV
    ├── prompts/
    │   └── cv_prompts.py            # Instrucciones y plantilla de evaluación
    ├── services/
    │   ├── pdf_processor.py         # Extracción de texto del PDF
    │   └── cv_evaluator.py          # Configuración e invocación del modelo
    └── ui/
        └── streamlit_ui.py          # Entradas, validaciones y presentación
```

Los directorios `__pycache__`, si aparecen, contienen archivos generados por Python y no forman parte de la lógica de la aplicación.

### Modelo de salida

Todos los campos de `AnalisisCV` son obligatorios:

| Campo | Tipo | Contenido |
| --- | --- | --- |
| `nombre_candidato` | `str` | Nombre extraído del CV |
| `experiencia_años` | `int` | Años de experiencia relevante |
| `habilidades_clave` | `list[str]` | Habilidades relevantes para el puesto |
| `education` | `str` | Nivel educativo y especialización |
| `experiencia_relevante` | `str` | Resumen de experiencia relacionada |
| `fortalezas` | `list[str]` | Fortalezas del candidato |
| `areas_mejora` | `list[str]` | Áreas de desarrollo |
| `porcentaje_ajuste` | `int` | Ajuste al puesto, validado entre 0 y 100 |

Las cantidades sugeridas de habilidades, fortalezas y áreas de mejora se describen en el esquema, pero no tienen restricciones de longitud implementadas.

## Requisitos

- Python 3.12 como referencia del `Dockerfile` del repositorio.
- Una clave de API de OpenAI con acceso al modelo configurado y cuota disponible.
- Conexión a Internet para las llamadas al modelo.
- Un PDF con texto extraíble; no se implementa OCR para documentos escaneados.

Las dependencias usadas directamente son `streamlit`, `PyPDF2`, `langchain-openai`, `langchain-core` y `pydantic`. El archivo raíz `requirements.txt` contiene las dependencias compartidas del entorno; Pydantic se instala como dependencia transitiva de los paquetes de LangChain. Las versiones no están fijadas.

## Ejecución local

Los siguientes comandos se ejecutan desde la raíz `docker-base/`, salvo donde se indica el cambio de directorio.

### 1. Crear un entorno e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows PowerShell, activa el entorno con `.\.venv\Scripts\Activate.ps1`.

### 2. Configurar la clave de OpenAI

En macOS o Linux:

```bash
export OPENAI_API_KEY="tu_clave_de_openai"
```

En Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "tu_clave_de_openai"
```

Esta aplicación no llama a `load_dotenv()`: crear un archivo `.env` por sí solo no configura la ejecución local. La clave debe estar presente en el entorno del proceso que ejecuta Streamlit. No incluyas claves reales en archivos versionados.

### 3. Iniciar Streamlit

```bash
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

Abre <http://localhost:8501>. Ejecutar desde esta carpeta permite resolver los imports locales `ui`, `services`, `models` y `prompts`. El punto de entrada de este módulo es `app/intermedio/cv_analyzer/app.py`; `app/main.py` corresponde a otra aplicación del repositorio.

## Ejecución con Docker

### Contenedor independiente

Desde `docker-base/`, con `OPENAI_API_KEY` ya definida en la terminal:

```bash
docker build -t cv-analyzer .
docker run --rm -p 8501:8501 \
  -e OPENAI_API_KEY \
  -w /app/app/intermedio/cv_analyzer \
  cv-analyzer \
  python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Abre <http://localhost:8501>. El comando sustituye el `CMD` del `Dockerfile`, que por defecto apunta a `app/main.py`. Esta opción no necesita PostgreSQL ni pgAdmin.

### Entorno Docker Compose del repositorio

El archivo `docker-compose.yml` inicia un entorno de desarrollo compartido. El servicio `app` ejecuta `sleep infinity`, por lo que es necesario iniciar Streamlit de forma explícita.

Antes de levantarlo, configura el archivo `.env` de la raíz con:

- `OPENAI_API_KEY`.
- `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`.
- `PGADMIN_DEFAULT_EMAIL` y `PGADMIN_DEFAULT_PASSWORD`.
- `PGADMIN_SERVERS_JSON`, con la configuración JSON de servidores de pgAdmin esperada por Compose.

Las variables de PostgreSQL y pgAdmin son obligatorias para este Compose, aunque el analizador de CV no las utiliza. `POSTGRES_PORT` y `PGADMIN_PORT` son opcionales y tienen valores predeterminados de `5433` y `5050`, respectivamente.

```bash
docker compose up -d --build
docker compose exec -w /app/app/intermedio/cv_analyzer app \
  python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Abre <http://localhost:8501>. Compose inyecta las variables del `.env` raíz en el servicio `app` mediante `env_file`. Si modificas la clave después de crear el contenedor, recréalo para actualizar su entorno.

Para detener el entorno:

```bash
docker compose down
```

## Uso

1. Carga un CV en PDF con texto seleccionable.
2. Escribe el puesto, la experiencia requerida, las habilidades obligatorias y deseables y las responsabilidades.
3. Pulsa **Analizar Candidato** y espera la respuesta del modelo.
4. Revisa el perfil, las habilidades y las razones del ajuste junto con la recomendación final.

Ejemplo de descripción:

```text
Puesto: Desarrollador Python
Requisitos obligatorios: 3 años de experiencia, Python, APIs REST y PostgreSQL.
Deseables: Docker, pruebas automatizadas y experiencia con LangChain.
Responsabilidades: desarrollar servicios, integrar APIs y mantener pruebas.
```

## Limitaciones y problemas conocidos

- **Errores de evaluación:** el bloque `except` de `services/cv_evaluator.py` construye `AnalisisCV` con los nombres `fotalezas` y `porcetaje_ajuste`, en lugar de `fortalezas` y `porcentaje_ajuste`. Si falla la llamada a OpenAI o la validación de la respuesta, ese resultado alternativo también falla por campos obligatorios ausentes. El error original no se registra ni se muestra explícitamente desde ese bloque.
- **Sin OCR:** un PDF compuesto solo por imágenes no puede analizarse. Los errores de extracción se muestran en la interfaz.
- **Sin almacenamiento:** el resultado no se guarda en una base de datos ni se conserva en `st.session_state`; se muestra durante la ejecución que procesa el clic de análisis. Una nueva interacción puede hacer que desaparezca.
- **Botón Limpiar:** únicamente llama a `st.rerun()`; no borra explícitamente el estado de los widgets ni sus valores.
- **Sin procesamiento por lotes:** se carga y analiza un CV por operación.
- **Sin segmentación de documentos:** se envía el texto completo del CV en una sola invocación, sin control explícito de longitud ni de tokens.
- **Evaluación generativa:** el porcentaje y las observaciones proceden del modelo y pueden variar. La aplicación no implementa una validación independiente del criterio de contratación.

## Resolución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| No encuentra `streamlit` u otro paquete | Activa el entorno virtual e instala `requirements.txt` con el mismo intérprete utilizado para ejecutar la aplicación. |
| No encuentra `ui`, `services`, `models` o `prompts` | Ejecuta el comando desde `app/intermedio/cv_analyzer/`. |
| Falla el análisis o aparece un error de validación | Comprueba `OPENAI_API_KEY`, la conectividad, el acceso al modelo y la cuota de la API. Ten en cuenta el problema del bloque `except` descrito arriba. |
| El PDF aparece vacío o no puede procesarse | Utiliza un PDF con texto seleccionable y verifica que el archivo pueda abrirse correctamente. |
| Docker arranca otra aplicación | Utiliza el comando de ejecución de este README para sustituir el `CMD` predeterminado. |
| Compose exige variables de PostgreSQL o pgAdmin | Completa la configuración del Compose compartido o utiliza el contenedor independiente. |
| El puerto 8501 está ocupado | En local, usa otro `--server.port`; con Docker, cambia el puerto del host, por ejemplo `-p 8502:8501`. |
