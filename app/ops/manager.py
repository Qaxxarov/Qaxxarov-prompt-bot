"""
Agro AI — Operations Manager
Morning briefing, evening report, AI-powered recommendations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.accounts import accounts
from app.ai.base import BaseAIEngine
from app.ai.hooks import HookEngine
from app.memory import memory
from app.ops.discipline import DisciplineTracker
from app.ops.monitor import AccountState, InstagramMonitor

logger = logging.getLogger("agro_ai.ops.manager")


class OpsManager:
    """
    AI Operations Manager — morning briefing, evening report,
    real-time recommendations, accountability.
    """

    def __init__(self, account_id: str = None):
        self.account_id = account_id or accounts.active.id
        self.account = accounts.get(self.account_id) or accounts.active
        self.monitor = InstagramMonitor(self.account_id)
        self.discipline = DisciplineTracker()
        self._ai = BaseAIEngine(self.account)
        self._hooks = HookEngine(self.account)

    # ─────────────────────────────────────────────────────
    # MORNING BRIEFING
    # ─────────────────────────────────────────────────────

    async def morning_briefing(self) -> str:
        """
        Ertalabki AI brifing:
        - Akkaunt holati
        - Bugungi prioritetlar
        - Eng yaxshi mavzu tavsiyasi
        - Hook tavsiyasi
        - Post vaqti tavsiyasi
        """
        state = self.monitor.state
        history = self.monitor.get_history(7)
        trend = self.monitor.get_growth_trend(7)
        disc = self.discipline.compute_discipline_score(state, history)

        # Memory'dan eng yaxshi pattern'lar
        top_hooks = memory.get_top_hooks(self.account_id, limit=3)
        hooks_text = "\n".join(f"  • {h.content[:60]}" for h in top_hooks) if top_hooks else "  (hali yo'q)"

        now = datetime.now()
        greeting = "🌅" if now.hour < 12 else "☀️"

        # Statik qism
        header = (
            f"{greeting} *ERTALABKI BRIFING*\n"
            f"📅 {now.strftime('%Y-%m-%d, %A')}\n"
            f"🌿 {self.account.instagram}\n\n"
        )

        status_section = (
            f"📊 *AKKAUNT HOLATI:*\n"
            f"  👥 Followers: {state.followers:,}\n"
            f"  👁 O'rtacha views: {state.avg_views:,}\n"
            f"  📈 ER: {state.avg_er}%\n"
            f"  🔥 Streak: {state.posting_streak} kun\n"
            f"  📋 Intizom: {disc['score']}/100\n\n"
        )

        trend_section = ""
        if trend.get("trend") != "unknown":
            trend_emoji = "📈" if trend["trend"] == "up" else "📉" if trend["trend"] == "down" else "➡️"
            trend_section = (
                f"{trend_emoji} *7 KUNLIK TREND:*\n"
                f"  Followers: {trend['follower_change']:+d}\n"
                f"  Views: {trend['view_change']:+d}\n"
                f"  Izchillik: {trend['consistency']:.0f}%\n\n"
            )

        hooks_section = f"🎣 *TOP HOOKLAR (xotiradan):*\n{hooks_text}\n\n"

        # AI qism — bugungi tavsiyalar
        context = self._ai.build_context()
        context["streak"] = state.posting_streak
        context["avg_views"] = state.avg_views
        context["avg_er"] = state.avg_er
        context["posted_yesterday"] = state.posted_today
        context["discipline_score"] = disc["score"]

        ai_advice = await self._ai.generate(
            "Bugungi kun uchun qisqa brifing:\n"
            "1. Bugun qaysi mavzuda reel qilish kerak? (1 ta aniq tavsiya)\n"
            "2. Eng yaxshi post vaqti?\n"
            "3. Qaysi hook turi ishlaydi bugun?\n"
            "4. CTA tavsiyasi?\n"
            "5. Storytelling tuzilmasi?\n\n"
            "Juda qisqa va aniq. Har biri 1 qator.",
            context=context,
            max_tokens=400,
        )

        return header + status_section + trend_section + hooks_section + f"💡 *BUGUNGI TAVSIYALAR:*\n{ai_advice}"

    # ─────────────────────────────────────────────────────
    # EVENING REPORT
    # ─────────────────────────────────────────────────────

    async def evening_report(self) -> str:
        """
        Kechki AI hisobot:
        - Bugungi natijalar
        - Performance tahlili
        - Accountability
        - Ertangi strategiya
        """
        state = self.monitor.state
        history = self.monitor.get_history(7)
        disc_msg = self.discipline.get_accountability_message(state, history)
        disc_data = self.discipline.compute_discipline_score(state, history)

        now = datetime.now()
        header = (
            f"🌙 *KECHKI HISOBOT*\n"
            f"📅 {now.strftime('%Y-%m-%d')}\n"
            f"🌿 {self.account.instagram}\n\n"
        )

        # Bugungi performance
        perf_section = ""
        if state.posted_today and state.recent_reels:
            latest = state.recent_reels[0]
            perf_label = "🔥 O'rtachadan yuqori!" if latest.views > state.avg_views else "📊 O'rtacha atrofida"
            perf_section = (
                f"📊 *BUGUNGI NATIJA:*\n"
                f"  👁 Views: {latest.views:,}\n"
                f"  ❤️ Likes: {latest.likes:,}\n"
                f"  💬 Comments: {latest.comments}\n"
                f"  📈 ER: {latest.engagement_rate}%\n"
                f"  {perf_label}\n\n"
            )

            # Memory'ga saqlash
            if latest.views > state.avg_views * 1.5:
                hook = latest.caption.split('.')[0] if latest.caption else ""
                if hook:
                    memory.save_memory(
                        self.account_id, "hook", hook,
                        tags=["viral", "today"], score=8.0, source="scraped",
                    )

        # Accountability
        accountability_section = f"📋 *INTIZOM:*\n{disc_msg}\n\n"

        # AI — ertangi strategiya
        context = self._ai.build_context()
        context["today_posted"] = state.posted_today
        context["discipline_score"] = disc_data["score"]
        context["streak"] = state.posting_streak

        ai_tomorrow = await self._ai.generate(
            "Ertangi kun uchun strategiya:\n"
            "1. Qaysi mavzuda post qilish kerak?\n"
            "2. Qaysi hook turi ishlaydi?\n"
            "3. Qaysi vaqtda post qilish?\n"
            "4. Bugungi xatolardan nima o'rganish kerak?\n\n"
            "Juda qisqa, 1 qator har biri.",
            context=context,
            max_tokens=300,
        )

        tomorrow_section = f"🎯 *ERTANGI STRATEGIYA:*\n{ai_tomorrow}"

        return header + perf_section + accountability_section + tomorrow_section

    # ─────────────────────────────────────────────────────
    # QUICK STATUS
    # ─────────────────────────────────────────────────────

    def quick_status(self) -> str:
        """Tezkor holat — skan qilmasdan."""
        state = self.monitor.state
        history = self.monitor.get_history(7)
        disc = self.discipline.compute_discipline_score(state, history)

        if state.last_scan_time == 0:
            return (
                "⚠️ *Hali skan qilinmagan*\n\n"
                "Birinchi skan uchun:\n"
                "📊 TAHLIL → 🔄 Yangi Tahlil"
            )

        hours_ago = state.hours_since_scan
        stale_warning = f"\n⚠️ _(Ma'lumot {hours_ago:.0f} soat oldingi)_" if hours_ago > 6 else ""

        posted_status = "✅ Post qilindi" if state.posted_today else "❌ Hali post qilinmadi"

        return (
            f"📊 *TEZKOR HOLAT*\n\n"
            f"🌿 {self.account.instagram}\n"
            f"👥 {state.followers:,} followers\n"
            f"👁 O'rtacha: {state.avg_views:,} views\n"
            f"📈 ER: {state.avg_er}%\n"
            f"🔥 Streak: {state.posting_streak} kun\n"
            f"📅 Bugun: {posted_status}\n"
            f"📋 Intizom: {disc['score']}/100 {disc['grade']}"
            f"{stale_warning}"
        )

    # ─────────────────────────────────────────────────────
    # WEEKLY REPORT
    # ─────────────────────────────────────────────────────

    async def weekly_report(self) -> str:
        """Haftalik hisobot."""
        state = self.monitor.state
        history = self.monitor.get_history(7)
        trend = self.monitor.get_growth_trend(7)
        disc = self.discipline.compute_discipline_score(state, history)

        posted_days = sum(1 for h in history if h.get("posted_today"))

        header = (
            f"📅 *HAFTALIK HISOBOT*\n"
            f"🌿 {self.account.instagram}\n\n"
            f"📊 *STATISTIKA:*\n"
            f"  📅 Post qilingan kunlar: {posted_days}/7\n"
            f"  🔥 Streak: {state.posting_streak} kun\n"
            f"  👥 Followers: {state.followers:,}\n"
            f"  👁 O'rtacha views: {state.avg_views:,}\n"
            f"  📈 ER: {state.avg_er}%\n"
            f"  📋 Intizom: {disc['score']}/100\n\n"
        )

        trend_section = ""
        if trend.get("trend") != "unknown":
            trend_emoji = "📈" if trend["trend"] == "up" else "📉" if trend["trend"] == "down" else "➡️"
            trend_section = (
                f"{trend_emoji} *TREND:*\n"
                f"  Followers: {trend['follower_change']:+d}\n"
                f"  Views o'zgarishi: {trend['view_change']:+d}\n\n"
            )

        # AI tavsiyalar
        context = self._ai.build_context()
        context["weekly_posts"] = posted_days
        context["streak"] = state.posting_streak
        context["discipline"] = disc["score"]

        ai_section = await self._ai.generate(
            "Haftalik xulosa va keyingi hafta uchun 5 ta tavsiya.\n"
            "Qisqa va aniq. Raqamlar bilan.",
            context=context,
            max_tokens=400,
        )

        return header + trend_section + f"💡 *TAVSIYALAR:*\n{ai_section}"
