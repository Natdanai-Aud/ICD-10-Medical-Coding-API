FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Runtime tools: poppler + tesseract are used by the offline importer,
# curl by the container healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-tha \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD curl -fsS http://127.0.0.1:8000/v1/health/live || exit 1

CMD ["uvicorn", "icd10.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
