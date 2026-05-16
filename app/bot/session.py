"""
Agro AI — User Session Management
Har bir foydalanuvchi uchun alohida sessiya + asyncio.Lock.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("agro_ai.bot.session")


@dataclass
class UserSession:
    """Bitta foydalanuvchi sessiyasi."""
    user_id: int = 0
    # Scraping natijalari
    profile: Optional[object] = None  # ProfileData
    reels: List = field(default_factory=list)
    stats: Optional[Dict] = None
    ideas: List = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    # Holat
    is_scraping: bool = False
    active_account_id: str = ""

    @property
    def has_data(self) -> bool:
        return self.stats is not None and len(self.reels) > 0


class SessionManager:
    """Global session boshqaruvchi — asyncio.Lock bilan thread-safe."""

    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
        self._locks: Dict[int, asyncio.Lock] = {}

    def get(self, user_id: int) -> UserSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        return self._sessions[user_id]

    def get_lock(self, user_id: int) -> asyncio.Lock:
        """User-specific lock — scraping race condition oldini olish."""
        if user_id not in self._locks:
            self._locks[user_id] = asyncio.Lock()
        return self._locks[user_id]

    def reset(self, user_id: int) -> None:
        self._sessions[user_id] = UserSession(user_id=user_id)

    def all_sessions(self) -> Dict[int, UserSession]:
        return self._sessions.copy()

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.has_data)


# Global instance
sessions = SessionManager()
