# CV Analyzer

Aplicación de Streamlit que compara un currículum en PDF con una vacante utilizando LangChain y Google Gemini.

## Objetivo y funcionamiento

Ayudar a revisar candidatos mediante su experiencia, formación, habilidades, fortalezas y áreas de mejora frente a un puesto. El resultado apoya la revisión humana; no sustituye la decisión del reclutador.

1. El usuario carga un PDF con texto seleccionable y escribe la vacante.
2. PyPDF2 extrae el texto de las páginas en memoria.
3. LangChain prepara mensajes separados para las instrucciones y los documentos.
4. `ChatGoogleGenerativeAI` utiliza `gemini-3.5-flash-lite`, los valores de muestreo del modelo y salida estructurada JSON Schema con Pydantic.
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

- Python 3.12 como versión de referencia; también se comprobó la instalación y el arranque en Linux con Python 3.14.4.
- Clave de Gemini con acceso al modelo y cuota disponible.
- Internet para la evaluación.
- PDF con texto seleccionable; no se realiza OCR.
- Docker con motor Linux, solo para la alternativa con contenedores.

Al pulsar **Analizar Candidato**, el texto del CV y de la vacante se envía a Google Gemini. Las llamadas pueden consumir la cuota de la cuenta.

## Ejecución local en Windows PowerShell

Estos pasos utilizan la integración actual con Gemini. Si la aplicación ya está abierta, detenla con `Ctrl+C` antes de actualizar las dependencias y vuelve a iniciarla al terminar.

### 1. Entrar en el proyecto

```powershell
cd C:\Users\lickn\Desktop\CV_Analyzer
```

Si clonaste o moviste el proyecto a otra ubicación, utiliza esa ruta. Ejecuta los pasos siguientes desde la raíz, donde está `app.py`.

### 2. Crear el entorno solo si no existe

Comprueba Python y crea el entorno si todavía no existe:

```powershell
python --version
python -m venv .venv
```

Si ya tienes la carpeta `.venv` preparada, omite su creación y continúa con la instalación de dependencias.

Si Python no aparece en el PATH, abre una terminal nueva después de instalarlo. En una instalación habitual por usuario puedes usar:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
```

### 3. Instalar o actualizar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

`requirements.txt` declara las dependencias de ejecución y `requirements-lock.txt` restringe las versiones registradas. Se usa el intérprete directamente: no necesitas activar el entorno ni modificar la política de PowerShell.

Ejecuta este paso también si utilizabas la versión anterior del proyecto: ahora se requieren `langchain-google-genai` y el SDK de Google.

### 4. Configurar la clave de Gemini

En la misma terminal que iniciará la aplicación:

```powershell
$env:GOOGLE_API_KEY = "tu_clave_de_gemini"
```

Obtén tu clave en [Google AI Studio](https://aistudio.google.com/apikey) y sustituye el valor de ejemplo. La aplicación lee `GOOGLE_API_KEY` y, si está vacía o ausente, utiliza `GEMINI_API_KEY`. Si ambas tienen valor, prevalece `GOOGLE_API_KEY`. No carga automáticamente `.env`. No incluyas credenciales reales en el código ni en archivos versionados.

La asignación con `$env:` corresponde a esa sesión de PowerShell. Si abres otra terminal para iniciar la aplicación, configura la clave nuevamente allí. Una clave de OpenAI no sirve para esta integración.

No es necesario definir un modelo para ejecutar la aplicación. Si quieres usar el predeterminado, continúa con el paso 5.

Para utilizar otro modelo disponible en tu cuenta, configura opcionalmente:

```powershell
$env:GEMINI_MODEL = "gemini-3.6-flash"
```

Sin esa variable se utiliza `gemini-3.5-flash-lite`. El acceso y la cuota dependen de tu cuenta. La integración usa Gemini Developer API, sin requerir configuración de Vertex AI.

### 5. Iniciar Streamlit

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false
```

Abre <http://localhost:8501>. Detén el servidor con `Ctrl+C`. Si el puerto está ocupado, cambia `--server.port=8501` por otro valor.

### 6. Realizar el análisis

Carga un CV en PDF con texto seleccionable, escribe la descripción de la vacante y pulsa **Analizar Candidato**. La primera evaluación real requiere una clave válida y cuota disponible en Gemini. Consulta la sección Uso para revisar el resultado y limpiar el formulario.

En las siguientes ejecuciones, basta con entrar en la carpeta, configurar la clave en esa terminal e iniciar Streamlit; reinstala dependencias cuando cambien los archivos `requirements`.

## Ejecución local en Linux

Ejecuta los siguientes comandos en Bash, una línea a la vez. Copia solamente el contenido de los bloques, sin el indicador de la terminal (`camper@...$`). Mantén abierta la terminal mientras uses la aplicación.

### 1. Entrar en el proyecto y comprobar Python

Si guardaste el proyecto en el Escritorio:

```bash
cd ~/Escritorio/CV_Analyzer
ls app.py requirements.txt requirements-lock.txt
python3 --version
```

