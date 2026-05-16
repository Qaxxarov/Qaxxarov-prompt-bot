"""
Agro AI — Operations Scheduler
Automatic scheduled jobs: morning, evening, daily, weekly.
Uses python-telegram-bot's JobQueue.
"""

import asyncio
import logging
from datetime import time as dt_time
from typing import Optional

from telegram.ext import Application, ContextTypes

from app.accounts import accounts
from app.ops.manager import OpsManager
from app.ops.monitor import InstagramMonitor
from app.settings import ADMIN_IDS

logger = logging.getLogger("agro_ai.ops.scheduler")


class OpsScheduler:
    """
    Scheduled operations — integrates with telegram bot JobQueue.
    """

    def __init__(self, chat_id: Optional[int] = None):
        self.chat_id = chat_id or (ADMIN_IDS[0] if ADMIN_IDS else None)
        self._ops = OpsManager()

    def register_jobs(self, app: Application) -> None:
        """Register all scheduled jobs with the bot's JobQueue."""
        if not self.chat_id:
            logger.warning("⚠️ ADMIN_IDS bo'sh — scheduled jobs o'chirilgan")
            return

        jq = app.job_queue

        # Morning briefing — har kuni 07:00 (UTC+5 = 02:00 UTC)
        jq.run_daily(
            self._morning_job,
            time=dt_time(hour=2, minute=0),  # UTC
            name="morning_briefing",
        )

        # Evening report — har kuni 22:00 (UTC+5 = 17:00 UTC)
        jq.run_daily(
            self._evening_job,
            time=dt_time(hour=17, minute=0),  # UTC
            name="evening_report",
        )

        # Daily scan — har kuni 14:00 (UTC+5 = 09:00 UTC)
        jq.run_daily(
            self._daily_scan_job,
            time=dt_time(hour=9, minute=0),  # UTC
            name="daily_scan",
        )

        # Weekly report — har dushanba 08:00 (UTC+5 = 03:00 UTC)
        jq.run_daily(
            self._weekly_job,
            time=dt_time(hour=3, minute=0),  # UTC
            days=(0,),  # Monday
            name="weekly_report",
        )

        logger.info(
            f"✅ 4 ta scheduled job ro'yxatga olindi | "
            f"chat_id={self.chat_id}"
        )

    async def _morning_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Morning briefing job."""
        try:
            logger.info("🌅 Morning briefing ishga tushdi")
            text = await self._ops.morning_briefing()
            await self._send(context, text)
        except Exception as e:
            logger.error(f"Morning job xatosi: {e}")

    async def _evening_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Evening report job."""
        try:
            logger.info("🌙 Evening report ishga tushdi")

            # Avval yangi skan (background thread)
            loop = asyncio.get_event_loop()
            monitor = InstagramMonitor(accounts.active.id)
            await loop.run_in_executor(None, monitor.scan_now)

            # Keyin hisobot
            self._ops = OpsManager()  # Refresh with new data
            text = await self._ops.evening_report()
            await self._send(context, text)
        except Exception as e:
            logger.error(f"Evening job xatosi: {e}")

    async def _daily_scan_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Daily background scan — faqat ma'lumot yangilash."""
        try:
            logger.info("🔄 Daily scan ishga tushdi")
            loop = asyncio.get_event_loop()
            monitor = InstagramMonitor(accounts.active.id)
            state = await loop.run_in_executor(None, monitor.scan_now)

            # Agar bugun post qilinmagan va soat 14:00 dan keyin — ogohlantirish
            if not state.posted_today:
                await self._send(
                    context,
                    "⏰ *ESLATMA*\n\n"
                    "Bugun hali post qilinmadi!\n"
                    f"🔥 Streak: {state.posting_streak} kun\n"
                    "💡 Eng yaxshi vaqt: 19:00-21:00\n\n"
                    "Post qilmasangiz streak yo'qoladi!"
                )
        except Exception as e:
            logger.error(f"Daily scan xatosi: {e}")

    async def _weekly_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Weekly report job."""
        try:
            logger.info("📅 Weekly report ishga tushdi")
            text = await self._ops.weekly_report()
            await self._send(context, text)
        except Exception as e:
            logger.error(f"Weekly job xatosi: {e}")

    async def _send(self, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
        """Xabar yuborish — chunking bilan."""
        if not self.chat_id:
            return
        # 4096 limit
        chunks = []
        while text:
            if len(text) <= 4000:
                chunks.append(text)
                break
            split = text.rfind("\n", 0, 4000)
            if split == -1:
                split = 4000
            chunks.append(text[:split])
            text = text[split:].lstrip("\n")

        for chunk in chunks:
            try:
                await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=chunk,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Xabar yuborishda xato: {e}")

    # ─────────────────────────────────────────────────────
    # MANUAL TRIGGERS (Telegram handler'lardan chaqirish uchun)
    # ─────────────────────────────────────────────────────

    async def trigger_morning(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Qo'lda morning briefing."""
        return await self._ops.morning_briefing()

    async def trigger_evening(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Qo'lda evening report."""
        # Yangi skan
        loop = asyncio.get_event_loop()
        monitor = InstagramMonitor(accounts.active.id)
        await loop.run_in_executor(None, monitor.scan_now)
        self._ops = OpsManager()
        return await self._ops.evening_report()

    async def trigger_weekly(self) -> str:
        """Qo'lda weekly report."""
        return await self._ops.weekly_report()
