# CV Analyzer

Aplicación de Streamlit que compara un currículum en PDF con una vacante utilizando LangChain y OpenAI.

## Objetivo y funcionamiento

Ayudar a revisar candidatos mediante su experiencia, formación, habilidades, fortalezas y áreas de mejora frente a un puesto. El resultado apoya la revisión humana; no sustituye la decisión del reclutador.

1. El usuario carga un PDF con texto seleccionable y escribe la vacante.
2. PyPDF2 extrae el texto de las páginas en memoria.
3. LangChain prepara mensajes separados para las instrucciones y los documentos.
4. `ChatOpenAI` utiliza `gpt-4o-mini`, temperatura `0.2` y salida estructurada con Pydantic.
5. La interfaz muestra el nombre, formación, años y resumen de experiencia, habilidades, fortalezas, áreas de mejora, porcentaje de ajuste y recomendación.

El prompt solicita estos pesos:

| Criterio | Peso |
| --- | --- |
| Experiencia relevante | 40 % |
| Habilidades técnicas | 35 % |
| Formación y certificaciones | 15 % |
| Coherencia profesional | 10 % |

El modelo estima un porcentaje entero entre 0 y 100. La aplicación valida su rango, pero no calcula una fórmula ponderada independiente ni puntuaciones parciales.

La **evaluación principal** utiliza 80–100: Excelente; 60–79: Bueno; 40–59: Regular; 0–39: Bajo. La **recomendación final** utiliza 70–100: Candidato recomendado; 50–69: Candidato con potencial; 0–49: Candidato no recomendado. Por ejemplo, 65 % corresponde a **Bueno** y **Candidato con potencial**.

## Requisitos

- Python 3.12 para ejecutar localmente.
- Clave de OpenAI con acceso al modelo y cuota disponible.
- Internet para la evaluación.
- PDF con texto seleccionable; no se realiza OCR.
- Docker con motor Linux, solo para la alternativa con contenedores.

Al pulsar **Analizar Candidato**, el texto del CV y de la vacante se envía a OpenAI. Las llamadas pueden consumir la cuota de la cuenta.

## Ejecución local en Windows PowerShell

Ejecuta los comandos desde la raíz del repositorio.

### 1. Crear el entorno

Comprueba Python y crea el entorno si todavía no existe:

```powershell
python --version
python -m venv .venv
```

Si Python no aparece en el PATH, abre una terminal nueva después de instalarlo. En una instalación habitual por usuario puedes usar:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
```

### 2. Instalar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

`requirements.txt` declara las dependencias de ejecución y `requirements-lock.txt` restringe las versiones registradas. Se usa el intérprete directamente: no necesitas activar el entorno ni modificar la política de PowerShell.

### 3. Configurar OpenAI

En la misma terminal que iniciará la aplicación:

```powershell
$env:OPENAI_API_KEY = "tu_clave_de_openai"
```

Sustituye el ejemplo por tu clave. La aplicación lee la variable del proceso y no carga automáticamente `.env`. No incluyas credenciales reales en el código ni en archivos versionados.

### 4. Iniciar Streamlit

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false
```

Abre <http://localhost:8501>. Detén el servidor con `Ctrl+C`. Si el puerto está ocupado, cambia `--server.port=8501` por otro valor.

## Ejecución con Docker

Esta alternativa no necesita el entorno Python local. Inicia Docker Desktop con contenedores Linux y comprueba el motor:

```powershell
docker version
docker info --format '{{.OSType}}'
```

El primer comando debe mostrar cliente y servidor; el segundo debe devolver `linux`.

### 1. Construir la imagen

Desde la raíz:

```powershell
docker build -t cv-analyzer:local .
```

El Dockerfile utiliza Python 3.12, instala las dependencias restringidas, comprueba imports y `pip check`, y ejecuta la aplicación sin privilegios de administrador. No requiere PostgreSQL, pgAdmin ni Docker Compose.

### 2. Iniciar el contenedor

Con `OPENAI_API_KEY` definida en esa terminal:

```powershell
docker run --rm --name cv-analyzer -p 127.0.0.1:8501:8501 -e OPENAI_API_KEY cv-analyzer:local
```

Abre <http://localhost:8501>. La clave se pasa al ejecutar y no se incorpora a la imagen. Para otro puerto del equipo, publica `-p 127.0.0.1:8502:8501` y abre <http://localhost:8502>.

### 3. Comprobar y detener

Desde otra terminal:

```powershell
docker inspect --format '{{.State.Health.Status}}' cv-analyzer
Invoke-WebRequest -Uri 'http://localhost:8501/_stcore/health' -UseBasicParsing
docker logs cv-analyzer
docker stop cv-analyzer
```

