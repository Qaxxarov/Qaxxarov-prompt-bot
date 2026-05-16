"""
Config shim — root-level fayllar (browser.py, scraper.py, analyzer.py, reporter.py)
uchun app/settings.py dan re-export.
Bu fayl faqat backward compatibility uchun. Yangi kod app/settings.py ishlatsin.
"""

import sys
from pathlib import Path

# app/ ni path'ga qo'shish
sys.path.insert(0, str(Path(__file__).parent))

from app.settings import (
    CHROME_PROFILE_DIR,
    CHROME_USER_DATA_DIR,
    DELAY_MAX,
    DELAY_MIN,
    EXPORT_DIR,
    HEADLESS,
    INSTAGRAM_BASE_URL,
    MAX_REELS,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    TARGET_PROFILE,
    AI_ENABLED,
)

# reporter.py EXPORT_DIR ni str sifatida kutadi
EXPORT_DIR = str(EXPORT_DIR)

# scraper.py INSTAGRAM_REELS_URL ishlatadi
INSTAGRAM_REELS_URL = f"{INSTAGRAM_BASE_URL}/{TARGET_PROFILE}/reels/"
