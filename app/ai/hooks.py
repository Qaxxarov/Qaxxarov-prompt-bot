"""
Agro AI — Viral Hook Engine
Kuchli, retention-focused hooklar yaratish.
"""

import logging
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.hooks")


class HookEngine(BaseAIEngine):
    """
    Viral Hook Generator.
    Birinchi 3 soniyada tomoshabinni ushlab turuvchi hooklar yaratadi.
    """

    engine_name = "hooks"
    default_max_tokens = 900
    default_temperature = 0.9

    # Hook kategoriyalari va ularning psixologik asoslari
    CATEGORIES = {
        "fear": {
            "name_uz": "Qo'rquv",
            "emoji": "😱",
            "psychology": "Yo'qotish qo'rquvi — odamlar foyda olishdan ko'ra yo'qotishdan ko'proq qo'rqadi",
            "patterns": [
                "Bu xatoni qilsangiz — {negative_outcome}",
                "Hech kim aytmaydi, lekin {hidden_truth}",
                "{percentage}% {audience} bu xatoni qiladi",
                "Agar {condition} — {consequence}",
                "{time_frame} ichida {bad_thing} bo'ladi, agar...",
            ],
        },
        "curiosity": {
            "name_uz": "Qiziqish",
            "emoji": "🤔",
            "psychology": "Ma'lumot bo'shlig'i — miya javob olmaguncha tinchlanmaydi",
            "patterns": [
                "Hech kim bilmagan {topic} siri",
                "Nima uchun {subject} {unexpected_result}?",
                "Bu usulni bilganlar {benefit}",
                "{authority} yashiradigan {secret}",
                "Oxirigacha ko'ring — {promise}",
            ],
        },
        "surprise": {
            "name_uz": "Hayrat",
            "emoji": "😲",
            "psychology": "Kutilmagan ma'lumot — dopamin chiqaradi, share qilishga undaydi",
            "patterns": [
                "{small_input} dan {big_output} — mumkinmi?",
                "Bu {subject} {timeframe} da {impossible_result}",
                "Hamma noto'g'ri biladi — haqiqat boshqacha",
                "Rekord: {impressive_number} — qanday?",
                "{common_belief} — mif yoki haqiqat?",
            ],
        },
        "benefit": {
            "name_uz": "Foyda",
            "emoji": "💰",
            "psychology": "Aniq foyda va'dasi — vaqt/pul tejash, natija olish",
            "patterns": [
                "{time} da {skill} o'rganing",
                "Bu usul {resource} ni {multiplier}x tejaydi",
                "Bepul va samarali — hoziroq sinab ko'ring",
                "{number} ta {item} — barchasi bepul",
                "Faqat {simple_action} qiling — natija {timeframe} da",
            ],
        },
        "emotional": {
            "name_uz": "Emotsional",
            "emoji": "❤️",
            "psychology": "Hissiy aloqa — empathy va nostalgia eng kuchli triggerlar",
            "patterns": [
                "Otam menga o'rgatgan bu usul...",
                "Birinchi marta {achievement} — his qilish mumkin emas",
                "Hamma 'bo'lmaydi' dedi. Men esa...",
                "{years} yil oldin boshlagan edim. Bugun...",
                "Bu video ko'rib yig'lab yubordim...",
            ],
        },
        "controversy": {
            "name_uz": "Bahsli",
            "emoji": "⚡",
            "psychology": "Bahsli fikr — comment va share portlashi, algoritm boost",
            "patterns": [
                "{popular_method} — eng katta xato",
                "Hamma shunday qiladi, lekin bu NOTO'G'RI",
                "{expensive_thing} vs {cheap_thing} — natija hayratlanarli",
                "Bu fikrimni aytganimda hamma g'azablandi...",
                "{authority} ham xato qiladi — isbotlayman",
            ],
        },
    }

    def get_system_prompt(self) -> str:
        return (
            f"Siz Instagram Reels uchun viral hook yaratish bo'yicha ekspertsiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n"
            f"Auditoriya: {self.account.target_audience}\n\n"
            f"QOIDALAR:\n"
            f"- Har bir hook BIRINCHI 1-2 SONIYADA aytiladi — e'tiborni DARHOL tortishi SHART\n"
            f"- Tomoshabinni DARHOL ushlab turishi kerak — scroll to'xtatsin\n"
            f"- Qisqa, kuchli, emotsional — 10-15 so'z max\n"
            f"- O'zbek tilida, oddiy va tushunarli — fermer tilida\n"
            f"- Curiosity gap yarating — javobni bilish uchun ko'rish kerak\n"
            f"- Raqamlar va aniq natijalar ishlating\n"
            f"- Har bir hook 1-2 qator\n\n"
            f"5 TA VARIANT BER, har biri BOSHQA USLUBDA:\n"
            f"1. SAVOL uslubi (\"Nima uchun...?\")\n"
            f"2. FAKT uslubi (\"90% fermerlar...\")\n"
            f"3. MUAMMO uslubi (\"Bu xatoni qilsangiz...\")\n"
            f"4. SIR uslubi (\"Hech kim bilmaydi...\")\n"
            f"5. RAQAM uslubi (\"3 ta usul...\", \"1 sotixdan 50 kg\")\n\n"
            f"HAR BIR HOOKGA qaysi VIZUAL bilan boshlanishi kerakligini yoz:\n"
            f"(masalan: \"Close-up: sarqaygan pomidor barglari\" yoki \"Wide: hovlida turgan fermer\")\n\n"
            f"YOMON HOOK (BUNDAY QILMA):\n"
            f"- \"Assalomu alaykum, bugun sizlarga...\"\n"
            f"- \"Bugungi videomizda...\"\n"
            f"- Sekin, zerikarli kirish"
        )

    async def generate_hooks(
        self,
        category: str = "viral",
        count: int = 10,
        stats: Optional[Dict] = None,
    ) -> str:
        """Berilgan kategoriyada hooklar yaratish."""
        ctx = self.build_context(stats)

        if category == "viral":
            # Aralash — eng yaxshi hooklar
            task = (
                f"{count} ta eng kuchli viral hook yarat.\n"
                "Har xil kategoriyalardan aralashtir: qo'rquv, qiziqish, hayrat, foyda, emotsional.\n"
                "Har biri birinchi 3 soniyada aytiladi.\n"
                "Qishloq xo'jaligi, urug', hosil, fermer mavzularida.\n"
                "Format: raqamlangan ro'yxat."
            )
        elif category in self.CATEGORIES:
            cat = self.CATEGORIES[category]
            task = (
                f"{count} ta {cat['name_uz'].upper()} asosidagi hook yarat.\n"
                f"Psixologik asos: {cat['psychology']}\n"
                f"Namuna pattern'lar: {', '.join(cat['patterns'][:3])}\n\n"
                "Qishloq xo'jaligi kontekstida. Har biri 1-2 qator.\n"
                "Format: raqamlangan ro'yxat."
            )
        else:
            task = f"{count} ta viral hook yarat. Qishloq xo'jaligi mavzusida."

        return await self.generate(task, context=ctx)

    async def generate_retention_hooks(self, stats: Optional[Dict] = None) -> str:
        """Retention oshiruvchi hooklar — oxirigacha ko'rishga undaydi."""
        ctx = self.build_context(stats)
        task = (
            "10 ta RETENTION hook yarat — tomoshabinni oxirigacha ko'rishga undaydi.\n\n"
            "Texnikalar:\n"
            "- 'Oxirida eng muhimini aytaman...'\n"
            "- 'Ko'pchilik 5-soniyada chiqib ketadi — siz emas'\n"
            "- '3-chi punkt eng muhimi...'\n"
            "- Countdown: '5 ta sir... 5... 4... 3...'\n"
            "- Cliffhanger: 'Lekin eng qizig'i...'\n\n"
            "Qishloq xo'jaligi kontekstida. Har biri 1-2 qator."
        )
        return await self.generate(task, context=ctx)

    async def analyze_hook_strength(self, hook_text: str) -> str:
        """Berilgan hook'ning kuchini tahlil qilish."""
        task = (
            f"Quyidagi hook'ni tahlil qil:\n\n"
            f'"{hook_text}"\n\n'
            "Baholash mezonlari (har biri 1-10):\n"
            "1. Qiziqish darajasi\n"
            "2. Emotsional ta'sir\n"
            "3. Aniqlik\n"
            "4. Retention kuchi\n"
            "5. Viral potensial\n\n"
            "Umumiy ball va yaxshilash tavsiyasi."
        )
        return await self.generate(task, max_tokens=400)

    def _fallback(self, task: str) -> str:
        """AI o'chirilganda agro hooklar."""
        return (
            "🎣 *VIRAL HOOKLAR (Shablon)*\n\n"
            "1. Bu xatoni qilsangiz — hosil yo'qoladi!\n"
            "2. Hech kim bilmagan urug' siri...\n"
            "3. 1 kg urug'dan 50 kg hosil — mumkinmi?\n"
            "4. 90% fermer bu xatoni qiladi\n"
            "5. Nima uchun qo'shniingiz ko'proq hosil oladi?\n"
            "6. Bu o'simlik 3 kunda unib chiqadi\n"
            "7. Yomg'irdan keyin HECH QACHON buni qilmang\n"
            "8. Rekord hosil olgan fermerning 1 ta siri\n"
            "9. Eng arzon urug' eng yaxshi — mif yoki haqiqat?\n"
            "10. 30 soniyada o'rganing — butun mavsumga yetadi\n\n"
            "_(AI yoqilsa — shaxsiylashtirilgan hooklar yaratiladi)_"
        )