Si está en otra carpeta, adapta el comando `cd`. El comando `ls` debe encontrar los tres archivos; de lo contrario, revisa la ubicación antes de continuar.

Python 3.12 es la versión de referencia. En este equipo Linux también se instaló el proyecto y se comprobó el arranque con Python 3.14.4. No necesitas instalar Python 3.12 si ya tienes ese entorno funcionando.

### 2. Crear el entorno virtual (solo la primera vez)

```bash
python3 -m venv .venv
./.venv/bin/python --version
./.venv/bin/python -m pip --version
```

Si utilizas un ejecutable específico, sustituye únicamente el primer comando por, por ejemplo, `python3.14 -m venv .venv`. Si ya tienes un `.venv` creado en Linux y los dos comandos de comprobación funcionan, omite su creación. Los entornos de Windows no se pueden reutilizar en Linux.

No necesitas activar el entorno: los siguientes pasos utilizan directamente `./.venv/bin/python`. No uses `sudo` para instalar paquetes dentro de `.venv`.

### 3. Instalar o actualizar las dependencias

```bash
./.venv/bin/python -m pip install -r requirements.txt -c requirements-lock.txt
./.venv/bin/python -m pip check
./.venv/bin/python -m streamlit --version
```

Espera a que termine la instalación antes de iniciar la aplicación. `Requirement already satisfied` significa que el paquete ya está instalado; no es un error. `pip check` debe terminar con `No broken requirements found`.

**No ejecutes `-m pip install ...` por separado:** `-m` es una opción de Python, no un comando de Bash. Copia la línea completa, empezando por `./.venv/bin/python`.

### 4. Configurar la API de Gemini

En la misma terminal donde iniciarás Streamlit:

```bash
export GOOGLE_API_KEY="tu_clave_de_gemini"
```

