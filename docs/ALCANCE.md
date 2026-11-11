# Alcance y criterios de aceptación

Estado: definición documental completada; aplicación pendiente de implementación.

## Fuentes y prioridad

La especificación funcional procede de [TallerCVAnalyzer.md](referencias/TallerCVAnalyzer.md). La [guía LangChain/LangGraph](referencias/LangChain_LangGraph2026.md) aporta conceptos y ejemplos de apoyo. Sus ejercicios independientes y comandos no son tareas adicionales de este proyecto. Las imágenes enlazadas con rutas `images/...` no se proporcionaron.

El taller describe una aplicación de referencia, incluidos sus defectos. Este documento distingue su funcionalidad de las decisiones de implementación y las mejoras propuestas. No se ha comprobado código de esa aplicación: el repositorio actual contiene documentación.

## Objetivo

Permitir que una persona cargue un CV en PDF con texto seleccionable, introduzca una descripción de puesto y reciba un análisis estructurado del ajuste del candidato. La evaluación será una estimación generada para apoyar la revisión humana.

## Flujo y responsabilidades

1. `app.py` llama a `main()` de la interfaz de Streamlit.
2. La interfaz recibe un PDF y el texto de la vacante, y comprueba ambas entradas al pulsar **Analizar Candidato**.
3. `extraer_texto_pdf()` lee las páginas en memoria mediante PyPDF2 y concatena el texto con separadores. Un fallo de lectura o ausencia de texto detiene el flujo antes de evaluar.
4. `crear_sistema_prompts()` prepara las instrucciones del reclutador y los datos del CV y la vacante mediante mensajes separados.
5. `crear_evaluador_cv()` configura ChatOpenAI y la salida estructurada con `AnalisisCV`.
6. `evaluar_candidato()` invoca `chat_prompt | modelo_estructurado`.
7. La interfaz presenta perfil, habilidades, fortalezas, áreas de mejora, porcentaje, evaluación principal y recomendación final.

La configuración descrita en el taller es `gpt-4o-mini` con temperatura `0.2`. Su disponibilidad y compatibilidad se comprobarán al implementar. Los textos del CV y del puesto se envían a OpenAI; la interfaz deberá comunicarlo.

## Contrato del análisis

Todos los campos son obligatorios y sus nombres se conservan para mantener correspondencia con el taller.

| Campo | Tipo | Significado |
| --- | --- | --- |
| `nombre_candidato` | `str` | Nombre extraído del documento |
| `experiencia_años` | `int` | Años de experiencia relevante |
| `habilidades_clave` | `list[str]` | Habilidades relacionadas con la vacante |
| `education` | `str` | Formación y especialización |
| `experiencia_relevante` | `str` | Resumen de experiencia aplicable |
| `fortalezas` | `list[str]` | Fortalezas identificadas |
| `areas_mejora` | `list[str]` | Áreas de desarrollo |
| `porcentaje_ajuste` | `int` | Valor entre 0 y 100, inclusive |

Las cantidades de elementos sugeridas en descripciones no se convierten en restricciones de longitud. El taller no define cómo representar todos los datos ausentes; esa política se concretará al construir los prompts, evitando inventar antecedentes.

## Criterios y escalas

| Criterio solicitado en el prompt | Peso |
| --- | --- |
| Experiencia relevante | 40 % |
| Habilidades técnicas | 35 % |
| Formación y certificaciones | 15 % |
| Coherencia profesional | 10 % |

El modelo estima el porcentaje. El alcance no incluye calcular una fórmula ponderada independiente ni devolver puntuaciones parciales por criterio.

| Rango | Evaluación principal |
| --- | --- |
| 80–100 | Excelente |
| 60–79 | Bueno |
| 40–59 | Regular |
| 0–39 | Bajo |

| Rango | Recomendación final |
| --- | --- |
| 70–100 | Candidato recomendado |
| 50–69 | Candidato con potencial |
| 0–49 | Candidato no recomendado |

