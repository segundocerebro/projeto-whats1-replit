# Dockerfile Multi-stage para Cloud Run
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser
COPY --from=builder /app /home/appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8080
ENV PORT 8080
CMD ["gunicorn", "-w", "3", "--preload", "--bind", "0.0.0.0:$PORT", "main:app"]
