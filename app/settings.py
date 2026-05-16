"""
Agro AI v3.0 — Markaziy Konfiguratsiya
Barcha sozlamalar shu yerdan boshqariladi.
"""

import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# ── Loyiha ildiz papkasi ──
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ════════════════════════════════════════════════════════
# 📝 LOGGING (Rotation + Sensitive Data Masking)
# ════════════════════════════════════════════════════════

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


class SensitiveFilter(logging.Filter):
    """API key, token va boshqa maxfiy ma'lumotlarni maskalash."""

    _patterns = [
        (re.compile(r'sk-[a-zA-Z0-9]{20,}'), 'sk-***MASKED***'),
        (re.compile(r'\d{9,10}:[a-zA-Z0-9_-]{35}'), '***BOT_TOKEN***'),
        (re.compile(r'eyJ[a-zA-Z0-9_-]{20,}\.eyJ[a-zA-Z0-9_-]{20,}'), '***JWT_TOKEN***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            for pattern, replacement in self._patterns:
                record.msg = pattern.sub(replacement, record.msg)
        if record.args:
            args = list(record.args) if isinstance(record.args, tuple) else [record.args]
            new_args = []
            for arg in args:
                if isinstance(arg, str):
                    for pattern, replacement in self._patterns:
                        arg = pattern.sub(replacement, arg)
                new_args.append(arg)
            record.args = tuple(new_args)
        return True


# Log formatter
_log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# File handler — RotatingFileHandler (max 5MB, 5 backup)
_file_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8",
)
_file_handler.setFormatter(logging.Formatter(_log_format))
_file_handler.addFilter(SensitiveFilter())

# Console handler
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter(_log_format))
_console_handler.addFilter(SensitiveFilter())

logging.basicConfig(
    level=logging.INFO,
    format=_log_format,
    handlers=[_file_handler, _console_handler],
)
logger = logging.getLogger("agro_ai")

# ════════════════════════════════════════════════════════
# 🤖 TELEGRAM
# ════════════════════════════════════════════════════════

TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

ADMIN_IDS: List[int] = []
_admin_raw = os.environ.get("ALLOWED_USER_IDS", "").strip()
if _admin_raw:
    for uid in _admin_raw.split(","):
        uid = uid.strip()
        if uid.isdigit():
            ADMIN_IDS.append(int(uid))

# ════════════════════════════════════════════════════════
# 🌐 CHROME
# ════════════════════════════════════════════════════════

def _default_chrome_user_data() -> str:
    """OS ga qarab default Chrome User Data yo'li."""
    import platform
    system = platform.system()
    home = Path.home()
    if system == "Windows":
        return str(home / "AppData" / "Local" / "Google" / "Chrome" / "User Data")
    elif system == "Darwin":  # macOS
        return str(home / "Library" / "Application Support" / "Google" / "Chrome")
    else:  # Linux
        return str(home / ".config" / "google-chrome")


CHROME_USER_DATA_DIR: str = os.environ.get(
    "CHROME_USER_DATA_DIR",
    _default_chrome_user_data(),
).strip()

CHROME_PROFILE_DIR: str = os.environ.get("CHROME_PROFILE_DIR", "Profile 3").strip()

# ════════════════════════════════════════════════════════
# 🎯 INSTAGRAM
# ════════════════════════════════════════════════════════

TARGET_PROFILE: str = os.environ.get("TARGET_PROFILE", "agro_uruglar_").strip().lstrip("@")
INSTAGRAM_BASE_URL: str = "https://www.instagram.com"

# ════════════════════════════════════════════════════════
# 🤖 AI
# ════════════════════════════════════════════════════════

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
AI_ENABLED: bool = bool(OPENAI_API_KEY)

# ════════════════════════════════════════════════════════
# ⚙️ SCRAPING
# ════════════════════════════════════════════════════════

MAX_REELS: int = int(os.environ.get("MAX_REELS", "20"))
DELAY_MIN: float = float(os.environ.get("DELAY_MIN", "2"))
DELAY_MAX: float = float(os.environ.get("DELAY_MAX", "5"))
HEADLESS: bool = os.environ.get("HEADLESS", "0") == "1"
SCRAPE_TIMEOUT: int = int(os.environ.get("SCRAPE_TIMEOUT_SEC", "300"))

# ════════════════════════════════════════════════════════
# 📁 PATHS
# ════════════════════════════════════════════════════════

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EXPORT_DIR = BASE_DIR / os.environ.get("EXPORT_DIR", "reports")
EXPORT_DIR.mkdir(exist_ok=True)

ACCOUNTS_FILE = DATA_DIR / "accounts.json"

# Telegram Mini App URL (public HTTPS URL)
WEBAPP_URL: str = os.environ.get("WEBAPP_URL", "").strip()

# ════════════════════════════════════════════════════════
# 🔍 DIAGNOSTIKA
# ════════════════════════════════════════════════════════

def validate() -> List[str]:
    """Startup validatsiya — muammolarni qaytaradi."""
    issues: List[str] = []

    if not TELEGRAM_BOT_TOKEN:
        issues.append("TELEGRAM_BOT_TOKEN o'rnatilmagan")

    # HEADLESS=1 bo'lganda Chrome profil tekshirmaslik (Docker/Railway)
    if not HEADLESS:
        if not os.path.isdir(CHROME_USER_DATA_DIR):
            issues.append(f"CHROME_USER_DATA_DIR topilmadi: {CHROME_USER_DATA_DIR}")

        profile_path = Path(CHROME_USER_DATA_DIR) / CHROME_PROFILE_DIR
        if not profile_path.is_dir():
            issues.append(f"Chrome profil topilmadi: {profile_path}")

    if not TARGET_PROFILE:
        issues.append("TARGET_PROFILE o'rnatilmagan")

    if not AI_ENABLED:
        issues.append("OPENAI_API_KEY o'rnatilmagan (AI o'chirilgan)")

    return issues


def print_status() -> None:
    """Startup holat chiqishi."""
    issues = validate()
    ai_status = f"✅ {OPENAI_MODEL}" if AI_ENABLED else "❌ o'chirilgan"
    logger.info("═" * 50)
    logger.info("  🌿 AGRO AI v3.0 — Konfiguratsiya")
    logger.info("═" * 50)
    logger.info(f"  Target:  @{TARGET_PROFILE}")
    logger.info(f"  Profil:  {CHROME_PROFILE_DIR}")
    logger.info(f"  AI:      {ai_status}")
    logger.info(f"  Admins:  {len(ADMIN_IDS)} ta")
    logger.info(f"  Reels:   max {MAX_REELS}")
    if issues:
        logger.warning("  ⚠️ MUAMMOLAR:")
        for i in issues:
            logger.warning(f"    • {i}")
    else:
        logger.info("  ✅ Barcha tekshiruvlar o'tdi")
    logger.info("═" * 50)
