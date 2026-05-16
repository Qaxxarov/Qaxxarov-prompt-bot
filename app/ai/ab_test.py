"""
Agro AI — A/B Test Engine
Bir mavzu uchun 2-3 variant yaratib, qaysi yaxshi ishlashini tracking.
"""

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.accounts import Account
from app.ai.base import BaseAIEngine
from app.memory.manager import memory
from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.ai.abtest")

ABTEST_DIR = DATA_DIR / "ab_tests"
ABTEST_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ABVariant:
    """A/B test varianti."""
    id: str = ""
    label: str = ""  # "A", "B", "C"
    hook: str = ""
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    selected: bool = False
    result_score: float = 0.0  # 0-10 (foydalanuvchi bahosi)
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"var_{uuid.uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class ABTest:
    """Bitta A/B test."""
    id: str = ""
    topic: str = ""
    account_id: str = ""
    variants: List[ABVariant] = field(default_factory=list)
    status: str = "active"  # "active", "completed", "expired"
    winner_id: str = ""
    created_at: float = 0.0
    completed_at: float = 0.0
    expires_at: float = 0.0  # 48 soatdan keyin

    def __post_init__(self):
        if not self.id:
            self.id = f"test_{uuid.uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = time.time()
        if not self.expires_at:
            self.expires_at = self.created_at + (48 * 3600)  # 48 soat


