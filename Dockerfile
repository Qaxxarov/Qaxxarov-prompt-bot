FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs reports data/memory data/monitor data/competitors data/trends data/alerts data/ab_tests data/competitor_monitor

ENV PYTHONUNBUFFERED=1
ENV HEADLESS=1

EXPOSE 8000

CMD ["sh", "-c", "python run.py --both --port ${PORT:-8000}"]
