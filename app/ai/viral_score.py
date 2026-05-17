"""
Agro AI — Viral Score Engine
Kontent viral potensialini baholash va bashorat qilish.
"""

import logging
import statistics
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.viral_score")


class ViralScoreEngine(BaseAIEngine):
    """
    Viral Score Analyzer.
    Reels performance'ini baholash, bashorat qilish, va yaxshilash tavsiyalari.
    """

    engine_name = "viral_score"
    default_max_tokens = 800
    default_temperature = 0.7

    # Scoring weights
    WEIGHTS = {
        "engagement_rate": 25,    # ER % → max 25 ball
        "viral_ratio": 20,        # Viral reels % → max 20 ball
        "view_consistency": 15,   # Views barqarorligi → max 15 ball
        "growth_trend": 15,       # O'sish trendi → max 15 ball
        "content_quality": 15,    # Caption, hashtag sifati → max 15 ball
        "posting_frequency": 10,  # Post chastotasi → max 10 ball
    }

    def get_system_prompt(self) -> str:
        return (
            f"Siz Instagram analytics va viral content ekspertisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n\n"
            f"Vazifangiz: kontent performance'ini tahlil qilish,\n"
            f"viral potensialini baholash, va amaliy tavsiyalar berish.\n\n"
            f"SCORING QOIDALARI:\n"
            f"- Uy sharoitida parvarish mavzusi ENG YUQORI ball olsin (isbot: 1.3M views)\n"
            f"- Oddiy tilda, har kim tushuna oladigan kontent YUQORI ball\n"
            f"- Faqat fermerlar uchun tor, ilmiy mavzu PAST ball\n"
            f"- Amaliy, darhol qo'llay oladigan maslahat YUQORI ball\n"
            f"- Mavsumga mos kontent bonus ball olsin\n"
            f"- Hook kuchi — birinchi 2 sekund qanchalik kuchli\n\n"
            f"O'zbek tilida, raqamlar va dalillar bilan."
        )

    def compute_score(self, stats: Dict) -> Dict:
        """
        Viral score hisoblash (0-100).
        Returns: {score, breakdown, grade, recommendations}
        """
        if not stats:
            return {"score": 0, "breakdown": {}, "grade": "N/A", "recommendations": []}

        eng = stats.get("engagement", {})
        views = stats.get("views", {})
        tiers = stats.get("performance_tiers", {})
        content = stats.get("content", {})
        overview = stats.get("overview", {})

        total_reels = overview.get("total_reels_analyzed", 1)
        avg_er = eng.get("average_er", 0)
        viral_count = tiers.get("viral", {}).get("count", 0)
        viral_ratio = viral_count / max(total_reels, 1) * 100

        # ── Har bir komponent uchun ball ──
        breakdown = {}

        # 1. Engagement Rate (max 25)
        er_score = min(25, avg_er * 5)  # 5% ER = 25 ball
        breakdown["engagement_rate"] = round(er_score, 1)

        # 2. Viral Ratio (max 20)
        vr_score = min(20, viral_ratio * 1.5)  # 13%+ viral = 20 ball
        breakdown["viral_ratio"] = round(vr_score, 1)

        # 3. View Consistency (max 15) — std_dev / mean
        avg_v = views.get("average", 0)
        std_v = views.get("std_dev", 0)
        if avg_v > 0:
            cv = std_v / avg_v  # Coefficient of variation
            consistency = max(0, 15 - cv * 10)  # Past CV = past ball
        else:
            consistency = 0
        breakdown["view_consistency"] = round(consistency, 1)

        # 4. Growth Trend (max 15) — max/average ratio
        max_v = views.get("max", 0)
        if avg_v > 0:
            growth_ratio = max_v / avg_v
            growth_score = min(15, growth_ratio * 3)
        else:
            growth_score = 0
        breakdown["growth_trend"] = round(growth_score, 1)

        # 5. Content Quality (max 15)
        has_captions = content.get("reels_with_caption", 0) / max(total_reels, 1)
        avg_hashtags = content.get("avg_hashtags_per_reel", 0)
        quality = has_captions * 8 + min(7, avg_hashtags)
        breakdown["content_quality"] = round(min(15, quality), 1)

        # 6. Posting Frequency (max 10) — total reels as proxy
        freq_score = min(10, total_reels * 0.5)
        breakdown["posting_frequency"] = round(freq_score, 1)

        # ── Jami ──
        total_score = sum(breakdown.values())
        total_score = min(100, max(0, round(total_score)))

        # Grade
        if total_score >= 80:
            grade = "🔥 A+ (Viral Machine)"
        elif total_score >= 65:
            grade = "✅ A (Yaxshi)"
        elif total_score >= 50:
            grade = "📊 B (O'rtacha)"
        elif total_score >= 35:
            grade = "⚠️ C (Yaxshilash kerak)"
        else:
            grade = "❌ D (Jiddiy ishlash kerak)"

        # Recommendations
        recs = self._generate_recommendations(breakdown, stats)

        return {
            "score": total_score,
            "breakdown": breakdown,
            "grade": grade,
            "recommendations": recs,
        }

    def _generate_recommendations(self, breakdown: Dict, stats: Dict) -> List[str]:
        """Score asosida tavsiyalar."""
        recs = []

        if breakdown.get("engagement_rate", 0) < 15:
            recs.append("📈 ER oshiring: CTA qo'shing, savol bering, debate yarating")

        if breakdown.get("viral_ratio", 0) < 10:
            recs.append("🚀 Viral kontent: shok faktlar, before/after, controversy ishlating")

        if breakdown.get("view_consistency", 0) < 8:
            recs.append("📊 Barqarorlik: bir xil sifat va format saqlang")

        if breakdown.get("content_quality", 0) < 8:
            recs.append("📝 Sifat: har doim caption va 5-10 hashtag ishlating")

        if breakdown.get("posting_frequency", 0) < 5:
            recs.append("📅 Chastota: haftada kamida 4-5 ta reel post qiling")

        if not recs:
            recs.append("✅ Ajoyib! Shu yo'nalishda davom eting.")

        return recs

    def format_score_message(self, score_data: Dict) -> str:
        """Score natijasini Telegram uchun formatlash."""
        s = score_data["score"]
        bar = "█" * (s // 10) + "░" * (10 - s // 10)
        breakdown = score_data["breakdown"]

        lines = [
            f"🏆 *VIRAL SCORE: {s}/100*",
            f"`[{bar}]`",
            f"📊 Daraja: {score_data['grade']}\n",
            "📋 *Tarkibiy qismlar:*",
        ]

        labels = {
            "engagement_rate": ("💡 Engagement", 25),
            "viral_ratio": ("🚀 Viral %", 20),
            "view_consistency": ("📊 Barqarorlik", 15),
            "growth_trend": ("📈 O'sish", 15),
            "content_quality": ("📝 Sifat", 15),
            "posting_frequency": ("📅 Chastota", 10),
        }

        for key, (label, max_val) in labels.items():
            val = breakdown.get(key, 0)
            pct = int(val / max_val * 100) if max_val > 0 else 0
            mini_bar = "▓" * (pct // 20) + "░" * (5 - pct // 20)
            lines.append(f"  {label}: `{mini_bar}` {val:.0f}/{max_val}")

        lines.append("\n💡 *Tavsiyalar:*")
        for rec in score_data["recommendations"]:
            lines.append(f"  • {rec}")

        return "\n".join(lines)

    async def predict_viral_potential(self, hook: str, stats: Optional[Dict] = None) -> str:
        """Berilgan hook/konsept uchun viral potensial bashorati."""
        ctx = self.build_context(stats)
        task = (
            f"Quyidagi kontent g'oyasining viral potensialini baholab ber:\n\n"
            f'"{hook}"\n\n'
            "Baholash (har biri 1-10):\n"
            "1. Hook kuchi\n"
            "2. Emotsional ta'sir\n"
            "3. Share qilish ehtimoli\n"
            "4. Comment uyg'otish\n"
            "5. Retention (oxirigacha ko'rish)\n\n"
            "Umumiy viral ball (1-100) va yaxshilash tavsiyasi."
        )
        return await self.generate(task, context=ctx, max_tokens=500)

    def _fallback(self, task: str) -> str:
        return (
            "🏆 *VIRAL SCORE*\n\n"
            "Score hisoblash uchun avval tahlil o'tkazing.\n"
            "📊 TAHLIL → 🔄 Yangi Tahlil\n\n"
            "Score tarkibi:\n"
            "• Engagement Rate (25 ball)\n"
            "• Viral Ratio (20 ball)\n"
            "• View Consistency (15 ball)\n"
            "• Growth Trend (15 ball)\n"
            "• Content Quality (15 ball)\n"
            "• Posting Frequency (10 ball)"
        )