La salud puede tardar en pasar de `starting` a `healthy`. La consulta HTTP debe devolver estado 200 y contenido `ok`. Ajusta la URL si cambiaste el puerto. `--rm` elimina el contenedor al detenerlo; no se configura almacenamiento duradero.

## Uso

1. Carga el CV y escribe la vacante.
2. Pulsa **Analizar Candidato** y espera la respuesta.
3. Revisa el perfil, las evidencias y ambas clasificaciones.
4. Usa **Limpiar** para borrar entradas, resultado y mensajes.

Ejemplo de vacante:

```text
Puesto: Desarrollador Python
Obligatorios: 3 años de experiencia, Python, APIs REST y PostgreSQL.
Deseables: Docker y pruebas automatizadas.
Responsabilidades: desarrollar servicios, integrar APIs y mantener pruebas.
```

El resultado permanece temporalmente en la sesión. Cambiar el contenido del CV o la descripción descarta el análisis anterior sin llamar al modelo. Solo **Analizar Candidato** ejecuta una evaluación. Si falla, no se presenta una puntuación ficticia ni se conserva una recomendación anterior.

**Guardar Análisis** solo muestra un aviso de funcionalidad en desarrollo; no guarda ni exporta resultados.

## Estructura

```text
CV_Analyzer/
├── app.py                    # Punto de entrada de Streamlit
├── models/cv_model.py        # Contrato Pydantic del análisis
├── prompts/cv_prompts.py     # Instrucciones de evaluación
├── services/
│   ├── pdf_processor.py      # Extracción de texto en memoria
│   └── cv_evaluator.py       # Integración con LangChain y OpenAI
├── ui/streamlit_ui.py        # Interfaz, escalas y estado de sesión
├── tests/                   # Pruebas y generador de PDF sintéticos
├── requirements.txt         # Dependencias de ejecución
├── requirements-dev.txt     # Dependencias de desarrollo
├── requirements-lock.txt    # Versiones registradas
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

## Pruebas y validación

Instala las dependencias de desarrollo y ejecuta las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -m pytest -q
```

La última validación completó **94 pruebas satisfactorias**, con datos sintéticos y sin solicitudes reales a OpenAI. Incluye esquema, PDF, prompts, errores del evaluador, escalas, interfaz, sesión y recorrido completo con HTTP simulado. `pip check` no detectó conflictos. PyPDF2 emite un aviso de deprecación; se conserva la dependencia utilizada en el taller.

El servidor local respondió HTTP 200 en la página principal y en salud. La revisión visual en navegador no se completó. La construcción Docker se inició durante la validación, pero no se confirmó su finalización ni la ejecución del contenedor. La prueba real de acceso, cuota y calidad de respuesta de OpenAI también está pendiente.

## Limitaciones y datos locales

- Un CV por operación; sin OCR, procesamiento por lotes, exportación ni base de datos.
- El resultado es generativo y puede variar. Pydantic comprueba estructura y rango, no la exactitud de las conclusiones.
- Se envía el CV completo, sin segmentación ni control explícito de tokens.
- Separar instrucciones y documentos no garantiza por sí solo resistencia a instrucciones maliciosas.
- Nombre y formación ausentes se representan como `No especificado`. Los años indeterminables usan `0` y una aclaración en el resumen; ese valor no demuestra falta de experiencia.
- La sesión no garantiza recuperar resultados después de cerrarla o restablecerla.

`.gitignore` excluye `.venv`, cachés, `.env`, secretos Streamlit, PDF y datos locales en `data/`, `uploads/` y `outputs/`. `.dockerignore` limita el contexto a los archivos necesarios para ejecutar la aplicación.

## Resolución de problemas

| Problema | Qué revisar |
| --- | --- |
| No encuentra Python | Reabre la terminal o utiliza la ruta del intérprete instalado. |
| No encuentra un paquete | Instala dependencias con el mismo intérprete de `.venv` usado para Streamlit. |
| No encuentra módulos del proyecto | Ejecuta los comandos desde la raíz. |
| Falta `OPENAI_API_KEY` | Define la variable en la terminal de la aplicación o del contenedor. Crear `.env` no basta. |
| OpenAI rechaza el acceso o alcanza un límite | Comprueba clave, permisos del modelo y cuota. |
| PDF vacío, protegido o ilegible | Usa una copia válida sin contraseña y con texto seleccionable. |
| Respuesta inválida o tiempo de espera | Revisa la conexión y reintenta; no se genera una evaluación alternativa. |
| Docker no conecta con el motor | Inicia Docker Desktop y comprueba el servidor con `docker version`. |
| Puerto 8501 ocupado | Cambia el puerto local de Streamlit o el puerto del host publicado por Docker. |
