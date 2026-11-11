# Ejecución con Docker

## Estado de verificación

Archivos preparados el 2026-11-11. No se encontró el comando `docker` ni los ejecutables habituales de Docker Desktop en este equipo. Por tanto, **la imagen no se ha construido ni el contenedor se ha ejecutado**. La compatibilidad de las dependencias fijadas con la imagen Linux queda pendiente de esa construcción.

Antes de ejecutar los comandos siguientes, instala e inicia Docker con un motor de contenedores Linux. En Windows puedes seguir la [instalación oficial de Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/). Después abre una terminal nueva y comprueba:

```powershell
docker version
docker info --format '{{.OSType}}'
```

El primer comando debe mostrar cliente y servidor disponibles; el segundo debe devolver `linux`.

## Construir la imagen

Desde la raíz de CV_Analyzer:

```powershell
docker build -t cv-analyzer:local .
```

El Dockerfile usa Python 3.12 sobre una imagen Linux slim e instala solo `requirements.txt`, aplicando las restricciones de `requirements-lock.txt`. Ese registro procede de Windows: la construcción ejecuta `pip check` e imports básicos, pero aún no se ha comprobado en Linux. Si hay incompatibilidades, habrá que resolverlas y registrar la nueva verificación; no eliminar restricciones silenciosamente.

El código se copia después de instalar las dependencias para permitir reutilizar la capa de instalación cuando solo cambia la aplicación. El proceso de Streamlit se ejecuta con un usuario sin privilegios. No se requieren PostgreSQL, pgAdmin, Docker Compose ni un entorno `.venv` en el contenedor.

## Iniciar la aplicación

Configura `OPENAI_API_KEY` en el entorno de PowerShell, como explica el README, y después ejecuta:

```powershell
docker run --rm --name cv-analyzer -p 127.0.0.1:8501:8501 -e OPENAI_API_KEY cv-analyzer:local
```

Abre <http://localhost:8501>. La clave se recibe al iniciar el contenedor; no se incluye en el Dockerfile ni se necesita para construir la imagen. Si no está configurada, la interfaz puede abrirse, pero el evaluador mostrará un error al intentar analizar.

El puerto del host se publica solo en localhost. Si 8501 está ocupado, cambia únicamente el primer puerto, por ejemplo `-p 127.0.0.1:8502:8501`, y abre <http://localhost:8502>.

Desde otra terminal puedes detener el contenedor con:

```powershell
docker stop cv-analyzer
```

`--rm` elimina el contenedor al detenerlo. El análisis solo se conserva temporalmente en la sesión de Streamlit; no se configura ningún volumen de datos.

## Comprobar el arranque

Con el contenedor iniciado, desde otra terminal:

```powershell
docker inspect --format '{{.State.Health.Status}}' cv-analyzer
Invoke-WebRequest -Uri 'http://localhost:8501/_stcore/health' -UseBasicParsing
docker logs cv-analyzer
```

La comprobación interna consulta `/_stcore/health` cada 30 segundos y puede tardar en pasar de `starting` a `healthy`. La consulta HTTP debe devolver estado 200 y contenido `ok`. Si cambiaste el puerto del host, ajusta también la URL de esta comprobación.

Abrir la página y comprobar salud no valida una evaluación real: primero hay que confirmar la clave, el acceso al modelo y la cuota. Para revisar el flujo, utiliza un CV sintético con texto seleccionable y una vacante de prueba.

## Contexto de construcción

`.dockerignore` excluye todo por defecto y admite únicamente `app.py`, los módulos Python de `models`, `prompts`, `services` y `ui`, los archivos de dependencias de ejecución y los archivos de construcción. No envía `.git`, `.venv`, `.tools`, `.env`, secretos Streamlit, PDF, documentación, pruebas ni carpetas de datos y resultados locales. El Dockerfile también usa instrucciones COPY explícitas.

Si se incorpora un recurso de ejecución nuevo, habrá que incluirlo expresamente en el contexto y en el Dockerfile. Las credenciales se siguen suministrando al ejecutar, no al construir.

## Comprobaciones pendientes

- Construcción real y resolución de las dependencias sobre Linux.
- Arranque como usuario sin privilegios, salud del contenedor y apertura de la interfaz.
- Evaluación real con credenciales configuradas y datos sintéticos en la validación final.

Referencias usadas para preparar los archivos: [guía de Streamlit con Docker](https://docs.streamlit.io/deploy/tutorials/docker), [contexto de construcción y dockerignore](https://docs.docker.com/build/concepts/context/) y [referencia del Dockerfile](https://docs.docker.com/reference/dockerfile/).
