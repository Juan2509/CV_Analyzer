FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/home/app

WORKDIR /app

# Instala solo dependencias de ejecución, restringidas a las versiones registradas.
COPY requirements.txt requirements-lock.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt -c requirements-lock.txt \
    && python -m pip check \
    && python -c "import streamlit, PyPDF2, langchain_google_genai, langchain_core, pydantic" \
    && useradd --create-home --uid 10001 app

COPY app.py ./
COPY models/ ./models/
COPY prompts/ ./prompts/
COPY services/ ./services/
COPY ui/ ./ui/

USER app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).close()"

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
