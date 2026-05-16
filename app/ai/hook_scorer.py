"""
Agro AI — Hook Scorer Engine
Score hooks for viral potential, retention, and emotional impact.
"""

import logging
from typing import Dict, Optional

from app.ai.base import BaseAIEngine
from app.memory import memory

logger = logging.getLogger("agro_ai.ai.hook_scorer")


class HookScorerEngine(BaseAIEngine):
    """
    Hook Scorer — hooklar viral potensialini baholash.
    Score: 0-100, tarkibiy qismlar bilan.
    """

    engine_name = "hook_scorer"
    default_max_tokens = 500
    default_temperature = 0.6  # More deterministic for scoring

    def get_system_prompt(self) -> str:
        return (
            "Siz Instagram Reels hook tahlilchisisiz.\n"
            "Vazifangiz: hooklar viral potensialini RAQAMLAR bilan baholash.\n"
            f"Niche: {self.account.niche}\n"
            f"Auditoriya: {self.account.target_audience}\n\n"
            "Baholash mezonlari:\n"
            "- Qiziqish uyg'otish (curiosity gap)\n"
            "- Emotsional ta'sir (fear/surprise/hope)\n"
            "- Aniqlik (nima haqida ekanligi tushunarli)\n"
            "- Retention kuchi (oxirigacha ko'rishga undaydi)\n"
            "- Share potensiali (boshqalarga yuborish istagi)\n"
            "Har bir mezon 1-10. Umumiy 1-100."
        )

    async def score_hook(self, hook: str, stats: Optional[Dict] = None) -> str:
        """Bitta hookni baholash."""
        ctx = self.build_context(stats)

        # Memory'dan eng yaxshi hooklar bilan solishtirish
        top_hooks = memory.get_top_hooks(self.account.id, limit=3)
        comparison = ""
        if top_hooks:
            comparison = "\nEng yaxshi hooklar (solishtirish uchun):\n" + "\n".join(
                f"  [score={h.score}] {h.content[:60]}" for h in top_hooks
            )

        task = (
            f"Quyidagi hookni baholab ber:\n\n"
            f'"{hook}"\n\n'
            f"{comparison}\n\n"
            "FORMAT:\n"
            "📊 UMUMIY BALL: X/100\n\n"
            "Tarkibiy qismlar:\n"
            "🤔 Qiziqish: X/10\n"
            "😱 Emotsiya: X/10\n"
            "🎯 Aniqlik: X/10\n"
            "⏱ Retention: X/10\n"
            "📤 Share: X/10\n\n"
            "💡 Yaxshilash: (1 jumla)\n"
            "✅ Yaxshilangan versiya: (1 ta yangi hook)"
        )
        return await self.generate(task, context=ctx)

    async def compare_hooks(self, hooks: list, stats: Optional[Dict] = None) -> str:
        """Bir nechta hookni solishtirish."""
        ctx = self.build_context(stats)
        hooks_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(hooks[:5]))

        task = (
            f"Quyidagi hooklarni solishtir va eng yaxshisini tanla:\n\n"
            f"{hooks_text}\n\n"
            "Har biri uchun qisqa baho (1-100) va 1 ta sabab.\n"
            "Oxirida: 🏆 ENG YAXSHI va nima uchun."
        )
        return await self.generate(task, context=ctx)

    async def optimize_hook(self, hook: str) -> str:
        """Hookni yaxshilash — 3 ta variant."""
        task = (
            f"Quyidagi hookni YAXSHILASH:\n\n"
            f'Original: "{hook}"\n\n'
            "3 ta yaxshilangan variant yarat:\n"
            "1. Kuchliroq emotsiya bilan\n"
            "2. Ko'proq curiosity bilan\n"
            "3. Qisqaroq va keskinroq\n\n"
            "Har biri 1 qator. Eng yaxshisini ⭐ bilan belgilab ber."
        )
        return await self.generate(task, max_tokens=300)

    def _fallback(self, task: str) -> str:
        return (
            "📊 *HOOK SCORER*\n\n"
            "Hook baholash uchun AI kerak (OPENAI_API_KEY).\n\n"
            "Baholash mezonlari:\n"
            "• Qiziqish (curiosity gap)\n"
            "• Emotsiya (fear/surprise)\n"
            "• Aniqlik\n"
            "• Retention\n"
            "• Share potensiali"
        )