Ambas escalas se muestran por separado: 65 % significa **Bueno** y **Candidato con potencial**.

## Criterios verificables de la entrega

| ID | Caso | Resultado esperado | Etapa del plan |
| --- | --- | --- | --- |
| AC01 | Falta PDF o vacante, o la vacante solo contiene espacios | Mensaje comprensible; no llamar al modelo | 7 |
| AC02 | PDF válido con texto en varias páginas | Extraer texto en orden y separar páginas | 4 |
| AC03 | PDF dañado o sin texto extraíble | Informar el problema y detener la evaluación | 4 y 7 |
| AC04 | Resultado estructurado válido | Aceptar los ocho campos y mostrarlos | 3, 6 y 7 |
| AC05 | Campo obligatorio ausente o porcentaje fuera de 0–100 | Rechazar el resultado mediante validación | 3 y 6 |
| AC06 | Vacante y CV válidos | Construir el prompt con ambos textos y los cuatro pesos | 5 |
| AC07 | Falta de clave o fallo de API | Informar un fallo técnico sin fabricar una evaluación | 6 y 7 |
| AC08 | Porcentajes en límites de categoría | Respetar ambas escalas, incluidos 0 y 100 | 7 |
| AC09 | Ajuste de 65 % | Mostrar Bueno y Candidato con potencial | 7 |
| AC10 | Usuario inicia el análisis | Comunicar que CV y vacante se envían a OpenAI | 7 |
| AC11 | Se incluye Guardar Análisis | Mostrar aviso de funcionalidad en desarrollo | 7 |
| AC12 | Ejecución local y contenedor independiente | Iniciar la aplicación documentada sin requerir base de datos | 9 y 10 |

Estos criterios son condiciones de aceptación futuras, no pruebas ya ejecutadas. La validación final usará datos sintéticos; las pruebas del evaluador simularán la API y se distinguirán de la prueba real con credenciales configuradas.

## Decisiones para implementar la referencia

- Usar la raíz de este repositorio y separar `models`, `prompts`, `services` y `ui`. La ruta `docker-base/app/intermedio/cv_analyzer/` pertenece al repositorio de ejercicios descrito en la fuente.
- Tomar Python 3.12 como referencia y declarar directamente las dependencias utilizadas. Las versiones compatibles se comprobarán en la etapa 2.
- Leer `OPENAI_API_KEY` del entorno del proceso. No asumir carga automática de `.env`.
- No reproducir los errores `fotalezas` y `porcetaje_ajuste` del manejo de excepciones documentado. Un error técnico no equivale a un candidato con ajuste cero.
- Mantener credenciales y CV personales fuera del control de versiones.

## Mejoras recomendadas separadas del alcance base

La etapa 8 propone conservar el análisis durante la sesión y hacer que **Limpiar** reinicie los widgets y resultados. Son mejoras sobre el comportamiento de referencia, que solo utiliza `st.rerun()` y no conserva el análisis en `st.session_state`.

Si se implementan, se comprobará que las interacciones no repitan llamadas a la API, que un resultado anterior no se confunda con entradas nuevas y que la limpieza reinicie el formulario. El estado de sesión no constituye almacenamiento duradero.

## Fuera de alcance

OCR, múltiples CV por operación, exportación, almacenamiento duradero, base de datos, puntuaciones parciales, cálculo determinista del ajuste, segmentación y control explícito de tokens, RAG, agentes, LangGraph y n8n. PostgreSQL y pgAdmin pertenecen al entorno compartido de la referencia y no son necesarios para este módulo.

Los resultados pueden variar y la validación del esquema no demuestra que las conclusiones del modelo sean correctas. No se promete una validación independiente de la decisión de contratación.

## Cierre de la etapa 1

Se contrastaron flujo, campos, pesos, escalas, configuración y limitaciones con el texto completo del taller. Las referencias originales se conservaron como Markdown. La siguiente etapa es preparar el entorno y las dependencias; todavía no se instalaron paquetes ni se creó código de aplicación.
