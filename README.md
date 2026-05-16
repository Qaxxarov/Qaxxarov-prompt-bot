# 🌿 AGRO AI v3.0

Instagram kontent strategiyasi uchun AI-powered Telegram bot va web dashboard.

## Xususiyatlar

- 📊 Instagram Reels tahlili (Selenium scraping)
- 🤖 13+ AI engine (OpenAI GPT-4o-mini)
- 📸 Media → avtomatik kontent yaratish (Vision API)
- 🕵️ Raqobatchi real-time monitoring
- 🧪 A/B test tizimi (variant yaratish + tracking)
- 📅 Kontent kalendar (FullCalendar.js dashboard)
- 🔔 Proaktiv alertlar (follower milestone, viral reel, ER)
- 📦 Mahsulot katalog + sotuv AI
- 📮 Avtomatik posting tizimi (navbat + reminder)
- 🌐 Multi-language kontent (UZ/RU)
- 💬 DM auto-reply bazasi (FAQ + AI fallback)
- 📋 Ops Manager (morning/evening briefing, discipline)
- 📤 Export (Excel, JSON, PDF)
- 🖥 Web Dashboard + Telegram Mini App
- 👥 Foydalanuvchi boshqaruvi (admin/manager/viewer)
- 🧠 Memory tizimi (o'rganuvchi AI)

## Arxitektura

```
app/
├── ai/           # 13+ AI engine (BaseAIEngine)
├── bot/          # Telegram bot (router + handlers)
├── competitors/  # Raqobatchi monitoring
├── dashboard/    # FastAPI web dashboard
├── dm/           # DM auto-reply
├── export/       # PDF/Excel export
├── memory/       # Persistent memory
├── ops/          # Scheduler, alerts, watchdog
├── posting/      # Post scheduler + publisher
├── products/     # Mahsulot katalog
├── scraper/      # Selenium Instagram scraper
└── users/        # Foydalanuvchi boshqaruvi
```

## O'rnatish

```bash
# 1. Repo klonlash
git clone <repo-url>
cd instagram_analyzer

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Dependencies
pip install -r requirements.txt

# 4. Konfiguratsiya
cp .env.example .env
# .env faylni to'ldiring

# 5. Diagnostika
python run.py --check

# 6. Bot ishga tushirish
python run.py

# 7. Bot + Dashboard
python run.py --both
```

## Ishlatish

```bash
python run.py              # Faqat Telegram bot
python run.py --dashboard  # Faqat web dashboard
python run.py --both       # Bot + Dashboard birga
python run.py --check      # Diagnostika
```

## Docker

```bash
# Build
docker build -t agro-ai .

# Run
docker-compose up -d

# Logs
docker-compose logs -f
```

## Testlar

```bash
pytest tests/ -v
```

## Env Variables

`.env.example` ga qarang. Asosiy o'zgaruvchilar:

| O'zgaruvchi | Tavsif |
|-------------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (@BotFather) |
| `ALLOWED_USER_IDS` | Ruxsat berilgan Telegram ID'lar |
| `OPENAI_API_KEY` | OpenAI API kalit |
| `TARGET_PROFILE` | Instagram username (@ siz) |
| `CHROME_USER_DATA_DIR` | Chrome User Data papkasi |
| `DASHBOARD_PASSWORD` | Web dashboard paroli |

## Telegram Bot Buyruqlari

- `/start` — Botni ishga tushirish
- `/help` — Yordam
- `/status` — Tizim holati
- `/reset` — Sessiyani tozalash
- `/webapp` — Mini App ochish

## Texnologiyalar

- Python 3.11+
- python-telegram-bot 21.x
- OpenAI GPT-4o-mini (Vision API)
- FastAPI + Uvicorn
- Selenium + Chrome
- ReportLab (PDF)
- FullCalendar.js (Dashboard)

## Litsenziya

Private — faqat ichki foydalanish uchun.
