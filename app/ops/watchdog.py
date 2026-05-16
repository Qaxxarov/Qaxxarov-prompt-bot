"""
Agro AI — Watchdog System
Background health monitoring, auto-recovery, crash detection.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from app.settings import DATA_DIR, EXPORT_DIR

logger = logging.getLogger("agro_ai.ops.watchdog")

HEALTH_FILE = DATA_DIR / "health.json"


class SystemHealth:
    """System health state."""

    def __init__(self):
        self.last_heartbeat: float = time.time()
        self.bot_alive: bool = True
        self.dashboard_alive: bool = False
        self.last_scrape_success: float = 0
        self.last_scrape_error: str = ""
        self.total_scrapes: int = 0
        self.failed_scrapes: int = 0
        self.total_ai_calls: int = 0
        self.failed_ai_calls: int = 0
        self.uptime_start: float = time.time()
        self.memory_entries: int = 0
        self.disk_usage_mb: float = 0

    @property
    def uptime_hours(self) -> float:
        return (time.time() - self.uptime_start) / 3600

    @property
    def scrape_success_rate(self) -> float:
        if self.total_scrapes == 0:
            return 100.0
        return round((self.total_scrapes - self.failed_scrapes) / self.total_scrapes * 100, 1)

    @property
    def ai_success_rate(self) -> float:
        if self.total_ai_calls == 0:
            return 100.0
        return round((self.total_ai_calls - self.failed_ai_calls) / self.total_ai_calls * 100, 1)

    def heartbeat(self) -> None:
        self.last_heartbeat = time.time()

    def record_scrape(self, success: bool, error: str = "") -> None:
        self.total_scrapes += 1
        if not success:
            self.failed_scrapes += 1
            self.last_scrape_error = error
        else:
            self.last_scrape_success = time.time()

    def record_ai_call(self, success: bool) -> None:
        self.total_ai_calls += 1
        if not success:
            self.failed_ai_calls += 1

    def get_disk_usage(self) -> float:
        """Reports + data folder size in MB."""
        total = 0
        for folder in [EXPORT_DIR, DATA_DIR]:
            if folder.exists():
                for f in folder.rglob("*"):
                    if f.is_file():
                        total += f.stat().st_size
        self.disk_usage_mb = round(total / (1024 * 1024), 1)
        return self.disk_usage_mb

    def format_status(self) -> str:
        """Telegram-ready health report."""
        now = datetime.now()
        self.get_disk_usage()

        scrape_ago = ""
        if self.last_scrape_success > 0:
            hours = (time.time() - self.last_scrape_success) / 3600
            scrape_ago = f"{hours:.1f} soat oldin"
        else:
            scrape_ago = "hali qilinmagan"

        return (
            f"🏥 *TIZIM SALOMATLIGI*\n"
            f"📅 {now.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"⏱ Uptime: *{self.uptime_hours:.1f}* soat\n"
            f"💓 Bot: {'✅ Faol' if self.bot_alive else '❌ Muammo'}\n"
            f"🌐 Dashboard: {'✅' if self.dashboard_alive else '⬜ off'}\n\n"
            f"📊 *Scraping:*\n"
            f"  Jami: {self.total_scrapes} | Xato: {self.failed_scrapes}\n"
            f"  Muvaffaqiyat: {self.scrape_success_rate}%\n"
            f"  Oxirgi: {scrape_ago}\n\n"
            f"🤖 *AI:*\n"
            f"  Jami: {self.total_ai_calls} | Xato: {self.failed_ai_calls}\n"
            f"  Muvaffaqiyat: {self.ai_success_rate}%\n\n"
            f"💾 Disk: {self.disk_usage_mb} MB\n"
            f"🧠 Memory: {self.memory_entries} yozuv"
        )


# Global instance
health = SystemHealth()


class Watchdog:
    """
    Background watchdog — monitors system health.
    Integrates with Telegram bot JobQueue.
    """

    def __init__(self):
        self._running = False

    def register_jobs(self, app) -> None:
        """Register health check job."""
        from datetime import time as dt_time
        jq = app.job_queue

        # Health check every 30 minutes
        jq.run_repeating(
            self._health_check,
            interval=1800,
            first=60,
            name="watchdog_health",
        )
        self._running = True
        logger.info("🏥 Watchdog registered (30 min interval)")

    async def _health_check(self, context) -> None:
        """Periodic health check."""
        health.heartbeat()
        health.get_disk_usage()

        # Check memory entries
        try:
            from app.memory import memory
            from app.accounts import accounts
            stats = memory.get_stats(accounts.active.id)
            health.memory_entries = stats.get("total", 0)
        except Exception:
            pass

        # Alert if scrape failure rate > 50%
        if health.total_scrapes > 3 and health.scrape_success_rate < 50:
            from app.settings import ADMIN_IDS
            if ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_IDS[0],
                        text=(
                            "🚨 *WATCHDOG ALERT*\n\n"
                            f"Scraping muvaffaqiyat darajasi past: {health.scrape_success_rate}%\n"
                            f"Oxirgi xato: {health.last_scrape_error[:100]}\n\n"
                            "Chrome profil yoki internet muammosi bo'lishi mumkin."
                        ),
                        parse_mode="Markdown",
                    )
                except Exception:
                    pass


watchdog = Watchdog()
