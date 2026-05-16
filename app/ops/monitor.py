"""
Agro AI — Instagram Monitor
Real-time account state tracking via existing scraper.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR, CHROME_PROFILE_DIR, CHROME_USER_DATA_DIR, TARGET_PROFILE

logger = logging.getLogger("agro_ai.ops.monitor")

MONITOR_DIR = DATA_DIR / "monitor"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ReelSnapshot:
    """Bitta reel holati snapshot."""
    url: str = ""
    shortcode: str = ""
    caption: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    posted_at: str = ""
    scraped_at: float = 0.0

    @property
    def age_hours(self) -> float:
        if not self.posted_at:
            return -1
        try:
            posted = datetime.fromisoformat(self.posted_at.replace("Z", "+00:00"))
            return (datetime.now(posted.tzinfo) - posted).total_seconds() / 3600
        except Exception:
            return -1


@dataclass
class AccountState:
    """Akkaunt holati — oxirgi skan natijasi."""
    username: str = ""
    followers: int = 0
    total_reels: int = 0
    last_scan_time: float = 0.0
    recent_reels: List[ReelSnapshot] = field(default_factory=list)
    avg_views: int = 0
    avg_er: float = 0.0
    max_views: int = 0
    viral_count: int = 0
    posted_today: bool = False
    last_post_hours_ago: float = -1
    posting_streak: int = 0
    missed_days: int = 0

    @property
    def is_stale(self) -> bool:
        """Ma'lumot 6 soatdan eski bo'lsa."""
        if self.last_scan_time == 0:
            return True
        return (time.time() - self.last_scan_time) > 6 * 3600

    @property
    def hours_since_scan(self) -> float:
        if self.last_scan_time == 0:
            return -1
        return (time.time() - self.last_scan_time) / 3600


class InstagramMonitor:
    """
    Real-time Instagram account monitoring.
    Uses existing scraper to fetch fresh data.
    Stores state history for trend analysis.
    """

    def __init__(self, account_id: str = "agro_uruglar"):
        self.account_id = account_id
        self._state_path = MONITOR_DIR / f"{account_id}_state.json"
        self._history_path = MONITOR_DIR / f"{account_id}_history.json"
        self._state: Optional[AccountState] = None

    @property
    def state(self) -> AccountState:
        if self._state is None:
            self._state = self._load_state()
        return self._state

    def _load_state(self) -> AccountState:
        if self._state_path.exists():
            try:
                with open(self._state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                reels_data = data.pop("recent_reels", [])
                state = AccountState(**data)
                state.recent_reels = [ReelSnapshot(**r) for r in reels_data]
                return state
            except Exception as e:
                logger.error(f"State yuklashda xato: {e}")
        return AccountState(username=TARGET_PROFILE)

    def _save_state(self) -> None:
        if self._state:
            try:
                data = asdict(self._state)
                with open(self._state_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"State saqlashda xato: {e}")

    def _save_history(self, state: AccountState) -> None:
        """Tarixga qo'shish (kunlik snapshot)."""
        history = []
        if self._history_path.exists():
            try:
                with open(self._history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass

        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "followers": state.followers,
            "avg_views": state.avg_views,
            "avg_er": state.avg_er,
            "total_reels": state.total_reels,
            "posted_today": state.posted_today,
            "posting_streak": state.posting_streak,
        }
        history.append(entry)
        # Oxirgi 90 kun saqlash
        history = history[-90:]

        try:
            with open(self._history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"History saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # SCANNING
    # ─────────────────────────────────────────────────────

    def scan_now(self) -> AccountState:
        """
        Hoziroq Instagram'ni skanlab yangi state yaratish.
        Uses ScrapingPipeline for reliability.
        SINXRON — thread pool'da chaqiring.
        """
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

        logger.info(f"🔍 Instagram skanlanmoqda: @{TARGET_PROFILE}")

        try:
            from app.scraper.pipeline import ScrapingPipeline
            pipeline = ScrapingPipeline()
            result = pipeline.run()

            if not result.success or not result.reels:
                logger.warning(f"⚠️ Skan muvaffaqiyatsiz: {result.error}")
                return self.state

            stats = result.stats
            reels = result.reels
            profile = result.profile

            # Recent reels snapshot
            recent = []
            for r in reels[:10]:
                recent.append(ReelSnapshot(
                    url=r.url,
                    shortcode=getattr(r, "shortcode", ""),
                    caption=r.caption[:100] if r.caption else "",
                    views=r.views,
                    likes=r.likes,
                    comments=r.comments,
                    engagement_rate=r.engagement_rate,
                    posted_at=getattr(r, "posted_at", ""),
                    scraped_at=time.time(),
                ))

            # Bugun post qilinganmi?
            posted_today = False
            last_post_hours = -1.0
            today_str = datetime.now().strftime("%Y-%m-%d")
            for r in recent:
                if r.posted_at and today_str in r.posted_at:
                    posted_today = True
                age = r.age_hours
                if age >= 0 and (last_post_hours < 0 or age < last_post_hours):
                    last_post_hours = age

            # Streak hisoblash
            old_state = self.state
            if posted_today:
                streak = old_state.posting_streak + 1 if old_state.posted_today else 1
                missed = 0
            else:
                streak = old_state.posting_streak
                if not old_state.posted_today and old_state.last_scan_time > 0:
                    missed = old_state.missed_days + 1
                else:
                    missed = old_state.missed_days

            tiers = stats.get("performance_tiers", {})
            new_state = AccountState(
                username=profile.username,
                followers=profile.followers,
                total_reels=profile.posts_count,
                last_scan_time=time.time(),
                recent_reels=recent,
                avg_views=stats["views"]["average"],
                avg_er=stats["engagement"]["average_er"],
                max_views=stats["views"]["max"],
                viral_count=tiers.get("viral", {}).get("count", 0),
                posted_today=posted_today,
                last_post_hours_ago=last_post_hours,
                posting_streak=streak,
                missed_days=missed,
            )

            self._state = new_state
            self._save_state()
            self._save_history(new_state)

            logger.info(
                f"✅ Skan tugadi: {len(reels)} reels | "
                f"avg={new_state.avg_views:,} views | "
                f"posted_today={posted_today} | streak={streak}"
            )
            return new_state

        except Exception as e:
            logger.exception(f"Skan xatosi: {e}")
            return self.state

    def get_history(self, days: int = 30) -> List[Dict]:
        """Oxirgi N kunlik tarix."""
        if not self._history_path.exists():
            return []
        try:
            with open(self._history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
            return history[-days:]
        except Exception:
            return []

    def get_growth_trend(self, days: int = 7) -> Dict:
        """O'sish trendi — oxirgi N kun."""
        history = self.get_history(days)
        if len(history) < 2:
            return {"trend": "unknown", "data": []}

        first = history[0]
        last = history[-1]
        follower_change = last.get("followers", 0) - first.get("followers", 0)
        view_change = last.get("avg_views", 0) - first.get("avg_views", 0)

        return {
            "trend": "up" if follower_change > 0 else "down" if follower_change < 0 else "flat",
            "follower_change": follower_change,
            "view_change": view_change,
            "days": len(history),
            "consistency": sum(1 for h in history if h.get("posted_today")) / max(len(history), 1) * 100,
        }
