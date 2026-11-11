# Entorno de desarrollo: etapa 2

Preparación comprobada el 2026-11-11 en Windows de 64 bits.

## Instalación

Se instaló Python 3.12.10 para el usuario, con pip y configuración del PATH, usando el [instalador oficial de Python](https://www.python.org/downloads/release/python-31210/). Antes de ejecutarlo se comprobó su firma Authenticode: estado `Valid`, editor Python Software Foundation.

Intérprete utilizado: `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`. El entorno aislado del proyecto está en `.venv/`. El instalador descargado está en `.tools/`; ambas carpetas están excluidas de Git. Puede ser necesario abrir otra terminal para cargar el PATH actualizado.

## Dependencias comprobadas

| Paquete | Versión instalada |
| --- | --- |
| streamlit | 1.67.0 |
| PyPDF2 | 3.0.1 |
| langchain-openai | 1.7.4 |
| langchain-core | 1.8.0 |
| pydantic | 2.14.3 |
| pytest | 9.2.0 |

`requirements.txt` declara las dependencias directas de ejecución; `requirements-dev.txt` agrega pytest. `requirements-lock.txt` contiene el resultado de `pip freeze`, incluidas dependencias transitivas del entorno de desarrollo. Su resolución fue comprobada en esta plataforma; la ejecución en Docker se validará en la etapa 9.

## Resultados de comprobación

- Entorno creado con Python 3.12.10 e instalación de dependencias finalizada correctamente.
- `python -m pip check`: `No broken requirements found.`
- Imports de los seis paquetes de la tabla: correctos.
- Imports de `ChatOpenAI`, `ChatPromptTemplate`, `BaseModel` y `Field`: correctos.
- `git check-ignore`: excluye `.venv/`, `.tools/`, `.env`, secretos Streamlit, PDF, entradas y resultados locales.
- `Creación de proyecto.txt` no existe en el directorio; Git registra la eliminación autorizada por el usuario.

No se configuró una clave real, no se llamó a la API ni se ejecutaron pruebas de funcionalidades todavía inexistentes. La compatibilidad comprobada corresponde a dependencias e imports, no al flujo completo del analizador.

Las instrucciones para reproducir el entorno y definir `OPENAI_API_KEY` están en el [README](../README.md). No es necesario compartir la clave para completar la siguiente etapa del modelo Pydantic.
