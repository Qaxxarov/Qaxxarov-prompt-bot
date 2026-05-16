"""
Agro AI — Competitor Intelligence Engine
AI-powered raqobatchi tahlili, pattern extraction, hook detection.
"""

import logging
import re
from typing import Dict, List, Optional

from app.accounts import Account
from app.ai.base import BaseAIEngine
from app.competitors.models import Competitor, CompetitorReel, competitor_db
from app.memory import memory

logger = logging.getLogger("agro_ai.competitors.engine")


class CompetitorEngine(BaseAIEngine):
    """
    Competitor Intelligence — raqobatchilarni tahlil qilish,
    ularning viral pattern'larini aniqlash va o'rganish.
    """

    engine_name = "competitor"
    default_max_tokens = 1000
    default_temperature = 0.75

    def get_system_prompt(self) -> str:
        return (
            "Siz Instagram competitor intelligence ekspertisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n\n"
            "Vazifangiz:\n"
            "- Raqobatchilarning viral pattern'larini aniqlash\n"
            "- Hook va storytelling texnikalarini ajratib olish\n"
            "- Engagement strategiyalarini tahlil qilish\n"
            "- Amaliy tavsiyalar berish\n"
            "O'zbek tilida, aniq va professional."
        )

    # ─────────────────────────────────────────────────────
    # HOOK EXTRACTION
    # ─────────────────────────────────────────────────────

    def extract_hook(self, caption: str) -> str:
        """Caption'dan hook (birinchi jumla) ajratib olish."""
        if not caption:
            return ""
        # Birinchi jumla — nuqta, ! yoki ? gacha
        match = re.match(r'^(.+?[.!?])', caption.strip())
        if match:
            return match.group(1).strip()
        # Birinchi qator
        first_line = caption.strip().split('\n')[0]
        return first_line[:100]

    def detect_format(self, caption: str, views: int = 0, avg_views: int = 0) -> str:
        """Reel formatini aniqlash."""
        cap_lower = (caption or "").lower()

        if any(w in cap_lower for w in ["pov:", "pov ", "point of view"]):
            return "pov"
        if any(w in cap_lower for w in ["oldin", "keyin", "before", "after", "natija"]):
            return "before_after"
        if any(w in cap_lower for w in ["qadam", "step", "qanday", "usul", "yo'l"]):
            return "tutorial"
        if any(w in cap_lower for w in ["hikoya", "story", "bir kun", "hayot"]):
            return "storytelling"
        if any(w in cap_lower for w in ["mif", "xato", "noto'g'ri", "haqiqat"]):
            return "myth_busting"
        if views > 0 and avg_views > 0 and views > avg_views * 2:
            return "viral_unknown"
        return "general"

    def detect_emotional_trigger(self, caption: str) -> str:
        """Emotsional triggerni aniqlash."""
        cap_lower = (caption or "").lower()

        triggers = {
            "fear": ["xato", "yo'qotish", "xavfli", "muammo", "kasallik"],
            "curiosity": ["sir", "bilmagan", "nima uchun", "qanday", "hech kim"],
            "surprise": ["hayrat", "kutilmagan", "rekord", "mumkin emas", "ishonmaysiz"],
            "pride": ["muvaffaqiyat", "natija", "erishdim", "hosil", "faxr"],
            "hope": ["yangi", "imkoniyat", "o'sish", "kelajak", "yaxshi"],
            "urgency": ["hozir", "tez", "kech", "vaqt", "bugun"],
        }

        for trigger, keywords in triggers.items():
            if any(kw in cap_lower for kw in keywords):
                return trigger
        return "neutral"

    # ─────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────

    def analyze_reels(self, reels_data: List[Dict]) -> Competitor:
        """
        Reel ma'lumotlaridan raqobatchi profilini yaratish.
        reels_data: [{"caption": ..., "views": ..., "likes": ..., ...}]
        """
        if not reels_data:
            return Competitor(username="unknown")

        comp_reels: List[CompetitorReel] = []
        all_hooks: List[str] = []
        all_hashtags: List[str] = []
        views_list: List[int] = []

        for rd in reels_data:
            caption = rd.get("caption", "")
            views = rd.get("views", 0)
            likes = rd.get("likes", 0)
            comments = rd.get("comments", 0)
            hashtags = rd.get("hashtags", [])

            hook = self.extract_hook(caption)
            fmt = self.detect_format(caption, views)
            trigger = self.detect_emotional_trigger(caption)

            reel = CompetitorReel(
                url=rd.get("url", ""),
                caption=caption,
                views=views,
                likes=likes,
                comments=comments,
                hashtags=hashtags,
                hook=hook,
                format_type=fmt,
                emotional_trigger=trigger,
                posted_at=rd.get("posted_at", ""),
            )
            comp_reels.append(reel)

            if hook:
                all_hooks.append(hook)
            all_hashtags.extend(hashtags)
            if views > 0:
                views_list.append(views)

        # Statistika
        avg_views = int(sum(views_list) / len(views_list)) if views_list else 0

        # Top hooklar (viral reellardan)
        viral_hooks = [
            r.hook for r in comp_reels
            if r.views > avg_views * 1.5 and r.hook
        ][:10]

        # Top hashtaglar
        from collections import Counter
        top_tags = [tag for tag, _ in Counter(all_hashtags).most_common(10)]

        # Viral pattern'lar
        viral_formats = [
            r.format_type for r in comp_reels
            if r.views > avg_views * 1.5
        ]
        format_counts = Counter(viral_formats)
        patterns = [f"{fmt}: {cnt} ta viral reel" for fmt, cnt in format_counts.most_common(5)]

        # ER hisoblash
        ers = [r.engagement_rate for r in comp_reels if r.views > 0]
        avg_er = round(sum(ers) / len(ers), 2) if ers else 0.0

        return Competitor(
            username=reels_data[0].get("username", "unknown"),
            account_id=self.account.id,
            avg_views=avg_views,
            avg_er=avg_er,
            top_hooks=viral_hooks,
            top_hashtags=top_tags,
            viral_patterns=patterns,
            reels=comp_reels,
        )

    # ─────────────────────────────────────────────────────
    # AI-POWERED ANALYSIS
    # ─────────────────────────────────────────────────────

    async def analyze_competitor(
        self,
        username: str,
        stats: Optional[Dict] = None,
    ) -> str:
        """AI bilan raqobatchi tahlili."""
        # Bazadan oldingi ma'lumotlarni olish
        existing = competitor_db.get(self.account.id, username)
        context = self.build_context(stats)

        if existing and existing.reels:
            context["competitor"] = username
            context["comp_followers"] = existing.followers
            context["comp_avg_views"] = existing.avg_views
            context["comp_avg_er"] = existing.avg_er
            context["comp_top_hooks"] = "; ".join(existing.top_hooks[:5])
            context["comp_viral_patterns"] = "; ".join(existing.viral_patterns[:5])

        task = (
            f"@{username} Instagram akkauntini tahlil qil.\n\n"
            "Quyidagilarni aniqlash kerak:\n"
            "1. KUCHLI TOMONLARI (5 ta)\n"
            "2. ZAIF TOMONLARI (3 ta)\n"
            "3. VIRAL PATTERN'LARI (qaysi format ishlaydi)\n"
            "4. HOOK TEXNIKALARI (qanday hook ishlatadi)\n"
            "5. ENGAGEMENT STRATEGIYASI\n"
            "6. BIZGA DARS (nima o'rganishimiz mumkin)\n"
            "7. USTUNLIK IMKONIYATI (qayerda ulardan yaxshiroq bo'lishimiz mumkin)\n\n"
            "Amaliy va aniq javob ber."
        )
        return await self.generate(task, context=context)

    async def compare_competitors(
        self,
        usernames: List[str],
        stats: Optional[Dict] = None,
    ) -> str:
        """Bir nechta raqobatchini solishtirish."""
        context = self.build_context(stats)
        names = ", ".join(f"@{u}" for u in usernames)

        task = (
            f"Quyidagi akkauntlarni solishtir: {names}\n\n"
            "Solishtirish mezonlari:\n"
            "1. Kontent sifati\n"
            "2. Hook kuchi\n"
            "3. Engagement rate\n"
            "4. Posting chastotasi\n"
            "5. Viral potensial\n"
            "6. Auditoriya aloqasi\n\n"
            f"Bizning akkaunt ({self.account.instagram}) bilan ham solishtir.\n"
            "Jadval formatida, aniq va qisqa."
        )
        return await self.generate(task, context=context, max_tokens=1200)

    async def extract_viral_patterns(
        self,
        username: str,
        stats: Optional[Dict] = None,
    ) -> str:
        """Raqobatchining viral pattern'larini ajratib olish."""
        existing = competitor_db.get(self.account.id, username)
        context = self.build_context(stats)

        extra = ""
        if existing and existing.top_hooks:
            hooks_text = "\n".join(f"  - {h}" for h in existing.top_hooks[:5])
            extra = f"\nMavjud hooklar:\n{hooks_text}"

        task = (
            f"@{username} ning viral kontent pattern'larini tahlil qil:\n\n"
            "1. HOOK FORMULALARI — qanday boshlanadi?\n"
            "2. STORYTELLING TUZILMASI — qanday hikoya qiladi?\n"
            "3. VISUAL USLUB — qanday ko'rinadi?\n"
            "4. CTA TEXNIKASI — qanday harakat chaqiradi?\n"
            "5. EMOTSIONAL TRIGGER — qaysi emotsiyalarni ishlatadi?\n"
            "6. PACING — tezlik va ritm\n"
            "7. RETENTION TEXNIKASI — qanday oxirigacha ushlab turadi?\n"
            f"{extra}\n\n"
            "Har bir pattern uchun aniq misol va qanday qo'llash mumkinligini ko'rsat."
        )
        return await self.generate(task, context=context, max_tokens=1200)

    async def generate_insights(self, stats: Optional[Dict] = None) -> str:
        """Barcha raqobatchilardan umumiy insight'lar."""
        competitors = competitor_db.get_all(self.account.id)
        context = self.build_context(stats)

        if competitors:
            comp_summary = "\n".join(
                f"  @{c.username}: {c.avg_views:,} avg views, {c.avg_er}% ER"
                for c in competitors[:5]
            )
            context["competitors_summary"] = comp_summary
            all_hooks = competitor_db.get_all_hooks(self.account.id)
            if all_hooks:
                context["competitor_hooks"] = "; ".join(all_hooks[:10])

        task = (
            "Barcha raqobatchilar tahlili asosida umumiy insight'lar:\n\n"
            "1. NICHE'DAGI UMUMIY TRENDLAR\n"
            "2. ENG SAMARALI HOOK FORMULALARI\n"
            "3. ENG YAXSHI ISHLAYOTGAN FORMATLAR\n"
            "4. ENGAGEMENT OSHIRISH USULLARI\n"
            "5. BIZNING USTUNLIGIMIZ\n"
            "6. YAXSHILASH KERAK BO'LGAN JOYLAR\n"
            "7. 5 TA AMALIY TAVSIYA\n\n"
            "Raqamlar va dalillar bilan."
        )
        return await self.generate(task, context=context)

    # ─────────────────────────────────────────────────────
    # MEMORY INTEGRATION
    # ─────────────────────────────────────────────────────

    def save_competitor_hooks(self, account_id: str, competitor: Competitor) -> int:
        """Raqobatchi hooklarini xotiraga saqlash."""
        saved = 0
        for hook in competitor.top_hooks:
            memory.save_memory(
                account_id=account_id,
                category="hook",
                content=hook,
                tags=["competitor", competitor.username],
                score=7.0,  # Competitor hooks start at 7
                source="competitor",
                metadata={"from": competitor.username},
            )
            saved += 1
        return saved

    def save_competitor_patterns(self, account_id: str, competitor: Competitor) -> int:
        """Raqobatchi pattern'larini xotiraga saqlash."""
        saved = 0
        for pattern in competitor.viral_patterns:
            memory.save_memory(
                account_id=account_id,
                category="pattern",
                content=pattern,
                tags=["competitor", competitor.username, "viral"],
                score=6.5,
                source="competitor",
                metadata={"from": competitor.username},
            )
            saved += 1
        return saved
