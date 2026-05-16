"""
Agro AI — Content Pipeline Engine
Full automatic AI content generation workflow.
Input: topic + audience + goal → Output: complete reel package.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine
from app.ai.hooks import HookEngine
from app.ai.storytelling import StorytellingEngine
from app.ai.veo import VeoEngine
from app.accounts import Account
from app.memory import memory

logger = logging.getLogger("agro_ai.ai.pipeline")


@dataclass
class ContentPackage:
    """To'liq kontent paketi — pipeline natijasi."""
    topic: str = ""
    audience: str = ""
    goal: str = ""
    # Generated content
    viral_idea: str = ""
    hook: str = ""
    storytelling_structure: str = ""
    scene_breakdown: str = ""
    veo_prompt: str = ""
    caption: str = ""
    cta: str = ""
    hashtags: List[str] = field(default_factory=list)
    posting_strategy: str = ""
    # Metadata
    estimated_er: str = ""
    viral_score: int = 0
    format_type: str = ""


class ContentPipelineEngine(BaseAIEngine):
    """
    Full Content Pipeline — bir buyruq bilan to'liq reel paketi yaratish.
    Barcha AI engine'larni orchestrate qiladi.
    """

    engine_name = "pipeline"
    default_max_tokens = 1500
    default_temperature = 0.85

    def __init__(self, account: Account):
        super().__init__(account)
        self._hooks = HookEngine(account)
        self._story = StorytellingEngine(account)
        self._veo = VeoEngine(account)

    def get_system_prompt(self) -> str:
        return (
            "Siz Instagram Reels uchun to'liq kontent pipeline ekspertisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n"
            f"Auditoriya: {self.account.target_audience}\n\n"
            "Vazifangiz: berilgan mavzu uchun TO'LIQ reel paketi yaratish.\n"
            "Har bir qism professional va viral-optimized bo'lishi kerak.\n"
            "O'zbek tilida. Cinematic. Emotsional. Amaliy."
        )

    async def generate_full_package(
        self,
        topic: str,
        audience: str = "",
        goal: str = "viral + engagement",
        stats: Optional[Dict] = None,
    ) -> ContentPackage:
        """
        To'liq kontent paketi yaratish.
        Barcha AI engine'larni ketma-ket chaqiradi.
        """
        pkg = ContentPackage(
            topic=topic,
            audience=audience or self.account.target_audience,
            goal=goal,
        )

        ctx = self.build_context(stats)
        ctx["topic"] = topic
        ctx["goal"] = goal

        # Memory'dan o'rganish
        learning = memory.get_learning_context(self.account.id, "hook", limit=3)
        avoid = memory.avoid_repetition_context(self.account.id, "hook", limit=5)

        # ── 1. Viral Idea ──
        idea_result = await self.generate(
            f"'{topic}' mavzusida 1 ta eng kuchli viral reel g'oyasi yarat.\n"
            "Format: sarlavha + 2 jumla tavsif + nima uchun viral.\n"
            f"{learning}\n{avoid}",
            context=ctx, max_tokens=200,
        )
        pkg.viral_idea = idea_result

        # ── 2. Hook ──
        hook_result = await self._hooks.generate(
            f"'{topic}' mavzusida 1 ta eng kuchli hook yarat.\n"
            "Birinchi 3 soniyada aytiladi. Faqat 1 ta, eng yaxshisi.\n"
            f"{learning}",
            context=ctx, max_tokens=100,
        )
        pkg.hook = hook_result

        # ── 3. Storytelling Structure ──
        story_result = await self._story.generate(
            f"'{topic}' mavzusida 25 soniyalik reel ssenariy:\n"
            "Hook (0-3s) → Setup (3-8s) → Climax (8-20s) → CTA (20-25s)\n"
            "Har qism: voiceover matni + kamera ko'rsatma.",
            context=ctx, max_tokens=600,
        )
        pkg.storytelling_structure = story_result

        # ── 4. Scene Breakdown ──
        scene_result = await self._story.generate_shot_plan(
            scene_count=6, style="cinematic", stats=stats,
        )
        pkg.scene_breakdown = scene_result

        # ── 5. Veo Prompt ──
        veo_result = await self._veo.generate(
            f"'{topic}' mavzusida 1 ta cinematic video prompt yarat.\n"
            "Ingliz tilida, 2-3 jumla, aniq vizual + kamera + yorug'lik.",
            max_tokens=150,
        )
        pkg.veo_prompt = veo_result

        # ── 6. Caption + CTA + Hashtags ──
        caption_result = await self.generate(
            f"'{topic}' mavzusida Instagram caption yoz:\n"
            "1. CAPTION (3-4 qator, hook bilan boshlanadi, CTA bilan tugaydi)\n"
            "2. CTA (1 qator, kuchli harakat chaqirig'i)\n"
            "3. HASHTAGLAR (7 ta, niche + trending)\n\n"
            "Format:\nCAPTION: ...\nCTA: ...\nHASHTAGS: #... #... #...",
            context=ctx, max_tokens=300,
        )
        pkg.caption = caption_result

        # ── 7. Posting Strategy ──
        posting_result = await self.generate(
            f"'{topic}' reeli uchun posting strategiya:\n"
            "- Eng yaxshi vaqt\n- Qaysi kunda\n- Birinchi 30 daqiqada nima qilish\n"
            "Faqat 3-4 qator.",
            context=ctx, max_tokens=150,
        )
        pkg.posting_strategy = posting_result

        # Memory'ga saqlash
        if pkg.hook:
            memory.save_memory(
                self.account.id, "hook", pkg.hook,
                tags=["pipeline", topic[:20]], score=6.0, source="generated",
            )

        logger.info(f"✅ Content pipeline tugadi: {topic}")
        return pkg

    def format_package(self, pkg: ContentPackage) -> str:
        """ContentPackage'ni Telegram/dashboard uchun formatlash."""
        return (
            f"🎬 *TO'LIQ KONTENT PAKETI*\n"
            f"📌 Mavzu: _{pkg.topic}_\n"
            f"🎯 Maqsad: _{pkg.goal}_\n\n"
            f"{'═' * 30}\n\n"
            f"💡 *1. VIRAL G'OYA:*\n{pkg.viral_idea}\n\n"
            f"🎣 *2. HOOK:*\n_{pkg.hook}_\n\n"
            f"🎭 *3. SSENARIY:*\n{pkg.storytelling_structure}\n\n"
            f"🎥 *4. KADRLAR:*\n{pkg.scene_breakdown}\n\n"
            f"🎞 *5. VEO PROMPT:*\n`{pkg.veo_prompt}`\n\n"
            f"📝 *6. CAPTION + CTA:*\n{pkg.caption}\n\n"
            f"📅 *7. POSTING:*\n{pkg.posting_strategy}"
        )

    async def quick_package(self, topic: str, stats: Optional[Dict] = None) -> str:
        """Tezkor paket — bitta AI chaqiruv bilan."""
        ctx = self.build_context(stats)
        learning = memory.get_learning_context(self.account.id, "hook", limit=3)

        task = (
            f"'{topic}' mavzusida TO'LIQ REEL PAKETI yarat:\n\n"
            "1. 🎣 HOOK (birinchi 3 soniya, 1 kuchli jumla)\n"
            "2. 🎬 SSENARIY (25s: Hook→Setup→Climax→CTA, har qism 1-2 jumla)\n"
            "3. 🎥 KADRLAR (5 ta: kadr turi + mazmun)\n"
            "4. 🎞 VEO PROMPT (ingliz, 2 jumla, cinematic)\n"
            "5. 📝 CAPTION (3 qator + CTA)\n"
            "6. #️⃣ HASHTAGLAR (7 ta)\n"
            "7. ⏰ ENG YAXSHI VAQT\n\n"
            f"{learning}\n"
            "Har bir qism aniq va professional."
        )
        return await self.generate(task, context=ctx, max_tokens=1200)

    def _fallback(self, task: str) -> str:
        return (
            "🎬 *KONTENT PIPELINE*\n\n"
            "AI yoqilmagan. Pipeline ishlashi uchun OPENAI_API_KEY kerak.\n\n"
            "Pipeline yaratadi:\n"
            "• Viral g'oya\n• Hook\n• Ssenariy\n• Kadrlar\n"
            "• Veo prompt\n• Caption\n• CTA\n• Hashtaglar\n• Posting vaqti"
        )
