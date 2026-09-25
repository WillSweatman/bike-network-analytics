FROM python:3.13-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY README.md ./
COPY src/ src/
COPY data/raw/ data/raw/
COPY models/ models/

RUN uv sync --no-dev

EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync uvicorn bike_network_analytics.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
