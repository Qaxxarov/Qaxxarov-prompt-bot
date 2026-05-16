"""
Agro AI — Hashtag Intelligence Engine
Smart hashtag generation, analysis, and optimization.
"""

import logging
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.hashtags")


class HashtagEngine(BaseAIEngine):
    """
    Hashtag Intelligence — optimal hashtag sets yaratish.
    Niche + trending + branded + reach optimization.
    """

    engine_name = "hashtags"
    default_max_tokens = 600
    default_temperature = 0.75

    # Agro niche hashtag bazasi
    NICHE_HASHTAGS = {
        "core": ["#agro", "#fermer", "#hosil", "#urug", "#dehqonchilik", "#qishloqxojaligi"],
        "product": ["#urug_sotish", "#sifatli_urug", "#gibrid_urug", "#issiqxona_urug"],
        "topic": ["#tuproq", "#sug'orish", "#o'g'it", "#kasallik", "#zararkunanda"],
        "location": ["#uzbekistan", "#toshkent", "#samarqand", "#fargona"],
        "trending": ["#agrotips", "#farmlife", "#greenhouse", "#organic", "#harvest"],
        "branded": ["#agro_uruglar_", "#agro_uruglar"],
    }

    def get_system_prompt(self) -> str:
        return (
            "Siz Instagram hashtag strategiyasi ekspertisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n\n"
            "QOIDALAR:\n"
            "- Har bir set 7-12 ta hashtag\n"
            "- Mix: 3 katta (1M+) + 4 o'rta (10K-1M) + 3 kichik (<10K)\n"
            "- Niche-specific + trending + branded\n"
            "- O'zbek + ingliz aralash\n"
            "- Har safar YANGI kombinatsiya"
        )

    async def generate_set(
        self,
        topic: str,
        style: str = "mixed",
        stats: Optional[Dict] = None,
    ) -> str:
        """Mavzuga mos hashtag seti yaratish."""
        ctx = self.build_context(stats)
        ctx["topic"] = topic

        task = (
            f"'{topic}' mavzusida Instagram reel uchun HASHTAG SETI yarat:\n\n"
            "Format:\n"
            "🔵 KATTA (1M+ post): 3 ta\n"
            "🟡 O'RTA (10K-1M): 4 ta\n"
            "🟢 KICHIK (<10K, niche): 3 ta\n"
            "🏷 BRANDED: 2 ta\n\n"
            "Jami 12 ta. Har biri # bilan. Qishloq xo'jaligi niche'ida."
        )
        return await self.generate(task, context=ctx)

    async def analyze_hashtags(self, hashtags: List[str]) -> str:
        """Mavjud hashtaglarni tahlil qilish."""
        tags_text = " ".join(hashtags[:15])
        task = (
            f"Quyidagi hashtaglarni tahlil qil:\n{tags_text}\n\n"
            "Baholash:\n"
            "1. Reach potensiali (1-10)\n"
            "2. Niche mosligi (1-10)\n"
            "3. Raqobat darajasi (past/o'rta/yuqori)\n"
            "4. Yaxshilash tavsiyasi\n"
            "5. Almashtirish kerak bo'lganlar"
        )
        return await self.generate(task, max_tokens=400)

    async def trending_hashtags(self) -> str:
        """Hozirgi trending agro hashtaglar."""
        task = (
            "Hozirgi Instagram'da qishloq xo'jaligi bo'yicha TRENDING hashtaglar:\n\n"
            "15 ta hashtag:\n"
            "- 5 ta global trending\n"
            "- 5 ta O'zbekiston trending\n"
            "- 5 ta niche trending\n\n"
            "Har biri: hashtag + taxminiy post soni + nima uchun trending."
        )
        return await self.generate(task)

    def get_quick_set(self, topic: str = "general") -> List[str]:
        """Tezkor hashtag seti (AI kerak emas)."""
        base = self.NICHE_HASHTAGS["core"][:3]
        branded = self.NICHE_HASHTAGS["branded"][:1]
        trending = self.NICHE_HASHTAGS["trending"][:3]

        topic_tags = self.NICHE_HASHTAGS.get("topic", [])[:2]
        if self.account.hashtags:
            topic_tags = self.account.hashtags[:3]

        return base + trending + topic_tags + branded

    def _fallback(self, task: str) -> str:
        quick = self.get_quick_set()
        return (
            "🏷 *HASHTAG SETI*\n\n"
            f"{' '.join(quick)}\n\n"
            "_(AI yoqilsa — mavzuga mos set yaratiladi)_"
        )
