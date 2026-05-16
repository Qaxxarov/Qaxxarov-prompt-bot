"""
Agro AI — DM Auto-Reply
Tez-tez so'raladigan savollarga javob bazasi.

ESLATMA: Instagram Graph API Business account talab qiladi.
Hozircha FAQ bazasi va logikani tayyorlaymiz.
API integratsiyani keyinroq ulash mumkin.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.dm.auto_reply")

FAQ_FILE = DATA_DIR / "faq.json"


@dataclass
class FAQEntry:
    """Bitta FAQ yozuvi."""
    id: str = ""
    keywords: List[str] = field(default_factory=list)
    response: str = ""
    category: str = ""
    use_count: int = 0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"faq_{int(time.time() * 1000)}"
        if not self.created_at:
            self.created_at = time.time()


class DMAutoReply:
    """
    DM avtomatik javob tizimi.
    - FAQ bazasidan keyword matching
    - AI fallback (FAQ'da javob topilmasa)
    - Bot orqali FAQ qo'shish/tahrirlash

    ESLATMA: Instagram Graph API Business account talab qiladi.
    Hozircha FAQ bazasi va logika tayyor — API integratsiya keyinroq.
    """

    def __init__(self):
        self._faqs: List[FAQEntry] = []
        self._load()

    def _load(self) -> None:
        """FAQ bazasini yuklash."""
        if FAQ_FILE.exists():
            try:
                with open(FAQ_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t_data in data.get("triggers", []):
                    faq = FAQEntry(**t_data)
                    self._faqs.append(faq)
                logger.info(f"📋 {len(self._faqs)} ta FAQ yuklandi")
            except Exception as e:
                logger.error(f"FAQ yuklashda xato: {e}")
                self._create_defaults()
        else:
            self._create_defaults()

    def _create_defaults(self) -> None:
        """Default FAQ'lar yaratish."""
        defaults = [
            FAQEntry(
                keywords=["narx", "narxi", "qancha", "price", "necha"],
                response=(
                    "Assalomu alaykum! 🌿\n\n"
                    "Narxlar haqida ma'lumot:\n"
                    "🌱 Pomidor urug'lari: 25,000 so'mdan\n"
                    "🥒 Bodring urug'lari: 30,000 so'mdan\n"
                    "🌶 Qalampir urug'lari: 20,000 so'mdan\n\n"
                    "To'liq katalog uchun bio'dagi linkni bosing! 👆"
                ),
                category="pricing",
            ),
            FAQEntry(
                keywords=["yetkazish", "dostavka", "delivery", "pochta"],
                response=(
                    "📦 Yetkazib berish:\n\n"
                    "✅ Butun O'zbekiston bo'ylab yetkazamiz!\n"
                    "🚚 Toshkent: 1-2 kun\n"
                    "🚛 Viloyatlar: 2-4 kun\n"
                    "💰 50,000+ buyurtmada BEPUL yetkazish!\n\n"
                    "Buyurtma berish uchun DM yozing yoki bio'dagi linkni bosing."
                ),
                category="delivery",
            ),
            FAQEntry(
                keywords=["buyurtma", "order", "olish", "sotib"],
                response=(
                    "🛒 Buyurtma berish:\n\n"
                    "1️⃣ Mahsulotni tanlang\n"
                    "2️⃣ Miqdorni yozing\n"
                    "3️⃣ Manzilni yuboring\n"
                    "4️⃣ To'lov usulini tanlang\n\n"
                    "Yoki bio'dagi link orqali buyurtma bering! 👆"
                ),
                category="order",
            ),
            FAQEntry(
                keywords=["parvarish", "qanday", "o'stirish", "ekiladi"],
                response=(
                    "🌱 Parvarish bo'yicha maslahat:\n\n"
                    "Qaysi ekin haqida bilmoqchisiz?\n"
                    "• Pomidor\n"
                    "• Bodring\n"
                    "• Qalampir\n"
                    "• Sabzi\n\n"
                    "Ekin nomini yozing — batafsil ma'lumot yuboramiz! 📚"
                ),
                category="care",
            ),
            FAQEntry(
                keywords=["hamkorlik", "reklama", "cooperation", "ads"],
                response=(
                    "🤝 Hamkorlik uchun:\n\n"
                    "Biz bilan hamkorlik qilmoqchimisiz?\n"
                    "📧 Email: info@example.com\n"
                    "📱 Tel: +998 XX XXX XX XX\n\n"
                    "Taklifingizni yozing — 24 soat ichida javob beramiz!"
                ),
                category="cooperation",
            ),
        ]
        self._faqs = defaults
        self._save()

    def _save(self) -> None:
        """FAQ bazasini saqlash."""
        try:
            data = {"triggers": [asdict(f) for f in self._faqs]}
            FAQ_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(FAQ_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"FAQ saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # MATCHING
    # ─────────────────────────────────────────────────────

    def find_response(self, message: str) -> Optional[FAQEntry]:
        """
        Xabarga mos FAQ topish (keyword matching).
        Returns: FAQEntry yoki None (AI fallback kerak).
        """
        message_lower = message.lower().strip()
        words = set(message_lower.split())

        best_match = None
        best_score = 0

        for faq in self._faqs:
            # Keyword matching score
            score = 0
            for keyword in faq.keywords:
                if keyword.lower() in message_lower:
                    score += 2  # Substring match
                if keyword.lower() in words:
                    score += 1  # Word match

            if score > best_score:
                best_score = score
                best_match = faq

        if best_match and best_score >= 2:
            best_match.use_count += 1
            self._save()
            return best_match

        return None

    async def get_ai_response(self, message: str) -> str:
        """
        FAQ'da javob topilmasa — AI javob yaratish.
        """
        try:
            from app.accounts import accounts
            from app.ai.base import BaseAIEngine

            acc = accounts.active
            engine = BaseAIEngine(acc)

            prompt = (
                f"Instagram DM'da foydalanuvchi quyidagini so'radi:\n"
                f"\"{message}\"\n\n"
                f"Qisqa, do'stona, professional javob yoz.\n"
                f"Agro urug'lar do'koni sifatida javob ber.\n"
                f"Emoji ishlat. 2-3 gap yetarli."
            )

            result = await engine.generate(prompt, max_tokens=200)
            return result

        except Exception as e:
            logger.error(f"AI DM response xatosi: {e}")
            return (
                "Rahmat savolingiz uchun! 🌿\n"
                "Tez orada javob beramiz. Bio'dagi linkdan to'liq ma'lumot olishingiz mumkin."
            )

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def add_faq(self, keywords: List[str], response: str, category: str = "general") -> FAQEntry:
        """Yangi FAQ qo'shish."""
        faq = FAQEntry(
            keywords=keywords,
            response=response,
            category=category,
        )
        self._faqs.append(faq)
        self._save()
        logger.info(f"➕ FAQ qo'shildi: {category} ({len(keywords)} keyword)")
        return faq

    def remove_faq(self, faq_id: str) -> bool:
        """FAQ o'chirish."""
        for i, faq in enumerate(self._faqs):
            if faq.id == faq_id:
                self._faqs.pop(i)
                self._save()
                return True
        return False

    def get_all(self) -> List[FAQEntry]:
        """Barcha FAQ'lar."""
        return self._faqs

    def get_by_category(self, category: str) -> List[FAQEntry]:
        """Kategoriya bo'yicha."""
        return [f for f in self._faqs if f.category == category]

    # ─────────────────────────────────────────────────────
    # FORMATTING
    # ─────────────────────────────────────────────────────

    def format_list(self) -> str:
        """FAQ ro'yxatini formatlash."""
        if not self._faqs:
            return "_(FAQ bo'sh.)_"

        lines = []
        for i, faq in enumerate(self._faqs, 1):
            keywords_str = ", ".join(faq.keywords[:3])
            lines.append(
                f"*{i}.* [{faq.category}] `{keywords_str}`\n"
                f"   📊 {faq.use_count} marta ishlatilgan"
            )
        return "\n".join(lines)


# Global instance
dm_auto_reply = DMAutoReply()
