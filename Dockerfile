# ═══════════════════════════════════════════════════
# AGRO AI v3.0 — Multi-stage Dockerfile
# ═══════════════════════════════════════════════════

# ── Build stage ──
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ──
FROM python:3.11-slim

# Chrome uchun kerakli paketlar
RUN apt-get update && apt-get install -y \
    wget gnupg2 curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Python dependencies from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Application code
COPY . .

# Kerakli papkalar
RUN mkdir -p data logs reports \
    data/memory data/monitor data/competitors \
    data/trends data/alerts data/ab_tests \
    data/competitor_monitor

# Environment
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=1
ENV CHROME_USER_DATA_DIR=/app/chrome_data
ENV CHROME_PROFILE_DIR=Default

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/overview', timeout=5)" || exit 1

EXPOSE 8000

# Default: bot + dashboard (PORT env variable bilan)
CMD ["sh", "-c", "python run.py --both --port ${PORT:-8000}"]
