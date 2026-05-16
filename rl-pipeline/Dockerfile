FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY rl_pipeline ./rl_pipeline
COPY tests ./tests

RUN uv pip install --system -e ".[dev]"

EXPOSE 8001

CMD ["python", "-c", "from rl_pipeline.health import health_check; print(health_check())"]
