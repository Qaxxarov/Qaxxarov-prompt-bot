# 📋 AGRO AI — Loyiha Holati

## Umumiy Ma'lumot
- **Loyiha:** Agro Uruglar AI Content Operating System
- **Til:** Python 3.10+
- **Bot:** python-telegram-bot 21.9
- **AI:** OpenAI GPT-4o-mini
- **Scraping:** Selenium + Chrome Profile 3
- **Target:** @agro_uruglar_

## Joriy Holat
- Telegram bot ishlaydi (polling rejimda)
- Instagram scraping Chrome Profile 3 orqali
- AI g'oyalar, hooklar, ssenariylar yaratiladi
- Excel/JSON eksport ishlaydi
- Multi-account tizimi tayyor (accounts.json)

## Texnik Stack
| Komponent | Texnologiya |
|-----------|-------------|
| Bot | python-telegram-bot 21.9 |
| AI | OpenAI API (gpt-4o-mini) |
| Scraping | Selenium 4.27 + webdriver-manager |
| Data | pandas + openpyxl |
| Export | JSON, Excel, PDF (reportlab) |
| Config | python-dotenv + JSON |
| Logging | Python logging + Rich |

## Ishga Tushirish
```bash
cd instagram_analyzer
pip install -r requirements.txt
# .env faylini to'ldiring
python run.py
```

## Muhim Fayllar
- `run.py` — Yagona entry point
- `.env` — Muhit o'zgaruvchilari
- `data/accounts.json` — Multi-account config
- `app/settings.py` — Markaziy konfiguratsiya
