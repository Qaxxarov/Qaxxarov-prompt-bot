"""
Agro AI — Competitor Data Models
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.competitors.models")

COMPETITORS_DIR = DATA_DIR / "competitors"
COMPETITORS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CompetitorReel:
    """Raqobatchi reeli ma'lumotlari."""
    url: str = ""
    caption: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    hashtags: List[str] = field(default_factory=list)
    hook: str = ""              # Extracted hook (birinchi jumla)
    format_type: str = ""       # tutorial, story, pov, trend, etc.
    emotional_trigger: str = ""
    posted_at: str = ""

    @property
    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return round((self.likes + self.comments) / self.views * 100, 2)


@dataclass
class Competitor:
    """Raqobatchi profili."""
    username: str
    account_id: str = ""        # Qaysi akkauntning raqobatchisi
    full_name: str = ""
    followers: int = 0
    avg_views: int = 0
    avg_er: float = 0.0
    niche: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    top_hooks: List[str] = field(default_factory=list)
    top_hashtags: List[str] = field(default_factory=list)
    viral_patterns: List[str] = field(default_factory=list)
    reels: List[CompetitorReel] = field(default_factory=list)
    last_analyzed: float = 0.0
    notes: str = ""

    @property
    def viral_rate(self) -> float:
        """Viral reels foizi."""
        if not self.reels:
            return 0.0
        viral = sum(1 for r in self.reels if r.views > self.avg_views * 2)
        return round(viral / len(self.reels) * 100, 1)


class CompetitorDatabase:
    """Raqobatchilar bazasi — per-account persistent storage."""

    def __init__(self):
        self._data: Dict[str, List[Competitor]] = {}

    def _get_path(self, account_id: str) -> Path:
        return COMPETITORS_DIR / f"{account_id}_competitors.json"

    def _load(self, account_id: str) -> List[Competitor]:
        if account_id in self._data:
            return self._data[account_id]

        path = self._get_path(account_id)
        competitors: List[Competitor] = []

        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for c_data in data:
                    reels_data = c_data.pop("reels", [])
                    comp = Competitor(**c_data)
                    comp.reels = [CompetitorReel(**r) for r in reels_data]
                    competitors.append(comp)
            except Exception as e:
                logger.error(f"Konkurent yuklashda xato: {e}")

        self._data[account_id] = competitors
        return competitors

    def _save(self, account_id: str) -> None:
        competitors = self._data.get(account_id, [])
        path = self._get_path(account_id)
        try:
            data = []
            for c in competitors:
                c_dict = asdict(c)
                data.append(c_dict)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Konkurent saqlashda xato: {e}")

    def add(self, account_id: str, competitor: Competitor) -> None:
        """Yangi raqobatchi qo'shish."""
        competitors = self._load(account_id)
        # Mavjudini yangilash yoki yangi qo'shish
        existing = next((c for c in competitors if c.username == competitor.username), None)
        if existing:
            idx = competitors.index(existing)
            competitors[idx] = competitor
        else:
            competitors.append(competitor)
        self._save(account_id)

    def get_all(self, account_id: str) -> List[Competitor]:
        return self._load(account_id)

    def get(self, account_id: str, username: str) -> Optional[Competitor]:
        competitors = self._load(account_id)
        return next((c for c in competitors if c.username == username), None)

    def remove(self, account_id: str, username: str) -> bool:
        competitors = self._load(account_id)
        before = len(competitors)
        self._data[account_id] = [c for c in competitors if c.username != username]
        if len(self._data[account_id]) < before:
            self._save(account_id)
            return True
        return False

    def get_all_hooks(self, account_id: str) -> List[str]:
        """Barcha raqobatchilarning top hooklari."""
        competitors = self._load(account_id)
        hooks = []
        for c in competitors:
            hooks.extend(c.top_hooks)
            for r in c.reels:
                if r.hook:
                    hooks.append(r.hook)
        return hooks

    def get_all_patterns(self, account_id: str) -> List[str]:
        """Barcha viral pattern'lar."""
        competitors = self._load(account_id)
        patterns = []
        for c in competitors:
            patterns.extend(c.viral_patterns)
        return patterns


# Global instance
competitor_db = CompetitorDatabase()
