FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

RUN apt-get update && apt-get install -y bash \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE ${APP_PORT}
