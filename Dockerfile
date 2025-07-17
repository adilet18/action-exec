# syntax=docker/dockerfile:1
FROM python:3.9-alpine AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

FROM python:3.9-alpine
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY app ./app
COPY pyproject.toml .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 