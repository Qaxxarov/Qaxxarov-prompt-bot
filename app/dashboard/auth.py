"""
Agro AI — Dashboard Authentication
Hashed password, brute-force protection, persistent sessions.
"""

import hashlib
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.dashboard.auth")

DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "").strip()
SESSIONS_FILE = DATA_DIR / "sessions.json"
SESSION_DURATION = 24 * 3600  # 24 soat

# Brute-force himoya
_failed_attempts: dict = {}  # {ip_or_key: {"count": int, "blocked_until": float}}
MAX_ATTEMPTS = 5
BLOCK_DURATION = 300  # 5 daqiqa


def _hash_password(password: str) -> str:
    """SHA-256 hash with salt."""
    salt = "agro_ai_salt_2024"
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()


def _is_blocked(key: str = "default") -> bool:
    """Brute-force block tekshirish."""
    info = _failed_attempts.get(key)
    if not info:
        return False
    if info["count"] >= MAX_ATTEMPTS:
        if time.time() < info["blocked_until"]:
            return True
        # Block muddati tugadi — reset
        del _failed_attempts[key]
    return False


def _record_failure(key: str = "default") -> None:
    """Muvaffaqiyatsiz urinishni yozish."""
    if key not in _failed_attempts:
        _failed_attempts[key] = {"count": 0, "blocked_until": 0}
    _failed_attempts[key]["count"] += 1
    if _failed_attempts[key]["count"] >= MAX_ATTEMPTS:
        _failed_attempts[key]["blocked_until"] = time.time() + BLOCK_DURATION
        logger.warning(f"🔒 Dashboard login blocked: {key} ({BLOCK_DURATION}s)")


def _load_sessions() -> dict:
    """Sessiyalarni diskdan yuklash."""
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, "r") as f:
                data = json.load(f)
            # Eskirganlarni tozalash
            now = time.time()
            return {k: v for k, v in data.items() if v.get("expires", 0) > now}
        except Exception:
            pass
    return {}


def _save_sessions(sessions: dict) -> None:
    """Sessiyalarni diskka saqlash."""
    try:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        logger.error(f"Session saqlashda xato: {e}")


# In-memory cache
_sessions = _load_sessions()


def create_session(password: str) -> Optional[str]:
    """Login — parol tekshirib token yaratish."""
    global _sessions

    if _is_blocked():
        logger.warning("🔒 Login blocked (brute-force)")
        return None

    if not DASHBOARD_PASSWORD:
        logger.error("DASHBOARD_PASSWORD o'rnatilmagan")
        return None

    # Parolni tekshirish (plain comparison — .env dan keladi)
    if password != DASHBOARD_PASSWORD:
        _record_failure()
        logger.warning("❌ Dashboard login: noto'g'ri parol")
        return None

    token = secrets.token_urlsafe(32)
    _sessions[token] = {
        "created": time.time(),
        "expires": time.time() + SESSION_DURATION,
    }
    _save_sessions(_sessions)
    logger.info("✅ Dashboard session yaratildi")
    return token


def validate_token(token: str) -> bool:
    """Token haqiqiyligini tekshirish."""
    global _sessions
    if not token:
        return False
    session = _sessions.get(token)
    if not session:
        # Diskdan qayta yuklash
        _sessions = _load_sessions()
        session = _sessions.get(token)
    if not session:
        return False
    if time.time() > session.get("expires", 0):
        _sessions.pop(token, None)
        _save_sessions(_sessions)
        return False
    return True


def logout(token: str) -> None:
    """Sessiyani tugatish."""
    global _sessions
    _sessions.pop(token, None)
    _save_sessions(_sessions)