Sustituye el ejemplo por tu clave de [Google AI Studio](https://aistudio.google.com/apikey). La aplicación sigue usando la API de Gemini; instalar dependencias o cambiar el puerto no requiere cambiar de proveedor ni de clave.

Como alternativa puedes definir `GEMINI_API_KEY`; si ambas tienen valor, prevalece `GOOGLE_API_KEY`. `.env` no se carga automáticamente. Si abres otra terminal, vuelve a definir la variable allí. No publiques la clave ni la incluyas en archivos versionados.

Puedes comprobar que hay una clave configurada sin mostrarla:

```bash
./.venv/bin/python -c 'import os; print("Clave configurada" if (os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()) else "Falta configurar la clave")'
```

Esta comprobación solo verifica que la variable tiene contenido; no consulta su validez ni su cuota.

El modelo predeterminado es `gemini-3.5-flash-lite`. Solo si necesitas otro modelo disponible para tu cuenta, define `GEMINI_MODEL` antes de arrancar. Para volver al predeterminado:

```bash
unset GEMINI_MODEL
```

### 5. Iniciar y utilizar la aplicación

```bash
./.venv/bin/python -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false
```

Cuando aparezca la URL, abre <http://localhost:8501> en el navegador del mismo equipo. Que la terminal permanezca ocupada es normal: está ejecutando el servidor. Carga un CV en PDF con texto seleccionable, escribe la vacante y pulsa **Analizar Candidato**.

Para detener el servidor, pulsa `Ctrl+C` en esa terminal. Si cambiaste la clave o el modelo, detén el servidor y vuelve a iniciarlo para aplicar las variables nuevas.

### 6. Volver a ejecutar el programa

En una terminal nueva:

```bash
cd ~/Escritorio/CV_Analyzer
export GOOGLE_API_KEY="tu_clave_de_gemini"
./.venv/bin/python -m streamlit run app.py --server.port=8501 --browser.gatherUsageStats=false
```

Adapta la ruta si corresponde. No recrees `.venv` en cada ejecución. Repite la instalación de dependencias cuando cambien los archivos `requirements`.

### Si algo falla en Linux

**`-m: no se encontró la orden` o `No module named streamlit`**

Instala usando el mismo intérprete con el que ejecutarás Streamlit:

```bash
./.venv/bin/python -m pip install -r requirements.txt -c requirements-lock.txt
./.venv/bin/python -m pip check
./.venv/bin/python -m streamlit --version
```

**`python3.12: orden no encontrada`**

Comprueba el Python disponible y crea el entorno con ese ejecutable:

```bash
python3 --version
python3 -m venv .venv
```

Si ya creaste `.venv` con Python 3.14 y funciona, continúa con la instalación de dependencias; no necesitas recrearlo con 3.12.

**Falta Python, `venv` o aparece un error sobre `ensurepip` al crear el entorno**

En Ubuntu/Debian, instala Python y el soporte de entornos virtuales del sistema:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
python3 -m venv .venv
```

Después vuelve al paso 3. Si elegiste una versión específica de Python, necesitas el paquete `venv` correspondiente a esa versión, si tu distribución lo ofrece. En otras distribuciones utiliza su gestor de paquetes.

**`No module named pip` dentro de un entorno ya creado**

```bash
./.venv/bin/python -m ensurepip --upgrade
./.venv/bin/python -m pip install -r requirements.txt -c requirements-lock.txt
```

Si `ensurepip` tampoco está disponible, instala el soporte `venv` descrito arriba y vuelve a crear el entorno.

**`Port 8501 is not available`**

Ya hay un proceso usando ese puerto. Si es otra instancia de la aplicación, puedes abrir <http://localhost:8501> o detenerla con `Ctrl+C` en su terminal. Para iniciar otra instancia en un puerto diferente:

```bash
./.venv/bin/python -m streamlit run app.py --server.port=8502 --browser.gatherUsageStats=false
```

En ese caso abre **<http://localhost:8502>**. Para identificar quién ocupa el puerto original:

```bash
ss -ltnp 'sport = :8501'
```

Revisa el proceso antes de detenerlo; no cierres procesos desconocidos para liberar el puerto.

**No abre la página en el navegador**

Comprueba que la terminal del servidor sigue abierta y que estás usando el puerto indicado en su URL. Desde otra terminal, si tienes `curl` instalado:

```bash
curl --fail http://localhost:8501/_stcore/health
```

Debe responder `ok`; adapta el puerto si usas 8502. Esta comprobación verifica el servidor, no el acceso a Gemini.

**La página abre, pero falla el análisis con Gemini**

Comprueba la presencia de la variable con el comando del paso 4 y reinicia Streamlit desde esa misma terminal. Si el mensaje indica clave inválida, permisos, cuota o modelo no disponible, revisa esos datos en Google AI Studio. Reinstalar Streamlit o cambiar el puerto no corrige un rechazo de la API. Si definiste un modelo por error, ejecuta `unset GEMINI_MODEL` y reinicia.

**Errores de conexión durante `pip install`**

Comprueba la conexión a Internet y la configuración de proxy o DNS del equipo. Después repite el comando completo del paso 3. Si la instalación termina con `ERROR`, no continúes al arranque hasta resolver ese mensaje.

### Pruebas opcionales en Linux

No son necesarias para iniciar la aplicación:

```bash
./.venv/bin/python -m pip install -r requirements-dev.txt -c requirements-lock.txt
./.venv/bin/python -m pytest -q
```

Se comprobaron la instalación de dependencias, `pip check`, los imports de la aplicación y el arranque de Streamlit en Linux con Python 3.14.4. La evaluación real con Gemini requiere verificar por separado la clave, el acceso al modelo y la cuota.

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

Con `GOOGLE_API_KEY` definida en esa terminal:

```powershell
docker run --rm --name cv-analyzer -p 127.0.0.1:8501:8501 -e GOOGLE_API_KEY cv-analyzer:local
```

Abre <http://localhost:8501>. La clave se pasa al ejecutar y no se incorpora a la imagen. Si usas la variable alternativa, sustituye `-e GOOGLE_API_KEY` por `-e GEMINI_API_KEY`. Para cambiar el modelo, añade `-e GEMINI_MODEL` después de definirlo en PowerShell. Para otro puerto del equipo, publica `-p 127.0.0.1:8502:8501` y abre <http://localhost:8502>.

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
│   └── cv_evaluator.py       # Integración con LangChain y Gemini
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

La validación de la migración a Gemini completó **101 pruebas satisfactorias** y `pip check` sin conflictos. Las pruebas usan datos sintéticos y respuestas HTTP simuladas de Gemini; no requieren una clave real ni consumen cuota. Incluyen esquema, PDF, prompts, errores del evaluador, selección de clave y modelo, escalas, interfaz, sesión y recorrido completo. PyPDF2 emite un aviso de deprecación; se conserva la dependencia utilizada en el taller.

El servidor local respondió HTTP 200 en la página principal y en salud durante la implementación inicial. La revisión visual en navegador no se completó. La construcción Docker anterior no confirmó la ejecución del contenedor; tras cambiar a Gemini es necesario reconstruir la imagen. La prueba real de acceso, cuota y calidad de respuesta de Gemini también está pendiente.

Referencias de la integración: [ChatGoogleGenerativeAI en LangChain](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai) y [Gemini 3.5 Flash-Lite](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite).

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
| Falta `GOOGLE_API_KEY` o `GEMINI_API_KEY` | Define una de ellas en la terminal de la aplicación o del contenedor. Crear `.env` no basta. |
| Gemini rechaza el acceso o alcanza un límite | Comprueba clave, permisos del modelo y cuota en Google AI Studio. |
| Modelo no disponible | Revisa `GEMINI_MODEL` y utiliza un identificador accesible para tu cuenta. |
| PDF vacío, protegido o ilegible | Usa una copia válida sin contraseña y con texto seleccionable. |
| Respuesta inválida o tiempo de espera | Revisa la conexión y reintenta; no se genera una evaluación alternativa. |
| Docker no conecta con el motor | Inicia Docker Desktop y comprueba el servidor con `docker version`. |
| Puerto 8501 ocupado | Cambia el puerto local de Streamlit o el puerto del host publicado por Docker. |
