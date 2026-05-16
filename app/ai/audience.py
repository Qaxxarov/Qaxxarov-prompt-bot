"""
Agro AI — Audience Psychology Engine
Auditoriya psixologiyasi, emotsional triggerlar, engagement pattern tahlili.
"""

import logging
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.audience")


class AudienceEngine(BaseAIEngine):
    """
    Audience Psychology Analyzer.
    Maqsadli auditoriyani chuqur tushunish va kontent moslashtirish.
    """

    engine_name = "audience"
    default_max_tokens = 1000
    default_temperature = 0.8

    # O'zbek fermer auditoriyasi psixologik profili
    AUDIENCE_SEGMENTS = {
        "traditional_farmer": {
            "name": "An'anaviy fermer",
            "age": "40-65",
            "pain_points": ["hosil kamligi", "kasalliklar", "suv tanqisligi", "narx tushishi"],
            "motivations": ["oila ta'minlash", "yer saqlash", "tajriba ulashish"],
            "content_preferences": ["amaliy maslahat", "real natijalar", "oddiy tushuntirish"],
            "emotional_triggers": ["faxr", "nostalgia", "xavotir", "umid"],
        },
        "young_farmer": {
            "name": "Yosh fermer",
            "age": "20-35",
            "pain_points": ["bilim yetishmasligi", "kapital", "texnologiya", "bozor topish"],
            "motivations": ["innovatsiya", "daromad", "mustaqillik", "o'sish"],
            "content_preferences": ["trend", "texnologiya", "case study", "motivatsiya"],
            "emotional_triggers": ["ilhom", "raqobat", "muvaffaqiyat", "FOMO"],
        },
        "greenhouse_owner": {
            "name": "Issiqxona egasi",
            "age": "30-55",
            "pain_points": ["harorat boshqaruvi", "kasallik", "narx", "iste'molchi topish"],
            "motivations": ["yuqori hosil", "premium narx", "texnologiya", "eksport"],
            "content_preferences": ["texnik", "raqamlar", "solishtirish", "yangiliklar"],
            "emotional_triggers": ["optimizatsiya", "nazorat", "natija", "innovatsiya"],
        },
        "seed_buyer": {
            "name": "Urug' xaridori",
            "age": "25-60",
            "pain_points": ["sifat kafolati", "narx/sifat", "qayerdan olish", "qaysi nav"],
            "motivations": ["yaxshi hosil", "ishonchli manba", "tejamkorlik"],
            "content_preferences": ["solishtirish", "review", "natija", "tavsiya"],
            "emotional_triggers": ["ishonch", "xavfsizlik", "foyda", "ijtimoiy isbotlash"],
        },
    }

    # Engagement triggerlar
    ENGAGEMENT_TRIGGERS = {
        "question": "Savol berish — comment uyg'otadi",
        "poll": "Tanlov — A yoki B? — debate yaratadi",
        "challenge": "Challenge — 'Siz ham sinab ko'ring'",
        "tag": "Tag — 'Fermer do'stingizni belgilang'",
        "save": "Save — 'Kerak bo'ladi — saqlang'",
        "share": "Share — 'Buni bilmagan do'stingizga yuboring'",
        "controversy": "Bahsli fikr — 'Ko'pchilik xato qiladi'",
        "story": "Shaxsiy hikoya — empathy va connection",
    }

    def get_system_prompt(self) -> str:
        return (
            f"Siz Instagram auditoriya psixologiyasi bo'yicha ekspertsiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n"
            f"Auditoriya: {self.account.target_audience}\n\n"
            f"Vazifangiz:\n"
            f"- Auditoriya segmentlarini tushunish\n"
            f"- Emotsional triggerlarni aniqlash\n"
            f"- Engagement oshirish strategiyalari\n"
            f"- Kontent auditoriyaga moslashtirish\n"
            f"O'zbek tilida, amaliy va aniq."
        )

    async def analyze_audience(self, stats: Optional[Dict] = None) -> str:
        """To'liq auditoriya tahlili."""
        ctx = self.build_context(stats)
        task = (
            "Maqsadli auditoriyaning to'liq psixologik profilini tuz:\n\n"
            "1. DEMOGRAFIYA: yosh, jins, joylashuv, kasb\n"
            "2. MUAMMOLAR: eng katta 5 ta pain point\n"
            "3. MOTIVATSIYALAR: nima ularni harakatga undaydi?\n"
            "4. KONTENT PREFERENSLARI: qanday format yoqadi?\n"
            "5. EMOTSIONAL TRIGGERLAR: qaysi emotsiyalar ishlaydi?\n"
            "6. XARID QARORLARI: qanday qaror qiladi?\n"
            "7. ONLINE XULQI: qachon faol? Qanday platform?\n\n"
            "Qishloq xo'jaligi kontekstida. Amaliy va aniq."
        )
        return await self.generate(task, context=ctx)

    async def get_emotional_triggers(self, stats: Optional[Dict] = None) -> str:
        """Eng samarali emotsional triggerlar tahlili."""
        ctx = self.build_context(stats)
        task = (
            "Fermer auditoriyasi uchun eng samarali 10 ta emotsional trigger:\n\n"
            "Har biri uchun:\n"
            "- Trigger nomi va tavsifi\n"
            "- Qanday ishlatish (misol hook bilan)\n"
            "- Qaysi kontent formatda eng yaxshi ishlaydi\n"
            "- Kutilgan natija (comment/share/save)\n\n"
            "Eng kuchlilaridan boshlang."
        )
        return await self.generate(task, context=ctx)

    async def suggest_engagement_tactics(self, stats: Optional[Dict] = None) -> str:
        """Engagement oshirish taktikalari."""
        ctx = self.build_context(stats)
        task = (
            "Instagram engagement oshirish uchun 10 ta taktika:\n\n"
            "Har biri:\n"
            "- Taktika nomi\n"
            "- Qanday qo'llash (aniq misol)\n"
            "- Kutilgan natija\n"
            "- Qaysi metrikaga ta'sir qiladi\n\n"
            "Fermer auditoriyasi uchun moslashtirilgan.\n"
            "Eng samaralilaridan boshlang."
        )
        return await self.generate(task, context=ctx)

    async def analyze_content_fit(self, content_idea: str, stats: Optional[Dict] = None) -> str:
        """Kontent g'oyasining auditoriyaga mosligini baholash."""
        ctx = self.build_context(stats)
        task = (
            f"Quyidagi kontent g'oyasini auditoriyaga mosligini baholab ber:\n\n"
            f'"{content_idea}"\n\n'
            "Baholash:\n"
            "1. Auditoriya qiziqishi (1-10)\n"
            "2. Emotsional ta'sir (1-10)\n"
            "3. Amaliy foyda (1-10)\n"
            "4. Share potensiali (1-10)\n"
            "5. Sotuv potensiali (1-10)\n\n"
            "Umumiy baho va yaxshilash tavsiyasi."
        )
        return await self.generate(task, context=ctx, max_tokens=500)

    def get_segment_info(self, segment: str) -> Optional[Dict]:
        """Auditoriya segmenti haqida ma'lumot."""
        return self.AUDIENCE_SEGMENTS.get(segment)

    def _fallback(self, task: str) -> str:
        segments = "\n".join(
            f"• *{s['name']}* ({s['age']}): {', '.join(s['pain_points'][:3])}"
            for s in self.AUDIENCE_SEGMENTS.values()
        )
        return (
            "🧠 *AUDITORIYA SEGMENTLARI*\n\n"
            f"{segments}\n\n"
            "💡 *Eng kuchli triggerlar:*\n"
            "• Yo'qotish qo'rquvi (hosil, vaqt)\n"
            "• Faxr (o'z mehnati natijasi)\n"
            "• Umid (yangi texnologiya)\n"
            "• Raqobat (qo'shni ko'proq oladi)\n\n"
            "_(AI yoqilsa — chuqur tahlil yaratiladi)_"
        )
