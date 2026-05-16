"""
Agro AI — Avtomatik PDF Hisobot
Haftalik (har dushanba 09:00) va Oylik (har oyning 1-kuni) hisobotlar.
PDF yaratib Telegram'ga yuboradi.
"""

import asyncio
import logging
from datetime import datetime, time as dt_time
from typing import Optional

from telegram.ext import Application, ContextTypes

from app.accounts import accounts
from app.export.pdf_report import PDFReportGenerator
from app.memory.manager import memory
from app.settings import ADMIN_IDS

logger = logging.getLogger("agro_ai.ops.auto_report")


class AutoReportScheduler:
    """
    Haftalik va oylik avtomatik PDF hisobot.
    - Haftalik: har dushanba 09:00 (UTC+5 = 04:00 UTC)
    - Oylik: har oyning 1-kuni 09:00 (UTC+5 = 04:00 UTC)
    """

    def __init__(self, chat_id: Optional[int] = None):
        self.chat_id = chat_id or (ADMIN_IDS[0] if ADMIN_IDS else None)

    def register_jobs(self, app: Application) -> None:
        """Scheduled jobs ro'yxatga olish."""
        if not self.chat_id:
            logger.warning("⚠️ ADMIN_IDS bo'sh — auto report o'chirilgan")
            return

        jq = app.job_queue

        # Haftalik PDF — har dushanba 09:00 (UTC+5 = 04:00 UTC)
        jq.run_daily(
            self._weekly_pdf_job,
            time=dt_time(hour=4, minute=0),  # UTC
            days=(0,),  # Monday
            name="weekly_pdf_report",
        )

        # Oylik PDF — har oyning 1-kuni 09:00 (UTC+5 = 04:00 UTC)
        jq.run_daily(
            self._monthly_pdf_job,
            time=dt_time(hour=4, minute=0),  # UTC
            name="monthly_pdf_report",
        )

        logger.info("✅ Auto Report jobs ro'yxatga olindi (weekly + monthly PDF)")

    async def _weekly_pdf_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Haftalik PDF hisobot job."""
        try:
            logger.info("📅 Haftalik PDF hisobot yaratilmoqda...")
            filepath = await self._generate_weekly_pdf()
            if filepath:
                await self._send_pdf(context, filepath, "📅 *HAFTALIK HISOBOT*\n\nO'tgan hafta natijalari:")
            else:
                await self._send_text(context, "⚠️ Haftalik PDF yaratishda xato.")
        except Exception as e:
            logger.error(f"Weekly PDF job xatosi: {e}")

    async def _monthly_pdf_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Oylik PDF hisobot job — faqat oyning 1-kuni."""
        now = datetime.now()
        if now.day != 1:
            return  # Faqat 1-kuni ishlaydi

        try:
            logger.info("📊 Oylik PDF hisobot yaratilmoqda...")
            filepath = await self._generate_monthly_pdf()
            if filepath:
                await self._send_pdf(context, filepath, "📊 *OYLIK HISOBOT*\n\nO'tgan oy umumiy natijalari:")
            else:
                await self._send_text(context, "⚠️ Oylik PDF yaratishda xato.")
        except Exception as e:
            logger.error(f"Monthly PDF job xatosi: {e}")

    async def _generate_weekly_pdf(self) -> Optional[str]:
        """Haftalik PDF yaratish."""
        acc = accounts.active
        pdf_gen = PDFReportGenerator(account_id=acc.id, brand=acc.instagram)

        # Stats olish
        stats = await self._get_current_stats()

        # Memory'dan top/worst
        top_hooks = memory.get_best_patterns(acc.id, "hook", limit=5)
        failed = memory.get_failed_patterns(acc.id, "hook", limit=3)

        # AI tavsiyalar
        recommendations = await self._generate_weekly_recommendations(stats)

        # Ideas
        ideas = []
        for h in top_hooks:
            ideas.append({"title": h.content[:50], "hook": h.content[:100]})

        filepath = pdf_gen.generate_strategy_report(
            stats=stats,
            recommendations=recommendations,
            ideas=ideas,
            title=f"Haftalik Hisobot — {datetime.now().strftime('%d.%m.%Y')}",
        )
        return filepath

    async def _generate_monthly_pdf(self) -> Optional[str]:
        """Oylik PDF yaratish."""
        acc = accounts.active
        pdf_gen = PDFReportGenerator(account_id=acc.id, brand=acc.instagram)

        stats = await self._get_current_stats()

        # Oylik tavsiyalar
        recommendations = await self._generate_monthly_recommendations(stats)

        # Top kontentlar
        all_best = memory.get_best_patterns(acc.id, "hook", limit=10)
        ideas = []
        for h in all_best:
            ideas.append({"title": h.content[:50], "hook": h.content[:100]})

        filepath = pdf_gen.generate_strategy_report(
            stats=stats,
            recommendations=recommendations,
            ideas=ideas,
            title=f"Oylik Hisobot — {datetime.now().strftime('%B %Y')}",
        )
        return filepath

    async def _get_current_stats(self) -> Optional[dict]:
        """Joriy statistikani olish."""
        try:
            from app.ops.monitor import InstagramMonitor
            acc = accounts.active
            monitor = InstagramMonitor(acc.id)
            state = monitor.get_state()
            if state and hasattr(state, "stats"):
                return state.stats
        except Exception as e:
            logger.debug(f"Stats olishda xato: {e}")
        return None

    async def _generate_weekly_recommendations(self, stats: Optional[dict]) -> list:
        """AI orqali haftalik tavsiyalar."""
        try:
            from app.ai.base import BaseAIEngine
            acc = accounts.active
            engine = BaseAIEngine(acc)

            prompt = (
                "Haftalik Instagram hisobot uchun 5 ta qisqa tavsiya yoz:\n"
                "1. O'tgan hafta nima yaxshi ishladi\n"
                "2. Nima yaxshilash kerak\n"
                "3. Kelasi hafta uchun strategiya\n"
                "4. Kontent mix tavsiyasi\n"
                "5. Eng yaxshi post vaqtlari\n\n"
                "Har biri 1-2 gap. O'zbek tilida."
            )
            if stats:
                ctx = engine.build_context(stats)
                result = await engine.generate(prompt, context=ctx, max_tokens=500)
            else:
                result = await engine.generate(prompt, max_tokens=500)

            return [line.strip() for line in result.split("\n") if line.strip()]
        except Exception as e:
            logger.error(f"Weekly recommendations xatosi: {e}")
            return ["Muntazam post qiling", "Hook'larni kuchaytiring", "Trend'larni kuzating"]

    async def _generate_monthly_recommendations(self, stats: Optional[dict]) -> list:
        """AI orqali oylik tavsiyalar."""
        try:
            from app.ai.base import BaseAIEngine
            acc = accounts.active
            engine = BaseAIEngine(acc)

            prompt = (
                "Oylik Instagram strategiya hisoboti uchun 7 ta tavsiya:\n"
                "1. Oylik umumiy baho\n"
                "2. Eng yaxshi kontent turi\n"
                "3. Auditoriya o'sishi tahlili\n"
                "4. Competitor comparison xulosasi\n"
                "5. Content mix optimallashtirish\n"
                "6. Kelasi oy uchun yo'l xaritasi\n"
                "7. O'sish maqsadlari\n\n"
                "Har biri 2-3 gap. O'zbek tilida. Professional."
            )
            if stats:
                ctx = engine.build_context(stats)
                result = await engine.generate(prompt, context=ctx, max_tokens=700)
            else:
                result = await engine.generate(prompt, max_tokens=700)

            return [line.strip() for line in result.split("\n") if line.strip()]
        except Exception as e:
            logger.error(f"Monthly recommendations xatosi: {e}")
            return [
                "Oylik o'sish maqsadlarini belgilang",
                "Kontent mix'ni optimallashtiring",
                "Competitor tahlilini chuqurlashtiring",
            ]

    async def _send_pdf(self, context: ContextTypes.DEFAULT_TYPE, filepath: str, caption: str) -> None:
        """PDF faylni Telegram'ga yuborish."""
        if not self.chat_id:
            return
        try:
            with open(filepath, "rb") as f:
                await context.bot.send_document(
                    chat_id=self.chat_id,
                    document=f,
                    caption=caption,
                    parse_mode="Markdown",
                )
            logger.info(f"📤 PDF yuborildi: {filepath}")
        except Exception as e:
            logger.error(f"PDF yuborishda xato: {e}")
            await self._send_text(context, f"⚠️ PDF yuborishda xato: {e}")

    async def _send_text(self, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
        """Matn yuborish."""
        if not self.chat_id:
            return
        try:
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Xabar yuborishda xato: {e}")

    # ─────────────────────────────────────────────────────
    # MANUAL TRIGGERS
    # ─────────────────────────────────────────────────────

    async def trigger_weekly_pdf(self) -> Optional[str]:
        """Qo'lda haftalik PDF yaratish."""
        return await self._generate_weekly_pdf()

    async def trigger_monthly_pdf(self) -> Optional[str]:
        """Qo'lda oylik PDF yaratish."""
        return await self._generate_monthly_pdf()
