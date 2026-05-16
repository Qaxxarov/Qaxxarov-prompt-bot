# 🏗 AGRO AI — Arxitektura

## Loyiha Tuzilmasi

```
instagram_analyzer/
├── app/                          # Asosiy dastur
│   ├── __init__.py
│   ├── settings.py               # Markaziy konfiguratsiya
│   ├── accounts.py               # Multi-account tizimi
│   ├── startup.py                # Startup validatsiya va diagnostika
│   │
│   ├── ai/                       # AI Engine modullari
│   │   ├── __init__.py
│   │   ├── base.py               # BaseAIEngine — barcha AI uchun asos
│   │   ├── hooks.py              # Viral Hook Engine
│   │   ├── storytelling.py       # Storytelling Engine
│   │   ├── scripts.py            # Scriptwriter Engine
│   │   ├── captions.py           # Caption Generator
│   │   ├── veo.py                # Veo Prompt Generator
│   │   ├── trends.py             # Trend Radar
│   │   ├── viral_score.py        # Viral Score Analyzer
│   │   ├── audience.py           # Audience Psychology
│   │   ├── competitor.py         # Competitor Intelligence
│   │   ├── growth.py             # Growth Advisor
│   │   ├── sales.py              # Sales AI
│   │   └── planner.py            # Content Calendar
│   │
│   ├── scraper/                  # Instagram scraping
│   │   ├── __init__.py
│   │   ├── browser.py            # Chrome WebDriver
│   │   ├── profile_manager.py    # Chrome profil boshqaruvi
│   │   ├── instagram.py          # Instagram scraper
│   │   └── models.py             # ReelData, ProfileData
│   │
│   ├── analytics/                # Tahlil tizimi
│   │   ├── __init__.py
│   │   ├── analyzer.py           # ReelsAnalyzer
│   │   └── formatters.py         # Telegram uchun formatlash
│   │
│   ├── export/                   # Hisobot yaratish
│   │   ├── __init__.py
│   │   ├── excel.py
│   │   ├── json_export.py
│   │   └── pdf.py
│   │
│   └── bot/                      # Telegram bot
│       ├── __init__.py
│       ├── main.py               # Entry point
│       ├── keyboards.py          # Barcha klaviaturalar
│       ├── middleware.py         # Auth, logging, error handling
│       ├── session.py            # User session management
│       ├── handlers/             # Handler modullari
│       │   ├── __init__.py
│       │   ├── start.py          # /start, /help
│       │   ├── tahlil.py         # 📊 TAHLIL
│       │   ├── goyalar.py        # 💡 G'OYALAR
│       │   ├── hooklar.py        # 🎣 HOOKLAR
│       │   ├── ssenariy.py       # ✍️ SSENARIY
│       │   ├── veo.py            # 🎞 VEO PROMPTLAR
│       │   ├── reja.py           # 📅 REJA
│       │   ├── trendlar.py       # 📡 TRENDLAR
│       │   ├── sotuv.py          # 📦 SOTUV AI
│       │   ├── audience.py       # 🧠 AUDIENCE AI
│       │   ├── viral_score.py    # 🏆 VIRAL SCORE
│       │   ├── osish.py          # 📈 O'SISH
│       │   ├── konkurent.py      # 🎯 KONKURENT
│       │   ├── export.py         # 📤 EXPORT
│       │   ├── sozlamalar.py     # ⚙️ SOZLAMALAR
│       │   └── admin.py          # 👑 ADMIN PANEL
│       └── router.py             # Callback routing
│
├── data/                         # Ma'lumotlar
│   ├── accounts.json             # Multi-account konfiguratsiya
│   └── sessions/                 # Foydalanuvchi sessiyalari
│
├── reports/                      # Eksport fayllar
├── logs/                         # Log fayllar
│
├── .env                          # Muhit o'zgaruvchilari
├── requirements.txt
├── run.py                        # Yagona entry point
├── ARCHITECTURE.md               # Shu fayl
├── ROADMAP.md
└── PROJECT_STATE.md
```

## Asosiy Tamoyillar

1. **Modularity** — Har bir AI feature alohida modul
2. **Multi-account** — accounts.json orqali bir nechta brand
3. **Separation of Concerns** — Bot UI / AI Logic / Scraping / Export alohida
4. **Dependency Injection** — Modullar bir-birini to'g'ridan-to'g'ri import qilmaydi
5. **Error Isolation** — Bitta modul xatosi butun tizimni to'xtatmaydi
6. **Config Validation** — Startup'da barcha sozlamalar tekshiriladi
7. **Dashboard-Ready** — API qatlami keyinchalik FastAPI bilan ulanadi

## Multi-Account Tizimi

```json
// data/accounts.json
{
  "accounts": [
    {
      "id": "agro_uruglar",
      "instagram": "@agro_uruglar_",
      "niche": "Qishloq xo'jaligi — urug'lar",
      "chrome_profile": "Profile 3",
      "ai_personality": "Professional agro ekspert",
      "target_audience": "Fermerlar, issiqxona egalari",
      "active": true
    }
  ],
  "default_account": "agro_uruglar"
}
```

## AI Engine Pattern

```python
class BaseAIEngine:
    """Barcha AI modullar uchun asos."""
    
    def __init__(self, account: Account):
        self.account = account
    
    async def generate(self, task: str, context: dict = None) -> str:
        """AI javob yaratish."""
        ...
    
    def get_system_prompt(self) -> str:
        """Account-specific system prompt."""
        ...
```
