# Production-oriented image skeleton for StellarHydra API and workers.
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY config ./config
COPY src ./src

RUN pip install --upgrade pip && pip install .

EXPOSE 8090

CMD ["uvicorn", "stellarhydra.api.main:app", "--host", "0.0.0.0", "--port", "8090"]