class ABTestEngine(BaseAIEngine):
    """
    A/B Test AI Engine.
    Bir mavzuga 2-3 variant yaratib, tracking qiladi.
    """

    engine_name: str = "ab_test"
    default_max_tokens: int = 1200
    default_temperature: float = 0.9

    def __init__(self, account: Account):
        super().__init__(account)
        self._tests_path = ABTEST_DIR / f"{account.id}_tests.json"
        self._tests: List[ABTest] = []
        self._load()

    def _load(self) -> None:
        """Testlarni yuklash."""
        if self._tests_path.exists():
            try:
                with open(self._tests_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t_data in data:
                    variants = [ABVariant(**v) for v in t_data.pop("variants", [])]
                    test = ABTest(**t_data, variants=variants)
                    self._tests.append(test)
            except Exception as e:
                logger.error(f"AB test yuklashda xato: {e}")

    def _save(self) -> None:
        """Testlarni saqlash."""
        try:
            data = []
            for t in self._tests:
                t_dict = asdict(t)
                data.append(t_dict)
            with open(self._tests_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"AB test saqlashda xato: {e}")

    async def create_test(self, topic: str, num_variants: int = 3) -> ABTest:
        """
        Yangi A/B test yaratish.
        AI orqali 2-3 variant generatsiya qiladi.
        """
        # AI orqali variantlar yaratish
        labels = ["A", "B", "C"][:num_variants]

        learning_ctx = memory.get_learning_context(self.account.id, "hook", limit=3)
        avoid_ctx = memory.avoid_repetition_context(self.account.id, "hook", limit=5)

        prompt = (
            f"Mavzu: {topic}\n\n"
            f"{num_variants} ta TURLI variant yarat. Har biri boshqacha uslubda:\n\n"
        )
        for i, label in enumerate(labels):
            prompt += f"VARIANT {label}:\n- Hook (1 qator, kuchli)\n- Caption (100-150 so'z)\n- 10 ta hashtag\n\n"

        prompt += (
            "Har bir variant BUTUNLAY boshqacha bo'lsin:\n"
            "- A: Emotsional/shok\n"
            "- B: Foydali/ta'limiy\n"
            "- C: Qiziqarli/trend\n\n"
            "FORMAT (har variant uchun):\n"
            "---VARIANT X---\n"
            "HOOK: ...\n"
            "CAPTION: ...\n"
            "HASHTAGS: #tag1 #tag2 ...\n"
            "---END---"
        )

        if learning_ctx:
            prompt += f"\n\n{learning_ctx}"
        if avoid_ctx:
            prompt += f"\n\n{avoid_ctx}"

        result = await self.generate(prompt, max_tokens=1500)

        # Parse variants
        variants = self._parse_variants(result, labels)

        # Test yaratish
        test = ABTest(
            topic=topic,
            account_id=self.account.id,
            variants=variants,
        )
        self._tests.append(test)
        self._save()

        logger.info(f"✅ A/B test yaratildi: {test.id} ({len(variants)} variant)")
        return test

    def _parse_variants(self, ai_result: str, labels: List[str]) -> List[ABVariant]:
        """AI natijasidan variantlarni ajratish."""
        variants = []

        for label in labels:
            variant = ABVariant(label=label)

            # Oddiy parsing — AI formatiga qarab
            section_start = ai_result.find(f"VARIANT {label}")
            if section_start == -1:
                section_start = ai_result.find(f"variant {label}")
            if section_start == -1:
                # Fallback — bo'laklarga bo'lish
                variant.hook = f"[{label}] {ai_result[:50]}..."
                variant.caption = ai_result[:200]
                variants.append(variant)
                continue

            # Section end
            next_variant = len(ai_result)
            for next_label in labels:
                if next_label != label:
                    pos = ai_result.find(f"VARIANT {next_label}", section_start + 10)
                    if pos != -1 and pos < next_variant:
                        next_variant = pos

            section = ai_result[section_start:next_variant]

            # Hook
            hook_start = section.upper().find("HOOK:")
            if hook_start != -1:
                hook_end = section.find("\n", hook_start)
                variant.hook = section[hook_start + 5:hook_end].strip() if hook_end != -1 else section[hook_start + 5:].strip()

            # Caption
            cap_start = section.upper().find("CAPTION:")
            if cap_start != -1:
                cap_end = section.upper().find("HASHTAG", cap_start)
                if cap_end == -1:
                    cap_end = section.find("---", cap_start)
                variant.caption = section[cap_start + 8:cap_end].strip() if cap_end != -1 else section[cap_start + 8:].strip()

            # Hashtags
            hash_start = section.upper().find("HASHTAG")
            if hash_start != -1:
                hash_line = section[hash_start:]
                hash_end = hash_line.find("\n---")
                if hash_end != -1:
                    hash_line = hash_line[:hash_end]
                # Extract hashtags
                import re
                tags = re.findall(r"#\w+", hash_line)
                variant.hashtags = tags[:15]

            variants.append(variant)

        return variants

    # ─────────────────────────────────────────────────────
    # TEST MANAGEMENT
    # ─────────────────────────────────────────────────────

    def get_active_tests(self) -> List[ABTest]:
        """Faol testlar."""
        now = time.time()
        active = []
        for t in self._tests:
            if t.status == "active":
                if now > t.expires_at:
                    t.status = "expired"
                else:
                    active.append(t)
        self._save()
        return active

    def get_all_tests(self, limit: int = 20) -> List[ABTest]:
        """Barcha testlar."""
        return self._tests[-limit:]

    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Test ID bo'yicha topish."""
        for t in self._tests:
            if t.id == test_id:
                return t
        return None

    def select_variant(self, test_id: str, variant_id: str) -> bool:
        """Foydalanuvchi variantni tanladi (ishlatmoqchi)."""
        test = self.get_test(test_id)
        if not test:
            return False
        for v in test.variants:
            if v.id == variant_id:
                v.selected = True
                self._save()
                return True
        return False

    def record_result(
        self,
        test_id: str,
        variant_id: str,
        score: float,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
    ) -> bool:
        """Variant natijasini yozish."""
        test = self.get_test(test_id)
        if not test:
            return False

        for v in test.variants:
            if v.id == variant_id:
                v.result_score = score
                v.views = views
                v.likes = likes
                v.comments = comments
                v.shares = shares
                break

        # Agar barcha variantlar baholangan bo'lsa — test tugadi
        scored = [v for v in test.variants if v.result_score > 0]
        if len(scored) >= 2:
            # Winner aniqlash
            winner = max(scored, key=lambda v: v.result_score)
            test.winner_id = winner.id
            test.status = "completed"
            test.completed_at = time.time()

            # Memory'ga saqlash — g'olib pattern
            memory.save_memory(
                account_id=self.account.id,
                category="hook",
                content=winner.hook,
                tags=["ab_test", "winner", test.topic[:20]],
                score=winner.result_score,
                source="ab_test",
                metadata={"test_id": test.id, "topic": test.topic},
            )

        self._save()
        return True

    # ─────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        """A/B test statistikasi."""
        total = len(self._tests)
        active = len([t for t in self._tests if t.status == "active"])
        completed = len([t for t in self._tests if t.status == "completed"])

        # Eng ko'p g'olib bo'lgan stil
        winner_labels = []
        for t in self._tests:
            if t.winner_id:
                for v in t.variants:
                    if v.id == t.winner_id:
                        winner_labels.append(v.label)

        from collections import Counter
        label_counts = Counter(winner_labels)
        top_style = label_counts.most_common(1)[0] if label_counts else ("—", 0)

        return {
            "total_tests": total,
            "active": active,
            "completed": completed,
            "expired": total - active - completed,
            "top_winning_style": top_style[0] if top_style else "—",
            "win_count": top_style[1] if top_style else 0,
        }

    def format_test(self, test: ABTest) -> str:
        """Testni chiroyli formatda ko'rsatish."""
        lines = [f"🧪 *A/B TEST: {test.topic}*\n"]
        lines.append(f"📌 Status: {test.status}")
        lines.append(f"🆔 ID: `{test.id}`\n")

        for v in test.variants:
            selected = " ✅" if v.selected else ""
            winner = " 🏆" if v.id == test.winner_id else ""
            lines.append(f"*VARIANT {v.label}*{selected}{winner}")
            lines.append(f"🎣 Hook: _{v.hook[:80]}_")
            if v.result_score > 0:
                lines.append(f"📊 Score: {v.result_score}/10")
            lines.append("")

        if test.status == "active":
            import datetime
            expires = datetime.datetime.fromtimestamp(test.expires_at)
            lines.append(f"⏰ Muddati: {expires.strftime('%d.%m %H:%M')} gacha")

        return "\n".join(lines)
