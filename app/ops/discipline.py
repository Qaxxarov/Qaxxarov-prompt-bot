"""
Agro AI — Discipline & Accountability Tracker
Posting consistency, streak, missed days, creator score.
"""

import logging
from datetime import datetime
from typing import Dict, List

from app.ops.monitor import AccountState

logger = logging.getLogger("agro_ai.ops.discipline")


class DisciplineTracker:
    """
    Creator discipline scoring va accountability.
    """

    def compute_discipline_score(self, state: AccountState, history: List[Dict]) -> Dict:
        """
        Discipline score hisoblash (0-100).
        Tarkibi:
        - Posting streak (30 ball)
        - Consistency % (30 ball)
        - Posting frequency (20 ball)
        - Timeliness (20 ball)
        """
        breakdown = {}

        # 1. Streak (max 30) — har 7 kun streak = 30 ball
        streak_score = min(30, state.posting_streak * 4.3)
        breakdown["streak"] = round(streak_score, 1)

        # 2. Consistency (max 30) — oxirgi 7 kunda necha kun post qilingan
        recent_7 = history[-7:] if len(history) >= 7 else history
        if recent_7:
            posted_days = sum(1 for h in recent_7 if h.get("posted_today"))
            consistency_pct = posted_days / len(recent_7) * 100
            consistency_score = consistency_pct * 0.3
        else:
            consistency_pct = 0
            consistency_score = 0
        breakdown["consistency"] = round(consistency_score, 1)

        # 3. Frequency (max 20) — haftada nechta post
        recent_posts = sum(1 for h in recent_7 if h.get("posted_today"))
        freq_score = min(20, recent_posts * 4)  # 5 post/hafta = 20 ball
        breakdown["frequency"] = round(freq_score, 1)

        # 4. Timeliness (max 20) — bugun post qilinganmi
        time_score = 20 if state.posted_today else 0
        breakdown["timeliness"] = round(time_score, 1)

        total = min(100, sum(breakdown.values()))

        # Grade
        if total >= 85:
            grade = "🔥 A+ (Ajoyib intizom)"
        elif total >= 70:
            grade = "✅ A (Yaxshi)"
        elif total >= 50:
            grade = "⚠️ B (O'rtacha)"
        elif total >= 30:
            grade = "📉 C (Yaxshilash kerak)"
        else:
            grade = "❌ D (Jiddiy muammo)"

        return {
            "score": round(total),
            "breakdown": breakdown,
            "grade": grade,
            "streak": state.posting_streak,
            "missed_days": state.missed_days,
            "consistency_pct": round(consistency_pct, 1),
        }

    def get_accountability_message(self, state: AccountState, history: List[Dict]) -> str:
        """
        Accountability xabari — qattiq, lekin adolatli.
        """
        score_data = self.compute_discipline_score(state, history)
        score = score_data["score"]
        streak = state.posting_streak
        missed = state.missed_days

        lines = []

        # Bugun post qilinganmi?
        if state.posted_today:
            lines.append("✅ *Bugun post qilindi!* Ajoyib ish!")
            if streak >= 7:
                lines.append(f"🔥 *{streak} kunlik streak!* Davom eting!")
            elif streak >= 3:
                lines.append(f"💪 *{streak} kunlik streak.* Yaxshi yo'nalish!")
        else:
            now_hour = datetime.now().hour
            if now_hour >= 21:
                lines.append("🚨 *BUGUN POST QILINMADI!*")
                lines.append("⚠️ Algoritm sizni unutmoqda.")
                lines.append("📉 Har bir o'tkazilgan kun reach'ni 10-20% kamaytiradi.")
                if missed >= 3:
                    lines.append(f"❌ *{missed} kun ketma-ket o'tkazildi!*")
                    lines.append("🔴 Bu jiddiy muammo — auditoriya sovumoqda.")
            elif now_hour >= 18:
                lines.append("⏰ *Hali post qilinmadi!*")
                lines.append("💡 Eng yaxshi vaqt: 19:00-21:00")
                lines.append("Hoziroq post qiling — kech bo'lmaydi!")
            else:
                lines.append("📋 Bugun hali post qilinmadi.")
                lines.append(f"💡 Tavsiya: {self._suggest_time()} da post qiling.")

        # Streak yo'qolishi haqida ogohlantirish
        if not state.posted_today and streak > 0:
            lines.append(f"\n⚠️ *{streak} kunlik streak yo'qolish xavfi!*")
            lines.append("Bugun post qilmasangiz streak 0 ga tushadi.")

        # Umumiy baho
        lines.append(f"\n📊 *Intizom balli:* {score}/100 — {score_data['grade']}")

        return "\n".join(lines)

    def _suggest_time(self) -> str:
        """Eng yaxshi post vaqtini tavsiya qilish."""
        now_hour = datetime.now().hour
        if now_hour < 7:
            return "07:00"
        elif now_hour < 12:
            return "12:00"
        elif now_hour < 18:
            return "19:00"
        else:
            return "20:00"

    def format_discipline_report(self, state: AccountState, history: List[Dict]) -> str:
        """To'liq intizom hisoboti."""
        data = self.compute_discipline_score(state, history)
        bd = data["breakdown"]

        bar = "█" * (data["score"] // 10) + "░" * (10 - data["score"] // 10)

        bugun_status = "✅ Post qilindi" if state.posted_today else "❌ Hali yoq"
        return (
            f"📋 *INTIZOM HISOBOTI*\n\n"
            f"🏆 *Score: {data['score']}/100*\n"
            f"`[{bar}]`\n"
            f"📊 Daraja: {data['grade']}\n\n"
            f"📋 *Tarkibiy qismlar:*\n"
            f"  🔥 Streak: `{bd['streak']:.0f}/30` ({state.posting_streak} kun)\n"
            f"  📊 Izchillik: `{bd['consistency']:.0f}/30` ({data['consistency_pct']:.0f}%)\n"
            f"  📅 Chastota: `{bd['frequency']:.0f}/20`\n"
            f"  ⏰ Bugungi: `{bd['timeliness']:.0f}/20`\n\n"
            f"📈 *Statistika:*\n"
            f"  🔥 Streak: {state.posting_streak} kun\n"
            f"  ❌ O'tkazilgan: {state.missed_days} kun\n"
            f"  📊 Izchillik: {data['consistency_pct']:.0f}%\n"
            f"  📅 Bugun: {bugun_status}"
        )
