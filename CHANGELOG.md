# Changelog

## v3.0 (2025-05-16)

### Tuzatilgan
- Eski v1 dublikat fayllar tozalandi
- CORS xavfsizlik tuzatildi
- Dashboard parol hashing
- API key leak oldini olindi
- Cross-platform scraping (Windows/Linux/Mac)
- Race condition (asyncio.Lock)
- PDF export bot'ga ulandi
- Dashboard auto-restart
- f-string backslash xatolari tuzatildi

### Yangi funksiyalar
- 📸 Media handler (video/rasm → kontent paket, Vision API)
- 🕵️ Competitor real-time monitoring (har 6 soatda)
- 🧪 A/B test tizimi (variant yaratish + tracking + scoring)
- 📄 Haftalik/oylik avtomatik PDF hisobot
- 📦 Mahsulot katalog + sotuv AI (real narx/stok)
- 📅 Kontent kalendar (FullCalendar.js dashboard)
- 🔔 Proaktiv alert tizimi (6 ta trigger)
- 🌐 Multi-language kontent (UZ/RU tarjima)
- 📮 Avtomatik posting tizimi (navbat + reminder)
- 💬 DM auto-reply bazasi (FAQ + AI fallback)
- 👥 Foydalanuvchi boshqaruvi (admin/manager/viewer rollar)
- ✅ Unit testlar (pytest)
- 📖 To'liq dokumentatsiya (README, CHANGELOG)
- 🐳 Multi-stage Dockerfile
- 📝 Log rotation + sensitive data masking

### Infratuzilma
- UserManager — rollar asosida auth
- AlertManager — proaktiv Telegram alertlar
- PostScheduler — post navbati
- ContentTranslator — multi-language AI
- DMAutoReply — FAQ matching + AI fallback
- Calendar API — CRUD endpoints
- SensitiveFilter — log masking
- RotatingFileHandler — log rotation

## v2.0

### Arxitektura
- Modular handler tizimi (register dekorator)
- 11 AI engine (BaseAIEngine)
- Multi-account boshqaruvi
- Memory tizimi (persistent JSON)
- Ops Manager (morning/evening briefing)
- Web Dashboard (FastAPI + Mini App)
- Callback router (section:action format)

### AI Engines
- Hooks, Storytelling, Veo, Audience
- Viral Score, Trends, Pipeline, Coach
- Hashtags, Hook Scorer, Competitor

## v1.0

- Asosiy Instagram scraping
- Oddiy Telegram bot
- Bitta akkaunt
