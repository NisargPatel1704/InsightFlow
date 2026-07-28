# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# System dependencies (build tools not usually needed for these wheels,
# but kept minimal and removed in the same layer to keep the image small)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance \
    && useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Seed the demo database on first boot if it doesn't already exist, then
# start the app under gunicorn. Override CMD/entrypoint for custom deploys.
CMD ["sh", "-c", "test -f instance/insightflow.db || python seed.py --reset; gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 60 run:app"]
