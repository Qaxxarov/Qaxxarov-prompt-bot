# 🚀 AGRO AI — Deployment Guide

## Lokal Ishga Tushirish (Windows)

```bash
cd instagram_analyzer
pip install -r requirements.txt

# .env faylini to'ldiring
# Keyin:
python run.py              # Faqat Telegram bot
python run.py --dashboard  # Faqat web dashboard
python run.py --both       # Bot + Dashboard birga
python run.py --check      # Diagnostika
```

## Docker Deployment

```bash
# Build
docker build -t agro-ai .

# Run
docker run -d \
  --name agro-ai \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  agro-ai

# Docker Compose
docker-compose up -d

# Loglar
docker logs -f agro-ai
```

## Cloud Deployment (VPS)

### 1. Server tayyorlash
```bash
apt update && apt install -y python3.11 python3-pip git
```

### 2. Loyihani yuklash
```bash
git clone <repo> /opt/agro-ai
cd /opt/agro-ai
pip install -r requirements.txt
```

### 3. Systemd service
```ini
# /etc/systemd/system/agro-ai.service
[Unit]
Description=Agro AI Bot + Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agro-ai
ExecStart=/usr/bin/python3 run.py --both --port 8000
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable agro-ai
systemctl start agro-ai
systemctl status agro-ai
```

### 4. Nginx reverse proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| TELEGRAM_BOT_TOKEN | ✅ | — | BotFather token |
| ALLOWED_USER_IDS | ❌ | all | Comma-separated |
| OPENAI_API_KEY | ❌ | — | AI features |
| OPENAI_MODEL | ❌ | gpt-4o-mini | AI model |
| CHROME_USER_DATA_DIR | ❌ | auto | Chrome path |
| CHROME_PROFILE_DIR | ❌ | Profile 3 | Chrome profile |
| TARGET_PROFILE | ✅ | — | Instagram username |
| MAX_REELS | ❌ | 20 | Scraping limit |
| HEADLESS | ❌ | 0 | 1 for server |
| DASHBOARD_PASSWORD | ❌ | agro2024 | Web login |
| DASHBOARD_PORT | ❌ | 8000 | Web port |
| EXPORT_DIR | ❌ | reports | Output folder |

## Monitoring

```bash
# Loglar
tail -f logs/app.log

# Bot holati
curl http://localhost:8000/api/ops/status

# Health check
curl http://localhost:8000/
```

## Backup

```bash
# Data backup
tar -czf backup_$(date +%Y%m%d).tar.gz data/ reports/ logs/
```
