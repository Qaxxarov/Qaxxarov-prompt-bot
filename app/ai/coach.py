"""
Agro AI — Creator Coach Engine
Daily missions, growth advice, discipline coaching, smart alerts.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine
from app.memory import memory

logger = logging.getLogger("agro_ai.ai.coach")


class CreatorCoachEngine(BaseAIEngine):
    """
    AI Creator Coach — shaxsiy murabbiy.
    Kunlik vazifalar, motivatsiya, qattiq javobgarlik.
    """

    engine_name = "coach"
    default_max_tokens = 600
    default_temperature = 0.85

    def get_system_prompt(self) -> str:
        return (
            "Siz professional Instagram creator coach'siz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n\n"
            "SHAXSIYAT:\n"
            "- Qattiq, lekin adolatli murabbiy\n"
            "- Natijaga yo'naltirilgan\n"
            "- Motivatsion, lekin real\n"
            "- Raqamlar va dalillar bilan gapiradi\n"
            "- Bahona qabul qilmaydi\n"
            "- Muvaffaqiyatni tan oladi\n"
            "O'zbek tilida. Qisqa va kuchli."
        )

    async def daily_missions(self, stats: Optional[Dict] = None) -> str:
        """Bugungi 5 ta vazifa."""
        ctx = self.build_context(stats)
        now = datetime.now()
        ctx["day_of_week"] = now.strftime("%A")
        ctx["hour"] = now.hour

        # Memory'dan o'rganish
        top_hooks = memory.get_top_hooks(self.account.id, limit=3)
        if top_hooks:
            ctx["best_hooks"] = "; ".join(h.content[:50] for h in top_hooks)

        task = (
            "Bugungi 5 ta VAZIFA yarat (creator uchun):\n\n"
            "Har biri:\n"
            "- Emoji + qisqa tavsif (1 qator)\n"
            "- Aniq, o'lchanadigan, bugun bajarilishi mumkin\n\n"
            "Kategoriyalar: kontent yaratish, engagement, o'rganish, tahlil, o'sish.\n"
            "Eng muhimidan boshlang."
        )
        return await self.generate(task, context=ctx)

    async def motivational_push(self, streak: int = 0, posted_today: bool = False) -> str:
        """Motivatsion xabar — holatga qarab."""
        if posted_today and streak >= 7:
            task = (
                f"Creator {streak} kunlik streak'da va bugun post qildi.\n"
                "Qisqa, kuchli MAQTOV xabari yoz. 2-3 jumla. Energetik."
            )
        elif posted_today:
            task = (
                "Creator bugun post qildi. Qisqa motivatsiya ber.\n"
                "Davom etishga undash. 2 jumla."
            )
        elif streak > 0:
            task = (
                f"Creator {streak} kunlik streak'da, lekin BUGUN hali post qilmadi.\n"
                "QATTIQ ogohlantirish: streak yo'qolish xavfi. 2-3 jumla. Urgent."
            )
        else:
            task = (
                "Creator hali post qilmagan va streak yo'q.\n"
                "JUDA QATTIQ motivatsiya. Bahona qabul qilma. 3 jumla."
            )
        return await self.generate(task, max_tokens=150)

    async def content_review(self, caption: str, views: int, avg_views: int) -> str:
        """Post natijasini baholash va tavsiya."""
        performance = "yuqori" if views > avg_views * 1.5 else "past" if views < avg_views * 0.5 else "o'rtacha"
        task = (
            f"Reel natijasini baholab ber:\n"
            f"Caption: \"{caption[:100]}\"\n"
            f"Views: {views:,} (o'rtacha: {avg_views:,})\n"
            f"Performance: {performance}\n\n"
            "Qisqa baho (1-10) va 2 ta yaxshilash tavsiyasi."
        )
        return await self.generate(task, max_tokens=200)

    async def weekly_coaching(self, stats: Optional[Dict] = None, discipline_score: int = 0) -> str:
        """Haftalik coaching sessiyasi."""
        ctx = self.build_context(stats)
        ctx["discipline_score"] = discipline_score

        task = (
            "Haftalik COACHING SESSIYASI:\n\n"
            "1. Bu hafta nima yaxshi bo'ldi? (1 jumla)\n"
            "2. Nima yomon bo'ldi? (1 jumla)\n"
            "3. Keyingi hafta FOKUS nima? (1 aniq maqsad)\n"
            "4. 3 ta AMALIY QADAM (hoziroq boshlash mumkin)\n"
            "5. MOTIVATSIYA (1 kuchli jumla)\n\n"
            "Qattiq va real. Bahona yo'q."
        )
        return await self.generate(task, context=ctx)

    def _fallback(self, task: str) -> str:
        return (
            "🎯 *BUGUNGI VAZIFALAR*\n\n"
            "1. 📹 1 ta reel yozib post qiling\n"
            "2. 💬 10 ta commentga javob bering\n"
            "3. 🔍 3 ta konkurent reelini ko'ring\n"
            "4. 📝 Ertangi reel uchun hook yozing\n"
            "5. 📊 Kechagi reel statistikasini tekshiring\n\n"
            "_(AI yoqilsa — shaxsiy vazifalar yaratiladi)_"
        )
