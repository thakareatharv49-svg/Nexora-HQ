FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NEXORA_ENV=production \
    NEXORA_DB_PATH=/data/nexora-hq.sqlite3

WORKDIR /app

RUN groupadd --system --gid 10001 nexora \
    && useradd --system --uid 10001 --gid nexora --create-home nexora \
    && mkdir -p /data \
    && chown nexora:nexora /data

COPY requirements-prod.txt ./requirements-prod.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements-prod.txt

COPY --chown=nexora:nexora src ./src
COPY --chown=nexora:nexora apps/web ./apps/web

USER nexora
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)" || exit 1

CMD ["uvicorn", "src.nexora_hq.app:app", "--host", "0.0.0.0", "--port", "8000"]
