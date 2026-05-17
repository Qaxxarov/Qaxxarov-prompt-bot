"""
Agro AI — Trend Radar Engine
Real-time trend detection, prediction, and adaptation.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.ai.base import BaseAIEngine
from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.ai.trends")

TRENDS_DIR = DATA_DIR / "trends"
TRENDS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TrendSignal:
    """Bitta trend signali."""
    id: str = ""
    category: str = ""       # hook_style, format, topic, pacing, storytelling
    name: str = ""
    description: str = ""
    momentum: float = 0.0    # 0-10 (qanchalik tez o'sib bormoqda)
    confidence: float = 0.0  # 0-10
    source: str = ""         # scraped, ai_detected, competitor
    examples: List[str] = field(default_factory=list)
    adaptation: str = ""     # Qanday moslashtirish mumkin
    detected_at: float = 0.0
    expires_at: float = 0.0  # Trend qachon eskiradi (taxminan)

    def __post_init__(self):
        if not self.id:
            self.id = f"trend_{int(time.time() * 1000)}"
        if not self.detected_at:
            self.detected_at = time.time()
        if not self.expires_at:
            self.expires_at = time.time() + 7 * 86400  # 7 kun default


class TrendRadarEngine(BaseAIEngine):
    """
    Trend Radar — trendlarni aniqlash, bashorat qilish, moslashtirish.
    """

    engine_name = "trend_radar"
    default_max_tokens = 1200
    default_temperature = 0.8

    TREND_CATEGORIES = [
        "hook_style",      # Hook uslublari trendi
        "format",          # Reel format trendi (POV, GRWM, etc.)
        "topic",           # Mavzu trendi
        "pacing",          # Tezlik/ritm trendi
        "storytelling",    # Hikoya tuzilmasi trendi
        "visual",          # Vizual uslub trendi
        "audio",           # Audio/musiqa trendi
    ]

    def __init__(self, account):
        super().__init__(account)
        self._signals_path = TRENDS_DIR / f"{account.id}_signals.json"

    def get_system_prompt(self) -> str:
        return (
            "Siz Instagram Reels trend intelligence ekspertisiz.\n"
            f"Brand: {self.account.instagram}\n"
            f"Niche: {self.account.niche}\n\n"
            "═══ TREND QOIDALARI ═══\n"
            "- Mavsumga qarab trend tavsiya ber:\n"
            "  * Yoz: sug'orish, issiqdan himoya, zararkunandalar\n"
            "  * Kuz: hosil yig'ish, saqlash, qayta ishlash\n"
            "  * Qish: ko'chat tayyorlash, tuproq tayyorlash, rejalashtirish\n"
            "  * Bahor: ekish, urug' tanlash, issiqxona\n"
            "- Uy sharoitida oddiy maslahatlar DOIM trend bo'ladi\n"
            "- Before/After format viral potensiali yuqori\n"
            "- Raqamli natijalar (\"3 kun\", \"50 kg\", \"1 sotix\") trend\n"
            "- Xatolar va miflar mavzusi doim qiziqtiradi\n\n"
            "Vazifangiz:\n"
            "- Hozirgi trendlarni aniqlash\n"
            "- Trend momentum'ini baholash\n"
            "- Kelgusi trendlarni bashorat qilish\n"
            "- Trendlarni niche'ga moslashtirish strategiyasi\n"
            "- Qishloq xo'jaligi kontekstida amaliy tavsiyalar\n"
            "O'zbek tilida, aniq va professional."
        )

    # ─────────────────────────────────────────────────────
    # TREND DETECTION
    # ─────────────────────────────────────────────────────

    async def detect_trends(self, stats: Optional[Dict] = None) -> str:
        """Joriy trendlarni aniqlash."""
        ctx = self.build_context(stats)
        task = (
            "Hozirgi Instagram Reels trendlarini aniqlash:\n\n"
            "Har bir trend uchun:\n"
            "1. NOMI va TAVSIFI\n"
            "2. KATEGORIYA (hook/format/topic/pacing/storytelling/visual/audio)\n"
            "3. MOMENTUM (1-10, qanchalik tez o'sib bormoqda)\n"
            "4. MISOL (aniq namuna)\n"
            "5. AGRO MOSLASHTIRISH (qishloq xo'jaligi uchun qanday ishlatish)\n\n"
            "Kamida 7 ta trend. Eng kuchlilaridan boshlang.\n"
            "Faqat HOZIR ishlayotgan trendlar — eskirganlarni kiritmang."
        )
        return await self.generate(task, context=ctx)

    async def predict_trends(self, stats: Optional[Dict] = None) -> str:
        """Kelgusi trendlarni bashorat qilish."""
        ctx = self.build_context(stats)
        task = (
            "Keyingi 30 kunda Instagram Reels'da paydo bo'ladigan trendlarni bashorat qil:\n\n"
            "Har bir bashorat uchun:\n"
            "1. TREND NOMI\n"
            "2. NIMA UCHUN paydo bo'ladi (sabab)\n"
            "3. QACHON boshlanadi (taxminan)\n"
            "4. QANDAY tayyorlanish kerak\n"
            "5. BIRINCHI BO'LISH strategiyasi\n\n"
            "5 ta bashorat. Qishloq xo'jaligi niche'iga mos.\n"
            "Faqat real signallarga asoslangan bashoratlar."
        )
        return await self.generate(task, context=ctx)

    async def get_trend_adaptation(self, trend_name: str, stats: Optional[Dict] = None) -> str:
        """Berilgan trendni niche'ga moslashtirish strategiyasi."""
        ctx = self.build_context(stats)
        task = (
            f"'{trend_name}' trendini qishloq xo'jaligi kontentiga moslashtir:\n\n"
            "1. ORIGINAL TREND qanday ishlaydi\n"
            "2. AGRO VERSIYA qanday bo'ladi\n"
            "3. HOOK (birinchi 3 soniya)\n"
            "4. KONTENT TUZILMASI\n"
            "5. VIZUAL USLUB\n"
            "6. CAPTION va CTA\n"
            "7. ENG YAXSHI VAQT\n\n"
            "Juda aniq va amaliy. Hoziroq qo'llash mumkin bo'lsin."
        )
        return await self.generate(task, context=ctx)

    async def daily_trend_report(self, stats: Optional[Dict] = None) -> str:
        """Kunlik trend hisoboti."""
        ctx = self.build_context(stats)
        task = (
            "Bugungi KUNLIK TREND HISOBOTI:\n\n"
            "1. 🔥 BUGUNGI TOP 3 TREND (eng kuchli)\n"
            "2. 📈 O'SIB BORMOQDA (momentum yuqori)\n"
            "3. 📉 PASAYMOQDA (endi ishlamaydi)\n"
            "4. 🆕 YANGI PAYDO BO'LDI\n"
            "5. 💡 BUGUN SINAB KO'RING (1 ta aniq tavsiya)\n\n"
            "Qisqa va aniq. Emoji bilan. Agro niche uchun."
        )
        return await self.generate(task, context=ctx, max_tokens=600)

    async def analyze_hook_trends(self, stats: Optional[Dict] = None) -> str:
        """Hook uslublari trendini tahlil qilish."""
        ctx = self.build_context(stats)
        task = (
            "Hozirgi Instagram'da eng ko'p ishlatilayotgan HOOK USLUBLARI:\n\n"
            "Har biri uchun:\n"
            "- Uslub nomi\n"
            "- Namuna (aniq matn)\n"
            "- Nima uchun ishlaydi (psixologiya)\n"
            "- Agro versiyasi\n"
            "- Momentum (1-10)\n\n"
            "10 ta hook trend. Eng kuchlilaridan boshlang."
        )
        return await self.generate(task, context=ctx)

    # ─────────────────────────────────────────────────────
    # SIGNAL STORAGE
    # ─────────────────────────────────────────────────────

    def save_signal(self, signal: TrendSignal) -> None:
        """Trend signalini saqlash."""
        signals = self._load_signals()
        signals.append(signal)
        # Oxirgi 100 ta saqlash
        signals = signals[-100:]
        self._save_signals(signals)

    def get_active_signals(self) -> List[TrendSignal]:
        """Faol (eskirmaganlar) signallarni olish."""
        signals = self._load_signals()
        now = time.time()
        return [s for s in signals if s.expires_at > now]

    def _load_signals(self) -> List[TrendSignal]:
        if not self._signals_path.exists():
            return []
        try:
            with open(self._signals_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [TrendSignal(**d) for d in data]
        except Exception:
            return []

    def _save_signals(self, signals: List[TrendSignal]) -> None:
        try:
            with open(self._signals_path, "w", encoding="utf-8") as f:
                json.dump([asdict(s) for s in signals], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Trend signal saqlashda xato: {e}")

    def _fallback(self, task: str) -> str:
        return (
            "📡 *TREND RADAR*\n\n"
            "🔥 *Hozirgi top trendlar:*\n"
            "1. POV format — fermer hayoti\n"
            "2. Before/After — hosil natijasi\n"
            "3. Myth-busting — noto'g'ri tushunchalar\n"
            "4. Micro-tutorial — 30 soniyada o'rganish\n"
            "5. Talking head + text overlay\n\n"
            "_(AI yoqilsa — real-time trend tahlili)_"
        )
