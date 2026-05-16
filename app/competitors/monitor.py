"""
Agro AI — 🕵️ Competitor Real-Time Monitor
Raqobatchilarni kuzatib, o'zgarishda alert yuborish.
Har 6 soatda avtomatik scrape.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.competitors.monitor")

MONITOR_DIR = DATA_DIR / "competitor_monitor"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CompetitorSnapshot:
    """Raqobatchi holatining bir vaqtdagi surati."""
    username: str
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    avg_views: int = 0
    avg_er: float = 0.0
    latest_reel_views: int = 0
    latest_reel_caption: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class CompetitorAlert:
    """Raqobatchi haqida alert."""
    username: str
    alert_type: str  # "viral_reel", "follower_spike", "hook_pattern", "er_change"
    message: str
    data: Dict = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class CompetitorMonitor:
    """
    Raqobatchilarni real-time monitoring.
    - Competitor qo'shish/o'chirish
    - Har 6 soatda avtomatik scrape
    - Alert yaratish (viral reel, follower spike, hook pattern)
    """

    def __init__(self, account_id: str):
        self.account_id = account_id
        self._data_path = MONITOR_DIR / f"{account_id}_competitors.json"
        self._history_path = MONITOR_DIR / f"{account_id}_history.json"
        self._alerts_path = MONITOR_DIR / f"{account_id}_alerts.json"
        self._competitors: Dict[str, Dict] = {}
        self._history: Dict[str, List[Dict]] = {}
        self._alerts: List[Dict] = []
        self._load()

    def _load(self) -> None:
        """Ma'lumotlarni yuklash."""
        if self._data_path.exists():
            try:
                with open(self._data_path, "r", encoding="utf-8") as f:
                    self._competitors = json.load(f)
            except Exception as e:
                logger.error(f"Competitor data yuklashda xato: {e}")

        if self._history_path.exists():
            try:
                with open(self._history_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except Exception as e:
                logger.error(f"Competitor history yuklashda xato: {e}")

        if self._alerts_path.exists():
            try:
                with open(self._alerts_path, "r", encoding="utf-8") as f:
                    self._alerts = json.load(f)
            except Exception as e:
                logger.error(f"Alerts yuklashda xato: {e}")

    def _save(self) -> None:
        """Ma'lumotlarni saqlash."""
        try:
            with open(self._data_path, "w", encoding="utf-8") as f:
                json.dump(self._competitors, f, ensure_ascii=False, indent=2)
            with open(self._history_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
            with open(self._alerts_path, "w", encoding="utf-8") as f:
                json.dump(self._alerts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Competitor data saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def add_competitor(self, username: str) -> bool:
        """Yangi raqobatchi qo'shish."""
        username = username.lstrip("@").strip().lower()
        if username in self._competitors:
            return False
        self._competitors[username] = {
            "username": username,
            "added_at": time.time(),
            "last_scan": 0,
            "followers": 0,
            "avg_views": 0,
            "avg_er": 0.0,
            "latest_reel_views": 0,
        }
        self._history[username] = []
        self._save()
        logger.info(f"➕ Competitor qo'shildi: @{username}")
        return True

    def remove_competitor(self, username: str) -> bool:
        """Raqobatchini o'chirish."""
        username = username.lstrip("@").strip().lower()
        if username in self._competitors:
            del self._competitors[username]
            self._history.pop(username, None)
            self._save()
            return True
        return False

    def get_all(self) -> List[Dict]:
        """Barcha raqobatchilar ro'yxati."""
        return list(self._competitors.values())

    def get_competitor(self, username: str) -> Optional[Dict]:
        """Bitta raqobatchi ma'lumoti."""
        return self._competitors.get(username.lstrip("@").strip().lower())

    # ─────────────────────────────────────────────────────
    # MONITORING
    # ─────────────────────────────────────────────────────

    async def scan_all(self) -> List[CompetitorAlert]:
        """Barcha raqobatchilarni skanerlash va alertlar yaratish."""
        alerts = []
        for username, data in self._competitors.items():
            try:
                new_alerts = await self._scan_one(username, data)
                alerts.extend(new_alerts)
            except Exception as e:
                logger.error(f"Competitor scan xatosi (@{username}): {e}")
        return alerts

    async def _scan_one(self, username: str, prev_data: Dict) -> List[CompetitorAlert]:
        """Bitta raqobatchini skanerlash."""
        alerts = []

        # Scraper orqali yangi ma'lumot olish
        try:
            new_data = await self._fetch_competitor_data(username)
        except Exception as e:
            logger.warning(f"Fetch xatosi @{username}: {e}")
            return alerts

        if not new_data:
            return alerts

        # Follower spike tekshirish
        old_followers = prev_data.get("followers", 0)
        new_followers = new_data.get("followers", 0)
        if old_followers > 0 and new_followers > old_followers:
            diff = new_followers - old_followers
            if diff >= 100:  # 100+ yangi follower
                alert = CompetitorAlert(
                    username=username,
                    alert_type="follower_spike",
                    message=f"📈 @{username} {diff} yangi follower oldi!",
                    data={"old": old_followers, "new": new_followers, "diff": diff},
                )
                alerts.append(alert)

        # Viral reel tekshirish
        new_views = new_data.get("latest_reel_views", 0)
        old_views = prev_data.get("latest_reel_views", 0)
        if new_views > old_views and new_views >= 10000:
            alert = CompetitorAlert(
                username=username,
                alert_type="viral_reel",
                message=f"🚨 @{username} viral reel chiqardi ({new_views:,} views)!",
                data={"views": new_views, "caption": new_data.get("latest_reel_caption", "")},
            )
            alerts.append(alert)

        # ER o'zgarishi
        old_er = prev_data.get("avg_er", 0)
        new_er = new_data.get("avg_er", 0)
        if old_er > 0 and new_er > 0:
            er_change = new_er - old_er
            if abs(er_change) >= 1.0:  # 1%+ o'zgarish
                direction = "oshdi" if er_change > 0 else "tushdi"
                alert = CompetitorAlert(
                    username=username,
                    alert_type="er_change",
                    message=f"⚡ @{username} ER {direction}: {old_er:.1f}% → {new_er:.1f}%",
                    data={"old_er": old_er, "new_er": new_er},
                )
                alerts.append(alert)

        # Ma'lumotni yangilash
        self._competitors[username].update({
            "followers": new_followers,
            "avg_views": new_data.get("avg_views", 0),
            "avg_er": new_er,
            "latest_reel_views": new_views,
            "last_scan": time.time(),
        })

        # Tarixga qo'shish
        if username not in self._history:
            self._history[username] = []
        self._history[username].append({
            "timestamp": time.time(),
            "followers": new_followers,
            "avg_views": new_data.get("avg_views", 0),
            "avg_er": new_er,
        })
        # Max 100 tarix
        self._history[username] = self._history[username][-100:]

        # Alertlarni saqlash
        for a in alerts:
            self._alerts.append(asdict(a))
        self._alerts = self._alerts[-200:]  # Max 200 alert

        self._save()
        return alerts

    async def _fetch_competitor_data(self, username: str) -> Optional[Dict]:
        """
        Raqobatchi ma'lumotini olish.
        Scraper mavjud bo'lsa ishlatadi, aks holda None.
        """
        try:
            from app.scraper.pipeline import ScrapePipeline
            pipeline = ScrapePipeline(target_profile=username)
            data = pipeline.quick_scan()
            if data:
                return {
                    "followers": data.get("profile", {}).get("followers", 0),
                    "avg_views": data.get("views", {}).get("average", 0),
                    "avg_er": data.get("engagement", {}).get("average_er", 0),
                    "latest_reel_views": data.get("views", {}).get("max", 0),
                    "latest_reel_caption": "",
                }
        except Exception as e:
            logger.debug(f"Scraper mavjud emas yoki xato: {e}")

        return None

    # ─────────────────────────────────────────────────────
    # ALERTS
    # ─────────────────────────────────────────────────────

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Oxirgi alertlar."""
        return self._alerts[-limit:]

    def get_alerts_for(self, username: str, limit: int = 5) -> List[Dict]:
        """Bitta raqobatchi uchun alertlar."""
        username = username.lstrip("@").strip().lower()
        filtered = [a for a in self._alerts if a.get("username") == username]
        return filtered[-limit:]

    # ─────────────────────────────────────────────────────
    # ANALYTICS
    # ─────────────────────────────────────────────────────

    def get_summary(self) -> str:
        """Monitoring umumiy holati."""
        total = len(self._competitors)
        if total == 0:
            return "Hali raqobatchi qo'shilmagan."

        lines = [f"📊 *MONITORING HOLATI*\n"]
        lines.append(f"👥 Raqobatchilar: {total} ta\n")

        for username, data in self._competitors.items():
            followers = data.get("followers", 0)
            avg_views = data.get("avg_views", 0)
            lines.append(f"• @{username}: {followers:,} followers, {avg_views:,} avg views")

        recent_alerts = self.get_recent_alerts(5)
        if recent_alerts:
            lines.append(f"\n🔔 *Oxirgi alertlar:*")
            for a in recent_alerts:
                lines.append(f"  {a.get('message', '')}")

        return "\n".join(lines)

    def get_follower_trend(self, username: str) -> List[Dict]:
        """Raqobatchi follower trendi."""
        username = username.lstrip("@").strip().lower()
        return self._history.get(username, [])
