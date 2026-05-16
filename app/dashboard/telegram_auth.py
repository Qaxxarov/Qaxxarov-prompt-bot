"""
Agro AI — Telegram WebApp Authentication
Validates Telegram Mini App initData for secure sessions.
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Optional
from urllib.parse import parse_qs, unquote

from app.settings import ADMIN_IDS, TELEGRAM_BOT_TOKEN

logger = logging.getLogger("agro_ai.dashboard.tg_auth")

# Sessions: {user_id: {"validated": timestamp, "user_data": dict}}
_tg_sessions: dict = {}
SESSION_TTL = 24 * 3600


def validate_webapp_data(init_data: str) -> Optional[dict]:
    """
    Validate Telegram WebApp initData.
    Returns user dict if valid, None otherwise.
    
    Telegram signs initData with HMAC-SHA256 using:
    secret_key = HMAC-SHA256(bot_token, "WebAppData")
    """
    if not init_data or not TELEGRAM_BOT_TOKEN:
        return None

    try:
        parsed = parse_qs(init_data)
        
        # Extract hash
        received_hash = parsed.get("hash", [""])[0]
        if not received_hash:
            return None

        # Build data-check-string (sorted, without hash)
        data_pairs = []
        for key, values in parsed.items():
            if key == "hash":
                continue
            data_pairs.append(f"{key}={values[0]}")
        data_pairs.sort()
        data_check_string = "\n".join(data_pairs)

        # Compute expected hash
        secret_key = hmac.new(
            b"WebAppData",
            TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(received_hash, expected_hash):
            logger.warning("❌ WebApp initData hash mismatch")
            return None

        # Check auth_date freshness (max 24h)
        auth_date = int(parsed.get("auth_date", ["0"])[0])
        if time.time() - auth_date > SESSION_TTL:
            logger.warning("❌ WebApp initData expired")
            return None

        # Extract user
        user_raw = parsed.get("user", [""])[0]
        if user_raw:
            user = json.loads(unquote(user_raw))
            return user

        return None

    except Exception as e:
        logger.error(f"WebApp auth xatosi: {e}")
        return None


def create_tg_session(user_data: dict) -> Optional[str]:
    """Create session from validated Telegram user data."""
    user_id = user_data.get("id")
    if not user_id:
        return None

    # Check if user is allowed
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        logger.warning(f"❌ Ruxsatsiz foydalanuvchi: {user_id}")
        return None

    # Create token (user_id based for simplicity)
    import secrets
    token = secrets.token_urlsafe(32)
    
    _tg_sessions[token] = {
        "user_id": user_id,
        "user_data": user_data,
        "created": time.time(),
    }

    logger.info(f"✅ TG session: {user_data.get('first_name', '')} (ID: {user_id})")
    return token


def validate_tg_token(token: str) -> Optional[dict]:
    """Validate a Telegram session token."""
    if not token:
        return None
    session = _tg_sessions.get(token)
    if not session:
        return None
    if time.time() - session["created"] > SESSION_TTL:
        del _tg_sessions[token]
        return None
    return session["user_data"]


def get_webapp_url(base_url: str, page: str = "") -> str:
    """Generate WebApp URL for a specific page."""
    url = base_url.rstrip("/")
    if page:
        return f"{url}/#/{page}"
    return url
