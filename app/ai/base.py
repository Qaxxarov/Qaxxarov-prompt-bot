"""
Agro AI — Base AI Engine
Barcha AI modullari uchun asos klass.
"""

import logging
from typing import Dict, Optional

from app.accounts import Account
from app.settings import AI_ENABLED, OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger("agro_ai.ai")


class BaseAIEngine:
    """
    Barcha AI modullar uchun asos.
    Har bir modul bu klassdan meros oladi.
    """

    engine_name: str = "base"
    default_max_tokens: int = 800
    default_temperature: float = 0.85

    def __init__(self, account: Account):
        self.account = account

    def get_system_prompt(self) -> str:
        """Account-specific system prompt. Override in subclasses."""
        return self.account.get_system_prompt()

    async def generate(
        self,
        task: str,
        context: Optional[Dict] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        AI javob yaratish.
        AI o'chirilgan bo'lsa — fallback matn qaytaradi.
        """
        if not AI_ENABLED:
            return self._fallback(task)

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=OPENAI_API_KEY)

            # Context qo'shish
            user_msg = task
            if context:
                ctx_lines = [f"- {k}: {v}" for k, v in context.items()]
                user_msg = f"KONTEKST:\n" + "\n".join(ctx_lines) + f"\n\nVAZIFA:\n{task}"

            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=max_tokens or self.default_max_tokens,
                temperature=temperature or self.default_temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI xatosi ({self.engine_name}): {e}")
            return "⚠️ AI vaqtincha ishlamayapti. Keyinroq urinib ko'ring."

    def _fallback(self, task: str) -> str:
        """AI o'chirilganda qaytariladigan matn."""
        return (
            "⚠️ AI o'chirilgan (OPENAI_API_KEY kerak).\n\n"
            f"So'rov: {task[:100]}..."
        )

    def build_context(self, stats: Optional[Dict] = None) -> Dict:
        """Umumiy kontekst yaratish."""
        ctx = {
            "brand": self.account.instagram,
            "niche": self.account.niche,
            "audience": self.account.target_audience,
        }
        if stats:
            ctx["followers"] = stats.get("profile", {}).get("followers", 0)
            ctx["avg_views"] = stats.get("views", {}).get("average", 0)
            ctx["avg_er"] = stats.get("engagement", {}).get("average_er", 0)
            top_tags = stats.get("content", {}).get("top_hashtags", [])
            ctx["top_hashtags"] = ", ".join(h["tag"] for h in top_tags[:5])
        return ctx
