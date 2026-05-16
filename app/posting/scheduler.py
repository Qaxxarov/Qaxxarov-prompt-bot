"""
Agro AI — Post Scheduler
Tayyor kontentni belgilangan vaqtda post qilish navbati.
"""

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.posting.scheduler")

POST_QUEUE_FILE = DATA_DIR / "post_queue.json"


@dataclass
class ScheduledPost:
    """Navbatdagi post."""
    id: str = ""
    caption: str = ""
    media_path: str = ""
    scheduled_time: str = ""  # ISO format: 2025-01-15T19:00:00
    status: str = "pending"  # pending, published, failed, cancelled
    hashtags: List[str] = field(default_factory=list)
    account_id: str = ""
    hook: str = ""
    notes: str = ""
    created_at: float = 0.0
    published_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"post_{uuid.uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = time.time()

    @property
    def scheduled_datetime(self) -> Optional[datetime]:
        """Scheduled time as datetime."""
        try:
            return datetime.fromisoformat(self.scheduled_time)
        except (ValueError, TypeError):
            return None

    @property
    def is_due(self) -> bool:
        """Post vaqti keldimi?"""
        dt = self.scheduled_datetime
        if not dt:
            return False
        return datetime.now() >= dt and self.status == "pending"


class PostScheduler:
    """
    Post navbati boshqaruvchisi.
    - Navbatga qo'shish
    - Vaqti kelganda publish yoki reminder
    - Tarix saqlash
    """

    def __init__(self):
        self._queue: List[ScheduledPost] = []
        self._load()

    def _load(self) -> None:
        """post_queue.json dan yuklash."""
        if POST_QUEUE_FILE.exists():
            try:
                with open(POST_QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for p_data in data.get("queue", []):
                    post = ScheduledPost(**p_data)
                    self._queue.append(post)
                logger.info(f"📋 {len(self._queue)} ta scheduled post yuklandi")
            except Exception as e:
                logger.error(f"Post queue yuklashda xato: {e}")
        else:
            self._save()

    def _save(self) -> None:
        """Saqlash."""
        try:
            data = {"queue": [asdict(p) for p in self._queue]}
            POST_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(POST_QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Post queue saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def add_to_queue(
        self,
        caption: str,
        scheduled_time: str,
        account_id: str,
        media_path: str = "",
        hashtags: List[str] = None,
        hook: str = "",
        notes: str = "",
    ) -> ScheduledPost:
        """Navbatga yangi post qo'shish."""
        post = ScheduledPost(
            caption=caption,
            media_path=media_path,
            scheduled_time=scheduled_time,
            hashtags=hashtags or [],
            account_id=account_id,
            hook=hook,
            notes=notes,
        )
        self._queue.append(post)
        self._save()
        logger.info(f"➕ Post navbatga qo'shildi: {post.id} ({scheduled_time})")
        return post

    def cancel_post(self, post_id: str) -> bool:
        """Postni bekor qilish."""
        for p in self._queue:
            if p.id == post_id and p.status == "pending":
                p.status = "cancelled"
                self._save()
                return True
        return False

    def mark_published(self, post_id: str) -> bool:
        """Postni published deb belgilash."""
        for p in self._queue:
            if p.id == post_id:
                p.status = "published"
                p.published_at = time.time()
                self._save()
                return True
        return False

    def mark_failed(self, post_id: str) -> bool:
        """Postni failed deb belgilash."""
        for p in self._queue:
            if p.id == post_id:
                p.status = "failed"
                self._save()
                return True
        return False

    # ─────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────

    def get_pending(self) -> List[ScheduledPost]:
        """Kutilayotgan postlar."""
        return [p for p in self._queue if p.status == "pending"]

    def get_due_posts(self) -> List[ScheduledPost]:
        """Vaqti kelgan postlar."""
        return [p for p in self._queue if p.is_due]

    def get_today_posts(self) -> List[ScheduledPost]:
        """Bugungi postlar."""
        today = datetime.now().strftime("%Y-%m-%d")
        return [
            p for p in self._queue
            if p.scheduled_time.startswith(today) and p.status == "pending"
        ]

    def get_history(self, limit: int = 20) -> List[ScheduledPost]:
        """Post tarixi (published + failed)."""
        history = [p for p in self._queue if p.status in ("published", "failed")]
        history.sort(key=lambda p: p.published_at or p.created_at, reverse=True)
        return history[:limit]

    def get_post(self, post_id: str) -> Optional[ScheduledPost]:
        """Post ID bo'yicha topish."""
        for p in self._queue:
            if p.id == post_id:
                return p
        return None

    # ─────────────────────────────────────────────────────
    # FORMATTING
    # ─────────────────────────────────────────────────────

    def format_queue(self) -> str:
        """Navbatni formatlash."""
        pending = self.get_pending()
        if not pending:
            return "_(Navbat bo'sh.)_"

        lines = []
        for i, p in enumerate(pending, 1):
            dt = p.scheduled_datetime
            time_str = dt.strftime("%d.%m %H:%M") if dt else "?"
            lines.append(
                f"*{i}.* ⏰ {time_str}\n"
                f"   📝 {p.caption[:50]}...\n"
                f"   🆔 `{p.id}`"
            )
        return "\n".join(lines)

    def format_today(self) -> str:
        """Bugungi postlarni formatlash."""
        today = self.get_today_posts()
        if not today:
            return "_(Bugun uchun post yo'q.)_"

        lines = []
        for p in today:
            dt = p.scheduled_datetime
            time_str = dt.strftime("%H:%M") if dt else "?"
            lines.append(f"⏰ {time_str} — {p.caption[:60]}...")
        return "\n".join(lines)


# Global instance
post_scheduler = PostScheduler()
