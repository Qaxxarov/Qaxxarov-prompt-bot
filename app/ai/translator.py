"""
Agro AI — Content Translator
O'zbek va rus tilida parallel kontent yaratish.
"""

import logging
from typing import Dict, Optional

from app.accounts import Account
from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.translator")


class ContentTranslator(BaseAIEngine):
    """
    Multi-language kontent yaratish va tarjima.
    O'zbek ↔ Rus tilida parallel kontent.
    """

    engine_name: str = "translator"
    default_max_tokens: int = 1000
    default_temperature: float = 0.7

    LANGUAGES = {
        "uz": "O'zbek tili",
        "ru": "Русский язык",
    }

    def __init__(self, account: Account):
        super().__init__(account)

    async def translate(self, text: str, target_lang: str = "ru") -> str:
        """
        Kontentni boshqa tilga tarjima qilish.
        Hashtag va emoji saqlanadi.
        """
        source_lang = "uz" if target_lang == "ru" else "ru"
        source_name = self.LANGUAGES.get(source_lang, source_lang)
        target_name = self.LANGUAGES.get(target_lang, target_lang)

        prompt = (
            f"Quyidagi Instagram kontentni {source_name} dan {target_name} ga tarjima qil.\n\n"
            f"QOIDALAR:\n"
            f"- Emoji'larni saqla\n"
            f"- Hashtag'larni ikkala tilda yoz (asl + tarjima)\n"
            f"- Instagram uslubini saqla (qisqa, ta'sirli)\n"
            f"- CTA ni moslashtirilgan holda tarjima qil\n"
            f"- Hook kuchini saqla\n\n"
            f"MATN:\n{text}"
        )

        result = await self.generate(prompt, max_tokens=1200)
        return result

    async def generate_bilingual(self, topic: str, content_type: str = "caption") -> str:
        """
        Bir mavzuda ikkala tilda kontent yaratish.
        """
        prompt = (
            f"Mavzu: {topic}\n"
            f"Kontent turi: {content_type}\n\n"
            f"Ikkala tilda Instagram kontent yarat:\n\n"
            f"1. O'ZBEK TILIDA:\n"
            f"- Hook (1 qator)\n"
            f"- Caption (100-150 so'z)\n"
            f"- 10 ta hashtag\n\n"
            f"2. RUS TILIDA:\n"
            f"- Hook (1 qator)\n"
            f"- Caption (100-150 so'z)\n"
            f"- 10 ta hashtag\n\n"
            f"Har ikkala versiya professional, emoji bilan, Instagram uslubida bo'lsin."
        )

        result = await self.generate(prompt, max_tokens=1500)
        return f"🌐 *IKKI TILDA KONTENT*\n\n{result}"

    async def translate_hooks(self, hooks: list, target_lang: str = "ru") -> str:
        """Hook'larni tarjima qilish."""
        hooks_text = "\n".join(f"- {h}" for h in hooks)
        target_name = self.LANGUAGES.get(target_lang, target_lang)

        prompt = (
            f"Quyidagi Instagram hook'larni {target_name} ga tarjima qil.\n"
            f"Hook kuchini va ta'sirini saqla!\n\n"
            f"HOOKLAR:\n{hooks_text}\n\n"
            f"Har bir hook uchun:\n"
            f"- Asl: ...\n"
            f"- Tarjima: ..."
        )

        result = await self.generate(prompt, max_tokens=800)
        return result

    async def adapt_for_language(self, content: str, target_lang: str = "ru") -> str:
        """
        Kontentni boshqa til auditoriyasiga moslash.
        Faqat tarjima emas — madaniy moslash.
        """
        target_name = self.LANGUAGES.get(target_lang, target_lang)

        prompt = (
            f"Quyidagi Instagram kontentni {target_name} auditoriyasiga moslashtirilgan holda qayta yoz.\n\n"
            f"MUHIM:\n"
            f"- Faqat tarjima emas — madaniy moslash\n"
            f"- Mahalliy iboralar ishlat\n"
            f"- Auditoriya psixologiyasiga mos\n"
            f"- Hook kuchini saqla\n"
            f"- Emoji va format saqla\n\n"
            f"ASL KONTENT:\n{content}"
        )

        result = await self.generate(prompt, max_tokens=1200)
        return result
