"""
Agro AI — Storytelling Engine
Emotsional, cinematic hikoya tuzilmalari yaratish.
"""

import logging
from typing import Dict, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.storytelling")


class StorytellingEngine(BaseAIEngine):
    """
    Emotsional storytelling va reel ssenariy yaratish.
    Cinematic arc, emotional triggers, va retention-optimized tuzilmalar.
    """

    engine_name = "storytelling"
    default_max_tokens = 1200
    default_temperature = 0.88

    # Hikoya tuzilmalari
    STORY_ARCS = {
        "transformation": {
            "name": "Transformatsiya",
            "structure": "Muammo → Kurash → Yechim → Natija",
            "duration": "25-45s",
            "emotional_flow": "Tushkunlik → Umid → Harakat → G'alaba",
        },
        "revelation": {
            "name": "Kashfiyot",
            "structure": "Savol → Izlanish → Kashfiyot → Ta'sir",
            "duration": "15-30s",
            "emotional_flow": "Qiziqish → Hayrat → Tushunish → Ilhom",
        },
        "conflict": {
            "name": "Ziddiyat",
            "structure": "Muammo → Ikkilanish → Qaror → Natija",
            "duration": "30-60s",
            "emotional_flow": "Xavotir → Stress → Qaroriylik → Yengillik",
        },
        "journey": {
            "name": "Sayohat",
            "structure": "Boshlash → Qiyinchilik → O'sish → Manzil",
            "duration": "30-45s",
            "emotional_flow": "Umid → Qo'rquv → Chidamlilik → Faxr",
        },
        "micro": {
            "name": "Mikro-hikoya",
            "structure": "Hook → Fakt → Natija",
            "duration": "7-15s",
            "emotional_flow": "Hayrat → Tushunish → Harakat",
        },
    }

    # Emotsional triggerlar
    EMOTIONAL_TRIGGERS = {
        "fear_of_loss": "Yo'qotish qo'rquvi — hosil, vaqt, pul",
        "pride": "Faxr — o'z mehnati natijasi",
        "nostalgia": "Nostalgia — ota-bobolar usullari",
        "hope": "Umid — yangi texnologiya, yangi imkoniyat",
        "surprise": "Hayrat — kutilmagan natija",
        "belonging": "Tegishlilik — fermerlar jamoasi",
        "achievement": "Erishish — rekord hosil, muvaffaqiyat",
        "empathy": "Hamdardlik — boshqa fermerning qiyinchiligi",
    }

    def get_system_prompt(self) -> str:
        return (
            f"Siz Instagram Reels uchun cinematic storytelling va ssenariy yozuvchisisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n"
            f"Auditoriya: {self.account.target_audience}\n\n"
            f"═══ SSENARIY FORMATI ═══\n"
            f"Har bir ssenariy KADR-BO'YICHA bo'lishi SHART:\n\n"
            f"KADR 1:\n"
            f"- Vaqt: 0:00-0:03\n"
            f"- Lokatsiya: (aniq joy — hovli, issiqxona, oshxona, bozor, dala, balkon)\n"
            f"- Personaj: (nima qilyapti, qanday pozada, yuz ifodasi)\n"
            f"- Matn/Voiceover: (aniq so'zlar)\n"
            f"- Vizual: (kamera burchagi, yaqin/uzoq plan, harakat)\n"
            f"- Musiqa/Ovoz: (qanday fon, sound effect)\n\n"
            f"KADR 2: ... (xuddi shunday davom etadi)\n\n"
            f"═══ PERSONAJ ═══\n"
            f"Maymun-fermer personaj (AI generated):\n"
            f"- Somon shlyapa, kletchatka ko'ylak, jeans kombinezon\n"
            f"- Sodda, do'stona, hazilkash — xalqqa yaqin fermer obrazi\n"
            f"- Har kadrda personajning pozasi, yuz ifodasi, harakati ANIQ yozilsin\n\n"
            f"═══ LOKATSIYA VARIANTLARI ═══\n"
            f"hovli, issiqxona, bozor, oshxona, dala, balkon, uy ichi, do'kon\n\n"
            f"═══ QOIDALAR ═══\n"
            f"- 5-12 kadr (15-60 sekundlik reel uchun)\n"
            f"- Hook — birinchi 1-2 sekundda e'tiborni tortadigan gap\n"
            f"- Personaj har kadrda faol\n"
            f"- CTA (call to action) — oxirida aniq ko'rsatma\n"
            f"- Musiqa/sound effect har kadr uchun tavsiya\n"
            f"- O'zbek tilida, sodda, xalq tili\n"
            f"- Cinematic, emotsional, hissiy\n"
            f"- Qisqa jumlalar, kuchli tasvirlar\n"
            f"- Retention uchun cliffhanger va curiosity gap"
        )

    async def generate_story(
        self,
        arc_type: str = "transformation",
        topic: Optional[str] = None,
        stats: Optional[Dict] = None,
    ) -> str:
        """To'liq reel ssenariy yaratish."""
        arc = self.STORY_ARCS.get(arc_type, self.STORY_ARCS["transformation"])
        ctx = self.build_context(stats)

        topic_line = f"Mavzu: {topic}" if topic else "Mavzu: urug' parvarishi yoki hosil ko'paytirish"

        task = (
            f"To'liq reel ssenariy yoz.\n\n"
            f"HIKOYA TURI: {arc['name']}\n"
            f"TUZILMA: {arc['structure']}\n"
            f"DAVOMIYLIK: {arc['duration']}\n"
            f"EMOTSIONAL OQIM: {arc['emotional_flow']}\n"
            f"{topic_line}\n\n"
            f"FORMAT:\n"
            f"Har bir qism uchun:\n"
            f"- Vaqt oralig'i (masalan: 0-3s)\n"
            f"- VOICEOVER matni (aniq so'zlar)\n"
            f"- KAMERA ko'rsatmasi (kadr turi, burchak, harakat)\n"
            f"- EMOTSIYA (tomoshabin nima his qiladi)\n"
            f"- MUSIQA holati (tez/sekin, baland/past)\n\n"
            f"Oxirida: Caption va 5 ta hashtag."
        )
        return await self.generate(task, context=ctx)

    async def generate_emotional_script(
        self,
        trigger: str = "pride",
        stats: Optional[Dict] = None,
    ) -> str:
        """Emotsional trigger asosida ssenariy."""
        trigger_desc = self.EMOTIONAL_TRIGGERS.get(trigger, "Emotsional ta'sir")
        ctx = self.build_context(stats)

        task = (
            f"Emotsional reel ssenariy yoz.\n\n"
            f"ASOSIY TRIGGER: {trigger_desc}\n\n"
            f"Tuzilma:\n"
            f"1. HOOK (0-3s) — emotsiyani darhol his qildirish\n"
            f"2. SETUP (3-10s) — vaziyatni ko'rsatish\n"
            f"3. CLIMAX (10-20s) — eng kuchli emotsional nuqta\n"
            f"4. RESOLUTION (20-25s) — yechim yoki xulosa\n"
            f"5. CTA (25-30s) — harakat chaqirig'i\n\n"
            f"Har qism uchun: voiceover + kamera + emotsiya.\n"
            f"Fermer hayotidan real, samimiy hikoya."
        )
        return await self.generate(task, context=ctx)

    async def generate_shot_plan(
        self,
        scene_count: int = 10,
        style: str = "cinematic",
        stats: Optional[Dict] = None,
    ) -> str:
        """Kadrlar rejasi (shot list) yaratish."""
        ctx = self.build_context(stats)

        task = (
            f"{scene_count} ta kadrdan iborat SHOT LIST yarat.\n\n"
            f"USLUB: {style}\n\n"
            f"Har bir kadr uchun:\n"
            f"- Kadr raqami\n"
            f"- Kadr turi (wide/medium/close-up/macro/drone/tracking)\n"
            f"- Burchak (eye-level/low-angle/high-angle/bird's-eye)\n"
            f"- Harakat (static/pan/tilt/dolly/handheld)\n"
            f"- Mazmun (nimani ko'rsatadi)\n"
            f"- Davomiylik (soniya)\n"
            f"- Yorug'lik (natural/golden-hour/backlit/dramatic)\n\n"
            f"Qishloq xo'jaligi mavzusida. Cinematic sifatda."
        )
        return await self.generate(task, context=ctx)

    async def generate_scene_breakdown(
        self,
        concept: str,
        duration: int = 30,
    ) -> str:
        """Berilgan konsept uchun sahna bo'linmasi."""
        task = (
            f"Quyidagi konsept uchun {duration} soniyalik reel sahna bo'linmasi yoz:\n\n"
            f"KONSEPT: {concept}\n\n"
            f"Har bir sahna uchun:\n"
            f"- Vaqt (masalan: 0:00-0:03)\n"
            f"- Vizual (nima ko'rinadi)\n"
            f"- Audio (voiceover yoki musiqa)\n"
            f"- Matn overlay (ekranda yozuv)\n"
            f"- Transition (keyingi sahnaga o'tish)\n\n"
            f"Cinematic, professional, Instagram Reels uchun optimallashtirilgan."
        )
        return await self.generate(task, max_tokens=1000)

    def _fallback(self, task: str) -> str:
        return (
            "🎭 *SSENARIY SHABLON*\n\n"
            "*[0-3s — HOOK]*\n"
            "\"Bu xatoni qilsangiz — hosil yo'qoladi!\"\n"
            "_(Close-up: fermer yuzi, jiddiy)_\n\n"
            "*[3-10s — MUAMMO]*\n"
            "\"Ko'pchilik urug'ni noto'g'ri saqlaydi...\"\n"
            "_(Medium: noto'g'ri saqlash ko'rsatiladi)_\n\n"
            "*[10-22s — YECHIM]*\n"
            "\"To'g'ri usul: quruq, salqin, germetik\"\n"
            "_(Step-by-step: to'g'ri saqlash)_\n\n"
            "*[22-25s — CTA]*\n"
            "\"Do'stingizga yuboring!\"\n"
            "_(Kameraga qarab, tabassum)_\n\n"
            "_(AI yoqilsa — shaxsiy ssenariy yaratiladi)_"
        )
