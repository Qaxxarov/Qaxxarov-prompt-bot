"""
Agro AI — Memory Manager
Persistent JSON-based memory with scoring, tagging, and search.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.memory")

MEMORY_DIR = DATA_DIR / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MemoryEntry:
    """Bitta xotira yozuvi."""
    id: str = ""
    category: str = ""          # hook, story, cta, caption, trend, audience, score
    content: str = ""           # Asosiy matn
    tags: List[str] = field(default_factory=list)
    score: float = 0.0          # 0-10 (performance ball)
    account_id: str = ""
    source: str = ""            # "generated", "scraped", "user", "competitor"
    metadata: Dict = field(default_factory=dict)
    created_at: float = 0.0
    used_count: int = 0
    last_used: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"{self.category}_{int(time.time() * 1000)}"
        if not self.created_at:
            self.created_at = time.time()


class MemoryManager:
    """
    Per-account persistent memory.
    Stores hooks, stories, patterns, scores — learns over time.
    """

    def __init__(self):
        self._stores: Dict[str, List[MemoryEntry]] = {}

    def _get_path(self, account_id: str) -> Path:
        return MEMORY_DIR / f"{account_id}.json"

    def _load(self, account_id: str) -> List[MemoryEntry]:
        """Akkaunt xotirasini yuklash."""
        if account_id in self._stores:
            return self._stores[account_id]

        path = self._get_path(account_id)
        entries: List[MemoryEntry] = []

        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                entries = [MemoryEntry(**e) for e in data]
                logger.info(f"📚 Xotira yuklandi: {account_id} ({len(entries)} yozuv)")
            except Exception as e:
                logger.error(f"Xotira yuklashda xato ({account_id}): {e}")

        self._stores[account_id] = entries
        return entries

    def _save(self, account_id: str) -> None:
        """Xotirani diskka saqlash."""
        entries = self._stores.get(account_id, [])
        path = self._get_path(account_id)
        try:
            data = [asdict(e) for e in entries]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Xotira saqlashda xato ({account_id}): {e}")

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def save_memory(
        self,
        account_id: str,
        category: str,
        content: str,
        tags: List[str] = None,
        score: float = 5.0,
        source: str = "generated",
        metadata: Dict = None,
    ) -> MemoryEntry:
        """Yangi xotira yozuvi saqlash."""
        entries = self._load(account_id)

        entry = MemoryEntry(
            category=category,
            content=content,
            tags=tags or [],
            score=score,
            account_id=account_id,
            source=source,
            metadata=metadata or {},
        )
        entries.append(entry)

        # Max 500 yozuv — eng pastlarini o'chirish
        if len(entries) > 500:
            entries.sort(key=lambda e: e.score, reverse=True)
            self._stores[account_id] = entries[:500]

        self._save(account_id)
        logger.debug(f"💾 Xotira saqlandi: {category} | score={score}")
        return entry

    def search_memory(
        self,
        account_id: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_score: float = 0.0,
        limit: int = 20,
        source: Optional[str] = None,
    ) -> List[MemoryEntry]:
        """Xotirada qidirish."""
        entries = self._load(account_id)
        results = entries

        if category:
            results = [e for e in results if e.category == category]
        if tags:
            tag_set = set(tags)
            results = [e for e in results if tag_set.intersection(e.tags)]
        if min_score > 0:
            results = [e for e in results if e.score >= min_score]
        if source:
            results = [e for e in results if e.source == source]

        # Score bo'yicha tartiblash
        results.sort(key=lambda e: e.score, reverse=True)
        return results[:limit]

    def get_best_patterns(self, account_id: str, category: str, limit: int = 10) -> List[MemoryEntry]:
        """Eng yaxshi pattern'larni olish (score >= 7)."""
        return self.search_memory(account_id, category=category, min_score=7.0, limit=limit)

    def get_failed_patterns(self, account_id: str, category: str, limit: int = 10) -> List[MemoryEntry]:
        """Muvaffaqiyatsiz pattern'lar (score < 3)."""
        entries = self._load(account_id)
        results = [e for e in entries if e.category == category and e.score < 3.0]
        results.sort(key=lambda e: e.score)
        return results[:limit]

    def get_top_hooks(self, account_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Eng yaxshi hooklar."""
        return self.get_best_patterns(account_id, "hook", limit)

    def get_best_story_structures(self, account_id: str, limit: int = 5) -> List[MemoryEntry]:
        """Eng yaxshi hikoya tuzilmalari."""
        return self.get_best_patterns(account_id, "story", limit)

    def update_score(self, account_id: str, entry_id: str, new_score: float) -> bool:
        """Yozuv ballini yangilash."""
        entries = self._load(account_id)
        for e in entries:
            if e.id == entry_id:
                e.score = new_score
                e.used_count += 1
                e.last_used = time.time()
                self._save(account_id)
                return True
        return False

    def mark_used(self, account_id: str, entry_id: str) -> None:
        """Yozuv ishlatilganini belgilash."""
        entries = self._load(account_id)
        for e in entries:
            if e.id == entry_id:
                e.used_count += 1
                e.last_used = time.time()
                break
        self._save(account_id)

    # ─────────────────────────────────────────────────────
    # ANALYTICS
    # ─────────────────────────────────────────────────────

    def get_stats(self, account_id: str) -> Dict:
        """Xotira statistikasi."""
        entries = self._load(account_id)
        if not entries:
            return {"total": 0, "categories": {}, "avg_score": 0}

        from collections import Counter
        cats = Counter(e.category for e in entries)
        scores = [e.score for e in entries]

        return {
            "total": len(entries),
            "categories": dict(cats),
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "top_score": max(scores) if scores else 0,
            "sources": dict(Counter(e.source for e in entries)),
        }

    def get_learning_context(self, account_id: str, category: str, limit: int = 5) -> str:
        """
        AI uchun o'rganish konteksti — eng yaxshi pattern'lardan.
        Bu matn AI prompt'ga qo'shiladi.
        """
        best = self.get_best_patterns(account_id, category, limit)
        if not best:
            return ""

        lines = [f"OLDINGI MUVAFFAQIYATLI {category.upper()} NAMUNALARI:"]
        for e in best:
            lines.append(f"  [score={e.score}] {e.content[:100]}")
        lines.append("Yuqoridagi namunalardan o'rgan va yanada yaxshiroq yarat.")
        return "\n".join(lines)

    def avoid_repetition_context(self, account_id: str, category: str, limit: int = 10) -> str:
        """
        Takrorlanishdan qochish uchun kontekst.
        Oxirgi yaratilgan kontentni AI'ga ko'rsatadi.
        """
        entries = self._load(account_id)
        recent = [e for e in entries if e.category == category]
        recent.sort(key=lambda e: e.created_at, reverse=True)
        recent = recent[:limit]

        if not recent:
            return ""

        lines = ["TAKRORLANMASIN — oxirgi yaratilgan kontentlar:"]
        for e in recent:
            lines.append(f"  - {e.content[:80]}")
        lines.append("Yuqoridagilardan FARQLI va YANGI kontent yarat.")
        return "\n".join(lines)


# Global instance
memory = MemoryManager()
