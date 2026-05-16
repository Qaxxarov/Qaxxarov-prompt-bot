"""
Agro AI — Veo Cinematic Prompt Engine
Professional video generation promptlar yaratish.
"""

import logging
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine

logger = logging.getLogger("agro_ai.ai.veo")


class VeoEngine(BaseAIEngine):
    """
    Cinematic Video Prompt Generator.
    Google Veo, Runway, Sora va boshqa video AI uchun promptlar.
    """

    engine_name = "veo"
    default_max_tokens = 1000
    default_temperature = 0.9

    # Cinematic uslublar
    STYLES = {
        "cinematic": {
            "name": "Cinematic",
            "keywords": "cinematic, 4K, shallow depth of field, golden hour, film grain",
            "camera": "smooth gimbal, slow dolly, crane shot",
            "color": "warm tones, orange and teal, filmic color grade",
        },
        "documentary": {
            "name": "Documentary",
            "keywords": "documentary style, natural light, authentic, handheld",
            "camera": "handheld, observational, intimate close-ups",
            "color": "natural colors, slightly desaturated, realistic",
        },
        "epic": {
            "name": "Epic",
            "keywords": "epic, dramatic, wide angle, volumetric lighting, 8K",
            "camera": "drone, sweeping crane, extreme wide",
            "color": "high contrast, dramatic shadows, HDR",
        },
        "intimate": {
            "name": "Intimate",
            "keywords": "intimate, close-up, macro, soft focus, gentle",
            "camera": "macro lens, static, slow push-in",
            "color": "soft pastels, warm highlights, gentle contrast",
        },
        "timelapse": {
            "name": "Timelapse",
            "keywords": "timelapse, hyperlapse, time compression, growth",
            "camera": "locked-off, slider, motorized pan",
            "color": "vivid, high saturation, dynamic range",
        },
    }

    # Agro sahnalar kutubxonasi
    SCENE_LIBRARY = {
        "seed_germination": {
            "title": "Urug' unib chiqishi",
            "visual": "Macro close-up of seed splitting open in dark soil, first white root emerging, then green sprout pushing through earth toward light",
            "mood": "Hope, life, miracle of nature",
            "duration": "5-10s timelapse",
        },
        "golden_harvest": {
            "title": "Oltin hosil",
            "visual": "Wide drone shot over golden wheat field at sunset, farmer walking through touching grain heads, dust particles in warm light",
            "mood": "Pride, achievement, abundance",
            "duration": "8-15s",
        },
        "rain_on_crops": {
            "title": "Yomg'ir va ekinlar",
            "visual": "Slow motion raindrops falling on green leaves, each drop creating tiny splash, camera slowly pulling back to reveal entire field being nourished",
            "mood": "Relief, nourishment, peace",
            "duration": "5-10s",
        },
        "farmer_hands": {
            "title": "Fermer qo'llari",
            "visual": "Extreme close-up of weathered hands gently holding seeds, soil under fingernails, warm backlight creating rim light on skin texture",
            "mood": "Hard work, dedication, connection to earth",
            "duration": "3-5s",
        },
        "greenhouse_morning": {
            "title": "Issiqxona tongi",
            "visual": "First light streaming through greenhouse glass panels, condensation droplets catching light, rows of green plants in soft focus",
            "mood": "New beginning, potential, controlled nature",
            "duration": "5-8s",
        },
        "before_after": {
            "title": "Oldin va keyin",
            "visual": "Split screen or smooth transition: barren dry soil transforms into lush green productive field, same camera angle",
            "mood": "Transformation, proof, satisfaction",
            "duration": "3-5s",
        },
    }

    def get_system_prompt(self) -> str:
        return (
            "Siz professional video production va AI video generation ekspertisiz.\n"
            "Vazifangiz: Google Veo, Runway Gen-3, Sora uchun mukammal promptlar yaratish.\n\n"
            "QOIDALAR:\n"
            "- Har bir prompt ingliz tilida (video AI uchun)\n"
            "- Juda aniq vizual tasvirlar\n"
            "- Kamera harakati, yorug'lik, rang palitra ko'rsating\n"
            "- Mood va atmosfera aniqlang\n"
            "- Qishloq xo'jaligi kontekstida\n"
            "- Cinematic sifat — National Geographic darajasida\n"
            "- Har bir prompt 2-4 jumla, 30-60 so'z"
        )

    async def generate_scene_prompt(
        self,
        scene_type: str,
        style: str = "cinematic",
        custom_details: str = "",
    ) -> str:
        """Bitta sahna uchun video prompt yaratish."""
        style_info = self.STYLES.get(style, self.STYLES["cinematic"])
        scene_info = self.SCENE_LIBRARY.get(scene_type)

        base_context = (
            f"Style: {style_info['keywords']}\n"
            f"Camera: {style_info['camera']}\n"
            f"Color: {style_info['color']}\n"
        )

        if scene_info:
            base_context += f"Scene reference: {scene_info['visual']}\n"

        task = (
            f"Quyidagi parametrlar asosida 3 ta video generation prompt yarat:\n\n"
            f"{base_context}"
            f"{'Additional: ' + custom_details if custom_details else ''}\n\n"
            "Har bir prompt:\n"
            "- Ingliz tilida\n"
            "- 2-4 jumla, 30-60 so'z\n"
            "- Aniq vizual, kamera, yorug'lik, rang\n"
            "- Mood va atmosfera\n"
            "- Qishloq xo'jaligi kontekstida\n\n"
            "Format:\n"
            "Prompt 1: ...\n"
            "Prompt 2: ...\n"
            "Prompt 3: ..."
        )
        return await self.generate(task)

    async def generate_reel_sequence(
        self,
        concept: str,
        duration: int = 30,
        style: str = "cinematic",
    ) -> str:
        """To'liq reel uchun sahna ketma-ketligi promptlari."""
        style_info = self.STYLES.get(style, self.STYLES["cinematic"])
        scene_count = max(3, duration // 5)

        task = (
            f"Quyidagi konsept uchun {scene_count} ta video prompt yarat:\n\n"
            f"KONSEPT: {concept}\n"
            f"DAVOMIYLIK: {duration} soniya\n"
            f"USLUB: {style_info['name']} — {style_info['keywords']}\n\n"
            f"Har bir sahna uchun:\n"
            f"- Sahna raqami va davomiyligi\n"
            f"- VIDEO PROMPT (ingliz tilida, 2-3 jumla)\n"
            f"- Transition (keyingi sahnaga o'tish)\n\n"
            f"Sahnalar mantiqiy ketma-ketlikda bo'lsin.\n"
            f"Birinchi sahna — hook (eng kuchli vizual).\n"
            f"Oxirgi sahna — CTA yoki emotional peak."
        )
        return await self.generate(task, max_tokens=1200)

    async def enhance_prompt(self, basic_prompt: str, style: str = "cinematic") -> str:
        """Oddiy promptni professional darajaga ko'tarish."""
        style_info = self.STYLES.get(style, self.STYLES["cinematic"])

        task = (
            f"Quyidagi oddiy video promptni professional darajaga ko'tar:\n\n"
            f"ORIGINAL: {basic_prompt}\n\n"
            f"USLUB: {style_info['name']}\n"
            f"Keywords: {style_info['keywords']}\n"
            f"Camera: {style_info['camera']}\n"
            f"Color: {style_info['color']}\n\n"
            "Natija:\n"
            "- Ingliz tilida\n"
            "- 3-4 jumla\n"
            "- Aniq kamera harakati\n"
            "- Yorug'lik va rang palitra\n"
            "- Atmosfera va mood\n"
            "- Texture va detallar"
        )
        return await self.generate(task, max_tokens=400)

    def get_scene_library(self) -> Dict:
        """Mavjud sahnalar kutubxonasini qaytarish."""
        return self.SCENE_LIBRARY

    def get_styles(self) -> Dict:
        """Mavjud uslublarni qaytarish."""
        return self.STYLES

    def _fallback(self, task: str) -> str:
        return (
            "🎞 *VEO PROMPT NAMUNALARI*\n\n"
            "*1. Cinematic Harvest:*\n"
            "`Cinematic drone shot over golden wheat fields in Uzbekistan at golden hour. "
            "Slow motion, 4K, warm tones, dust particles in sunlight. "
            "A farmer walks through the field touching wheat heads.`\n\n"
            "*2. Seed Growth:*\n"
            "`Ultra slow timelapse of seed germinating in dark soil. "
            "Macro lens, underground view showing roots, then above ground growth. "
            "Natural lighting progression from dark to bright.`\n\n"
            "*3. Rain Scene:*\n"
            "`Slow motion rain falling on green crop leaves. "
            "Each raindrop creating ripples, macro lens, natural light. "
            "Refreshing, life-giving atmosphere.`\n\n"
            "_(AI yoqilsa — shaxsiy promptlar yaratiladi)_"
        )
