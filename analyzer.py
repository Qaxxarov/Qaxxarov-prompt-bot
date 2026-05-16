"""
╔══════════════════════════════════════════════════════╗
║       Instagram Reels Analyzer — Analytics Module    ║
║       Statistika va AI tahlil                        ║
╚══════════════════════════════════════════════════════╝
"""

import json
import logging
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import config
from scraper import ProfileData, ReelData

logger = logging.getLogger("instagram_analyzer.analyzer")


# ════════════════════════════════════════════════════════
# 💡 REEL IDEA MODEL
# ════════════════════════════════════════════════════════

@dataclass
class ReelIdea:
    """Bitta viral reel g'oyasi."""
    number: int = 0
    title: str = ""
    hook: str = ""
    concept: str = ""
    caption: str = ""
    hashtags: List[str] = field(default_factory=list)
    format: str = ""
    viral_reason: str = ""
    estimated_er: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ReelIdea":
        return cls(
            number=d.get("number", 0),
            title=d.get("title", ""),
            hook=d.get("hook", ""),
            concept=d.get("concept", ""),
            caption=d.get("caption", ""),
            hashtags=d.get("hashtags", []),
            format=d.get("format", ""),
            viral_reason=d.get("viral_reason", ""),
            estimated_er=d.get("estimated_er", ""),
        )

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "title": self.title,
            "hook": self.hook,
            "concept": self.concept,
            "caption": self.caption,
            "hashtags": " ".join(self.hashtags),
            "format": self.format,
            "viral_reason": self.viral_reason,
            "estimated_er": self.estimated_er,
        }


# ════════════════════════════════════════════════════════
# 📊 ANALYTICS ENGINE
# ════════════════════════════════════════════════════════

class ReelsAnalyzer:
    """
    Yig'ilgan reels ma'lumotlarini tahlil qilish.
    """

    def __init__(self, profile: ProfileData, reels: List[ReelData]):
        self.profile = profile
        self.reels = reels
        self._stats: Optional[Dict] = None

    # ─────────────────────────────────────────────────────
    # CORE STATS
    # ─────────────────────────────────────────────────────

    def compute_stats(self) -> Dict:
        """Asosiy statistikani hisoblash."""
        if not self.reels:
            return {}

        views = [r.views for r in self.reels]
        likes = [r.likes for r in self.reels]
        comments = [r.comments for r in self.reels]
        ers = [r.engagement_rate for r in self.reels]

        # Top reels
        sorted_by_views = sorted(self.reels, key=lambda r: r.views, reverse=True)
        sorted_by_er = sorted(self.reels, key=lambda r: r.engagement_rate, reverse=True)

        # Hashtag frequency
        all_hashtags = []
        for r in self.reels:
            all_hashtags.extend(r.hashtags)
        top_hashtags = Counter(all_hashtags).most_common(10)

        # Mention frequency
        all_mentions = []
        for r in self.reels:
            all_mentions.extend(r.mentions)
        top_mentions = Counter(all_mentions).most_common(5)

        stats = {
            # Profile
            "profile": {
                "username": self.profile.username,
                "full_name": self.profile.full_name,
                "followers": self.profile.followers,
                "following": self.profile.following,
                "posts_count": self.profile.posts_count,
                "is_verified": self.profile.is_verified,
            },
            # Overview
            "overview": {
                "total_reels_analyzed": len(self.reels),
                "total_views": sum(views),
                "total_likes": sum(likes),
                "total_comments": sum(comments),
            },
            # Views stats
            "views": {
                "average": int(statistics.mean(views)) if views else 0,
                "median": int(statistics.median(views)) if views else 0,
                "max": max(views) if views else 0,
                "min": min(views) if views else 0,
                "std_dev": int(statistics.stdev(views)) if len(views) > 1 else 0,
            },
            # Likes stats
            "likes": {
                "average": int(statistics.mean(likes)) if likes else 0,
                "median": int(statistics.median(likes)) if likes else 0,
                "max": max(likes) if likes else 0,
            },
            # Engagement
            "engagement": {
                "average_er": round(statistics.mean(ers), 2) if ers else 0,
                "median_er": round(statistics.median(ers), 2) if ers else 0,
                "max_er": round(max(ers), 2) if ers else 0,
                "er_benchmark": self._er_benchmark(statistics.mean(ers) if ers else 0),
            },
            # Top performers
            "top_reels": {
                "by_views": [r.to_dict() for r in sorted_by_views[:3]],
                "by_engagement": [r.to_dict() for r in sorted_by_er[:3]],
                "worst_by_views": [r.to_dict() for r in sorted_by_views[-3:]],
            },
            # Content analysis
            "content": {
                "top_hashtags": [{"tag": f"#{tag}", "count": cnt} for tag, cnt in top_hashtags],
                "top_mentions": [{"mention": f"@{m}", "count": cnt} for m, cnt in top_mentions],
                "avg_hashtags_per_reel": round(
                    sum(len(r.hashtags) for r in self.reels) / len(self.reels), 1
                ),
                "reels_with_caption": sum(1 for r in self.reels if r.caption),
            },
            # Performance tiers
            "performance_tiers": self._classify_reels(),
        }

        self._stats = stats
        return stats

    def _er_benchmark(self, er: float) -> str:
        """Engagement rate baholash."""
        if er >= 6:
            return "🔥 Ajoyib (6%+)"
        elif er >= 3:
            return "✅ Yaxshi (3-6%)"
        elif er >= 1:
            return "⚠️ O'rtacha (1-3%)"
        else:
            return "❌ Past (<1%)"

    def _classify_reels(self) -> Dict:
        """Reellarni performance darajasiga ko'ra tasniflash."""
        if not self.reels:
            return {}

        avg_views = statistics.mean(r.views for r in self.reels)

        viral = []      # 3x+ o'rtachadan yuqori
        good = []       # 1.5x-3x
        average = []    # 0.5x-1.5x
        underperform = []  # 0.5x dan past

        for r in self.reels:
            ratio = r.views / avg_views if avg_views > 0 else 0
            entry = {"url": r.url, "views": r.views, "er": r.engagement_rate}
            if ratio >= 3:
                viral.append(entry)
            elif ratio >= 1.5:
                good.append(entry)
            elif ratio >= 0.5:
                average.append(entry)
            else:
                underperform.append(entry)

        return {
            "viral": {"count": len(viral), "reels": viral},
            "good": {"count": len(good), "reels": good},
            "average": {"count": len(average), "reels": average},
            "underperforming": {"count": len(underperform), "reels": underperform},
        }

    # ─────────────────────────────────────────────────────
    # RECOMMENDATIONS
    # ─────────────────────────────────────────────────────

    def generate_recommendations(self) -> List[str]:
        """Ma'lumotlarga asoslangan tavsiyalar."""
        if not self._stats:
            self.compute_stats()

        recs = []
        stats = self._stats

        avg_er = stats["engagement"]["average_er"]
        avg_views = stats["views"]["average"]
        top_hashtags = stats["content"]["top_hashtags"]
        viral_count = stats["performance_tiers"].get("viral", {}).get("count", 0)
        total = stats["overview"]["total_reels_analyzed"]

        # Engagement rate tavsiyalari
        if avg_er < 1:
            recs.append(
                "📉 Engagement rate juda past (<1%). Call-to-action qo'shing: "
                "'Like bosing', 'Fikringizni yozing' kabi so'rovlar ishlating."
            )
        elif avg_er < 3:
            recs.append(
                "📊 Engagement rate o'rtacha (1-3%). Savol bilan tugaydigan "
                "caption'lar yozing — bu comment'larni oshiradi."
            )
        else:
            recs.append(
                f"🔥 Engagement rate yaxshi ({avg_er}%). Shu formatni davom ettiring!"
            )

        # Viral content
        if viral_count > 0:
            recs.append(
                f"🚀 {viral_count} ta viral reel topildi. Ularning umumiy "
                "xususiyatlarini (mavzu, format, uzunlik) tahlil qiling va takrorlang."
            )

        # Hashtag tavsiyasi
        if top_hashtags:
            best_tags = ", ".join(h["tag"] for h in top_hashtags[:5])
            recs.append(
                f"#️⃣ Eng ko'p ishlatiladigan hashtaglar: {best_tags}. "
                "Har bir reelda 5-10 ta maqsadli hashtag ishlating."
            )
        else:
            recs.append(
                "#️⃣ Hashtaglar ishlatilmayapti. Niche hashtaglar qo'shish "
                "organik reach'ni 30-50% oshirishi mumkin."
            )

        # Posting frequency
        recs.append(
            "📅 Haftada kamida 3-5 ta reel post qiling. "
            "Izchillik Instagram algoritmiga ijobiy ta'sir qiladi."
        )

        # Views vs followers
        followers = stats["profile"]["followers"]
        if followers > 0 and avg_views > 0:
            reach_rate = avg_views / followers * 100
            if reach_rate < 10:
                recs.append(
                    f"👁 Reach rate past ({reach_rate:.1f}%). "
                    "Birinchi 30 daqiqada aktiv bo'ling — "
                    "tezkor engagement algoritmga signal beradi."
                )
            elif reach_rate > 50:
                recs.append(
                    f"🎯 Reach rate ajoyib ({reach_rate:.1f}%)! "
                    "Followers'dan tashqari auditoriyaga ham yetib boryapsiz."
                )

        # Underperforming content
        underperform_count = stats["performance_tiers"].get("underperforming", {}).get("count", 0)
        if underperform_count > total * 0.4:
            recs.append(
                f"⚠️ {underperform_count} ta reel o'rtachadan past. "
                "Hook (birinchi 3 soniya) va thumbnail'larni yaxshilang."
            )

        return recs

    # ─────────────────────────────────────────────────────
    # VIRAL IDEA GENERATOR
    # ─────────────────────────────────────────────────────

    def generate_reel_ideas(self, count: int = 20) -> List["ReelIdea"]:
        """
        Tahlil qilingan ma'lumotlar asosida viral reel g'oyalar yaratish.
        AI mavjud bo'lsa OpenAI ishlatadi, aks holda rule-based generator.
        """
        if not self._stats:
            self.compute_stats()

        if config.AI_ENABLED:
            return self._ai_reel_ideas(count)
        return self._rule_based_reel_ideas(count)

    def _build_ideas_context(self) -> str:
        """AI uchun profil kontekstini tayyorlash."""
        s = self._stats

        # Viral reellarning caption'larini yig'ish
        viral_reels = s["performance_tiers"].get("viral", {}).get("reels", [])
        good_reels  = s["performance_tiers"].get("good",  {}).get("reels", [])
        top_captions = []
        for r in self.reels:
            ratio = r.views / max(s["views"]["average"], 1)
            if ratio >= 1.5 and r.caption:
                top_captions.append(
                    f'  • "{r.caption[:120]}" — {r.views:,} views, ER {r.engagement_rate}%'
                )
        captions_block = "\n".join(top_captions[:6]) or "  (caption ma'lumoti yo'q)"

        top_tags = ", ".join(h["tag"] for h in s["content"]["top_hashtags"][:8])

        return f"""
PROFIL: @{s['profile']['username']} ({s['profile']['followers']:,} followers)
NICHE: {self.profile.bio[:100] if self.profile.bio else "aniqlanmagan"}

STATISTIKA:
- Tahlil qilingan reels: {s['overview']['total_reels_analyzed']}
- O'rtacha views: {s['views']['average']:,}
- Eng yuqori views: {s['views']['max']:,}
- O'rtacha engagement rate: {s['engagement']['average_er']}%
- Viral reels soni: {len(viral_reels)}
- Yaxshi reels soni: {len(good_reels)}

ENG YAXSHI ISHLAGAN CAPTION'LAR:
{captions_block}

TOP HASHTAGLAR: {top_tags}
""".strip()

    def _ai_reel_ideas(self, count: int) -> List["ReelIdea"]:
        """OpenAI orqali {count} ta viral reel g'oyasi."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)

            context = self._build_ideas_context()

            prompt = f"""
Quyidagi Instagram profil tahlili asosida {count} ta VIRAL reel g'oyasi yarat.

{context}

HAR BIR G'OYA UCHUN QUYIDAGI FORMATDA JAV0B BER (JSON array):
[
  {{
    "number": 1,
    "title": "Qisqa sarlavha (max 8 so'z)",
    "hook": "Birinchi 3 soniyada aytiladi — diqqatni tortuvchi gap",
    "concept": "Reel nimadan iborat — 2-3 jumlada tushuntir",
    "caption": "Post caption matni (CTA bilan)",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "format": "Tutorial | Before/After | POV | Storytelling | Trend | Educational | Behind-scenes",
    "viral_reason": "Nima uchun viral bo'lishi mumkin — 1 jumla",
    "estimated_er": "Taxminiy engagement rate (masalan: 4-7%)"
  }}
]

QOIDALAR:
- Faqat JSON qaytargin, boshqa matn yo'q
- Profil niche'iga mos g'oyalar
- Har xil formatlar aralashtirilsin (tutorial, trend, storytelling va h.k.)
- Hook juda kuchli bo'lsin — "Bilasizmi...", "Hech kim aytmagan...", "X soniyada..."
- O'zbek tilida yoz
""".strip()

            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Siz Instagram content strategist va viral marketing ekspertisiz. "
                            "Faqat JSON formatda javob bering."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3500,
                temperature=0.85,
            )

            raw = response.choices[0].message.content.strip()
            # JSON blokni tozalash (```json ... ``` bo'lishi mumkin)
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            import json
            ideas_data = json.loads(raw)
            ideas = [ReelIdea.from_dict(d) for d in ideas_data[:count]]
            logger.info(f"✅ AI {len(ideas)} ta reel g'oyasi yaratdi")
            return ideas

        except Exception as e:
            logger.error(f"AI g'oya generatsiya xatosi: {e} — rule-based'ga o'tilmoqda")
            return self._rule_based_reel_ideas(count)

    def _rule_based_reel_ideas(self, count: int) -> List["ReelIdea"]:
        """
        AI yo'q bo'lganda ishlaydigan rule-based g'oya generatori.
        Profil statistikasidan pattern'lar chiqarib, shablonlarni to'ldiradi.
        """
        s = self._stats
        username = s["profile"]["username"]
        top_tags = [h["tag"] for h in s["content"]["top_hashtags"][:5]]
        avg_er   = s["engagement"]["average_er"]
        niche    = self.profile.bio[:60] if self.profile.bio else "biznes/hayot"

        # Viral reellardan mavzu pattern'larini chiqarish
        viral_topics: List[str] = []
        for r in self.reels:
            ratio = r.views / max(s["views"]["average"], 1)
            if ratio >= 1.5 and r.caption:
                words = r.caption.split()[:5]
                viral_topics.append(" ".join(words))

        # 20 ta shablon — 5 ta format kategoriyasi x 4 ta g'oya
        templates = [
            # ── EDUCATIONAL (4 ta) ──
            ReelIdea(
                number=1, format="Educational",
                title="5 ta sir hech kim aytmagan",
                hook="Hech kim sizga buni aytmagan — lekin men aytaman...",
                concept=f"@{username} profilida eng ko'p savol berilgan mavzu bo'yicha 5 ta kam ma'lum fakt. Har bir fakt ekranda yozuv bilan ko'rsatiladi.",
                caption=f"Buni bilmasangiz, katta xato qilayotgansiz 👇\n\nSavollaringiz bo'lsa — kommentga yozing!\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#bilim", "#sirlar"],
                viral_reason="'Hech kim aytmagan' hook qiziqish uyg'otadi, share'lar ko'payadi",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 4:.1f}%",
            ),
            ReelIdea(
                number=2, format="Educational",
                title="Yangi boshlovchilar uchun 3 qadam",
                hook="Agar siz ham boshida adashgan bo'lsangiz — bu reel siz uchun",
                concept="Niche'ga yangi kirganlar uchun 3 bosqichli yo'l xaritasi. Har bir qadam animatsiya yoki text overlay bilan.",
                caption=f"Boshida men ham shunday adashganman 😅\n\nQaysi qadamda qiynalyapsiz? 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#boshlash", "#qadamlar"],
                viral_reason="Yangi boshlovchilar katta auditoriya, save va share ko'p bo'ladi",
                estimated_er=f"{avg_er + 1:.1f}-{avg_er + 3:.1f}%",
            ),
            ReelIdea(
                number=3, format="Educational",
                title="Ko'pchilik bilmagan 1 ta usul",
                hook="Bu usulni bilganlar natijani 2x tezroq oladi...",
                concept="Niche'dagi eng samarali lekin kam ma'lum bo'lgan bitta usul yoki lifehack. Amaliy ko'rsatma bilan.",
                caption=f"Bu usulni o'rganib {s['views']['max']:,} views oldim 🚀\n\nSiz ham sinab ko'ring!\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#usul", "#lifehack"],
                viral_reason="Amaliy va qisqa — save rate yuqori bo'ladi",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 5:.1f}%",
            ),
            ReelIdea(
                number=4, format="Educational",
                title="Xato qilmang — bu farqni biling",
                hook="90% odam bu ikki narsani aralashtirib yuboradi...",
                concept="Niche'dagi eng keng tarqalgan 2 ta tushunchani solishtirish. Chap/o'ng split screen yoki before/after.",
                caption=f"Siz qaysi tomondasiz? Kommentga yozing 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#farq", "#xato"],
                viral_reason="Debate uyg'otadi — comment va share ko'payadi",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 6:.1f}%",
            ),
            # ── STORYTELLING (4 ta) ──
            ReelIdea(
                number=5, format="Storytelling",
                title="Mening eng katta xatom",
                hook="Bu xatoni qilmasangiz, men kabi yillar yo'qotmaysiz...",
                concept="Shaxsiy tajribadan eng katta xato va undan olingan saboq. Hissiy, samimiy ohangda.",
                caption=f"Bu xatoni qilganman — endi siz qilmang 🙏\n\nO'zingizning xatolaringizni kommentga yozing\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#tajriba", "#sabоq"],
                viral_reason="Samimiylik trust yaratadi, comment va save ko'payadi",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 4:.1f}%",
            ),
            ReelIdea(
                number=6, format="Storytelling",
                title="0 dan bugungi kunga — mening yo'lim",
                hook="Bir yil oldin hech narsam yo'q edi. Bugun esa...",
                concept="Transformation story — boshlanish nuqtasi va hozirgi holat. Raqamlar va dalillar bilan.",
                caption=f"Yo'l oson bo'lmadi, lekin arziydigan edi ✨\n\nSizning yo'lingiz qanday? 👇\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#transformation", "#yol"],
                viral_reason="Motivatsion kontent keng auditoriyaga yetadi, share ko'p",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 5:.1f}%",
            ),
            ReelIdea(
                number=7, format="Storytelling",
                title="Hech kim ishonmagan paytda",
                hook="Hamma 'bo'lmaydi' dedi. Men esa...",
                concept="Qiyinchilikka qaramay maqsadga erishish haqida qisqa hikoya. Emotsional arc bilan.",
                caption=f"Ishonmaydiganlar uchun emas, ishonganlar uchun 💪\n\nSizga kim ishonmagan? 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#motivatsiya", "#maqsad"],
                viral_reason="Underdog story universally resonates — keng auditoriya",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 4:.1f}%",
            ),
            ReelIdea(
                number=8, format="Storytelling",
                title="Bir kunlik hayotim — real ko'rsataman",
                hook="Mening bir kunim qanday o'tadi? Hech narsa yashirmayman...",
                concept="Day-in-the-life format. Ertalabdan kechgacha real ko'rsatish. Montaj tez, musiqali.",
                caption=f"Real hayot — filter yo'q 📱\n\nSizning kuningiz qanday o'tadi? 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#hayot", "#dayinthelife"],
                viral_reason="Authenticity trending — followers bilan yaqinlik oshadi",
                estimated_er=f"{avg_er + 1:.1f}-{avg_er + 3:.1f}%",
            ),
            # ── TUTORIAL / HOW-TO (4 ta) ──
            ReelIdea(
                number=9, format="Tutorial",
                title="30 soniyada o'rganing",
                hook="30 soniyangiz bormi? Unda bu usulni o'rganing...",
                concept="Bitta konkret ko'nikmani 30 soniyada ko'rsatish. Tez montaj, text overlay, musiqali.",
                caption=f"30 soniya — lekin butun hayotingizni o'zgartirishi mumkin 🔥\n\nSave qiling, kerak bo'ladi!\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#tutorial", "#30soniya"],
                viral_reason="Qisqa + amaliy = save rate maksimal",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 6:.1f}%",
            ),
            ReelIdea(
                number=10, format="Tutorial",
                title="Step-by-step: noldan natijagacha",
                hook="Qadamma-qadam ko'rsataman — hech narsa yashirmayman",
                concept="Bitta natijaga erishish uchun to'liq jarayon. Har bir qadam numbered overlay bilan.",
                caption=f"Buni qilsangiz — natija kafolatlangan ✅\n\nQaysi qadamda savolingiz bor? 👇\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#stepbystep", "#qoʻllanma"],
                viral_reason="To'liq qo'llanma = save va share maksimal",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 5:.1f}%",
            ),
            ReelIdea(
                number=11, format="Tutorial",
                title="Men ishlatadiganlar — top 3 vosita",
                hook="Har kuni ishlatadigan 3 ta vositam — bepul va samarali",
                concept="Niche'da eng foydali 3 ta tool/usul/resurs. Har birini qisqa demo bilan ko'rsatish.",
                caption=f"Bularni bilmasangiz, vaqtingizni behuda sarflayapsiz ⏰\n\nQaysi birini bilardingiz? 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#vositalar", "#tools"],
                viral_reason="Resource sharing = save rate eng yuqori format",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 6:.1f}%",
            ),
            ReelIdea(
                number=12, format="Tutorial",
                title="Xatoni tuzatish — live ko'rsataman",
                hook="Bu xatoni qilayotgansiz — hoziroq to'xtating",
                concept="Keng tarqalgan xatoni real vaqtda ko'rsatib, to'g'ri usulni o'rgatish. Before/after format.",
                caption=f"Bu xatoni qilganlar — like bosing 👍\n\nTo'g'ri usulni bilganlar — kommentga yozing!\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#xato", "#togri"],
                viral_reason="'Xato' so'zi hook sifatida kuchli — comment uyg'otadi",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 5:.1f}%",
            ),
            # ── TREND / POV (4 ta) ──
            ReelIdea(
                number=13, format="POV",
                title="POV: Siz ham shunday his qilasizmi?",
                hook="POV: Hammasi yaxshi ketayotganda...",
                concept="Niche'ga oid kulgili yoki tanish vaziyat. Tomoshabin o'zini ko'rishi kerak.",
                caption=f"Faqat men shundaymi? 😅\n\nO'zingizni ko'rdingizmi? Kommentga yozing!\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#pov", "#tanish"],
                viral_reason="Relatable kontent = share va comment portlashi",
                estimated_er=f"{avg_er + 4:.1f}-{avg_er + 7:.1f}%",
            ),
            ReelIdea(
                number=14, format="POV",
                title="Kutilmagan natija — hamma hayron",
                hook="Hech kim bu natijani kutmagan edi...",
                concept="Surprise reveal format. Birinchi yarmi muammo, ikkinchi yarmi kutilmagan yechim.",
                caption=f"Oxirigacha ko'rdingizmi? 👀\n\nSizda ham shunday bo'lganmi? 👇\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#surprise", "#natija"],
                viral_reason="Curiosity gap — oxirigacha ko'rish majburiyati",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 6:.1f}%",
            ),
            ReelIdea(
                number=15, format="Trend",
                title="Trending audio + niche kontent",
                hook="[Trending audio bilan boshlanadi]",
                concept="Hozirgi trending audio yoki formatni niche'ga moslashtirish. Tez va qisqa — 15-20 soniya.",
                caption=f"Trend + niche = viral formula 🎵\n\nSizga yoqdimi? Like bosing!\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#trend", "#viral"],
                viral_reason="Trending audio algoritmda ustunlik beradi",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 7:.1f}%",
            ),
            ReelIdea(
                number=16, format="Trend",
                title="'Get ready with me' — niche versiyasi",
                hook="Keling, birga tayyorlanamiz...",
                concept="GRWM formatini niche'ga moslashtirish. Jarayon ko'rsatish + voiceover.",
                caption=f"Mening tayyorlanish jarayonim 🎬\n\nSizniki qanday? Kommentga yozing!\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#grwm", "#jarayon"],
                viral_reason="GRWM format hozir eng trending — katta reach",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 5:.1f}%",
            ),
            # ── BEHIND THE SCENES / ENGAGEMENT (4 ta) ──
            ReelIdea(
                number=17, format="Behind-scenes",
                title="Sahna ortida — haqiqatni ko'rsataman",
                hook="Hech kim ko'rmaydigan tomonimni ko'rsataman...",
                concept="Ish jarayonining sahna ortini ko'rsatish. Raw, unfiltered footage. Voiceover bilan.",
                caption=f"Haqiqat har doim chiroyli emas 😅\n\nSiz ham shunday his qilasizmi? 👇\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#behindthescenes", "#haqiqat"],
                viral_reason="Authenticity = trust = loyal followers",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 4:.1f}%",
            ),
            ReelIdea(
                number=18, format="Behind-scenes",
                title="Savollarga javob — Q&A reel",
                hook="Eng ko'p berilgan savolga javob beraman...",
                concept="Followers savollarini yig'ib, reelda javob berish. Har bir savol text overlay bilan.",
                caption=f"Savollaringizni kommentga yozing — keyingi reelda javob beraman! 📩\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#qa", "#savol"],
                viral_reason="Community engagement — followers o'zini muhim his qiladi",
                estimated_er=f"{avg_er + 3:.1f}-{avg_er + 6:.1f}%",
            ),
            ReelIdea(
                number=19, format="Educational",
                title="Raqamlar bilan isbotlayman",
                hook=f"Men {s['views']['max']:,} views olgan reelning sirini aytaman...",
                concept="Eng yaxshi ishlagan reel'ning nima uchun viral bo'lganini tahlil qilish. Data-driven storytelling.",
                caption=f"Raqamlar yolg'on gapirmaydi 📊\n\nSiz ham sinab ko'ring va natijani yozing!\n\n{' '.join(top_tags[:4])}",
                hashtags=top_tags + ["#data", "#tahlil"],
                viral_reason="Transparency + data = credibility va share",
                estimated_er=f"{avg_er + 2:.1f}-{avg_er + 5:.1f}%",
            ),
            ReelIdea(
                number=20, format="Engagement",
                title="Tanlov: A yoki B?",
                hook="Siz qaysi tomondasiz? A yoki B?",
                concept="Niche'ga oid ikki qarashni solishtirish. Tomoshabin kommentda ovoz beradi. Split screen.",
                caption=f"A yoki B? Kommentga yozing 👇\n\nDo'stlaringizni tag qiling — ular nima deydi?\n\n{' '.join(top_tags[:3])}",
                hashtags=top_tags + ["#tanlov", "#debate"],
                viral_reason="Debate format = comment portlashi = algoritm boost",
                estimated_er=f"{avg_er + 4:.1f}-{avg_er + 8:.1f}%",
            ),
        ]

        return templates[:count]

    # ─────────────────────────────────────────────────────
    # AI ANALYSIS
    # ─────────────────────────────────────────────────────

    def ai_analysis(self) -> str:
        """OpenAI orqali chuqur tahlil (agar API key bo'lsa)."""
        if not config.AI_ENABLED:
            return "ℹ️ AI tahlil uchun OPENAI_API_KEY kerak (.env faylida)"

        try:
            from openai import OpenAI

            if not self._stats:
                self.compute_stats()

            client = OpenAI(api_key=config.OPENAI_API_KEY)

            # Qisqa summary tayyorlash
            s = self._stats
            summary = f"""
Instagram profil: @{s['profile']['username']}
Followers: {s['profile']['followers']:,}
Tahlil qilingan reels: {s['overview']['total_reels_analyzed']}
O'rtacha views: {s['views']['average']:,}
O'rtacha engagement rate: {s['engagement']['average_er']}%
Viral reels: {s['performance_tiers'].get('viral', {}).get('count', 0)}
Top hashtaglar: {', '.join(h['tag'] for h in s['content']['top_hashtags'][:5])}
Top 3 reel views: {[r['views'] for r in s['top_reels']['by_views']]}
"""

            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Siz Instagram marketing ekspertisiz. "
                            "Berilgan ma'lumotlar asosida qisqa, amaliy tavsiyalar bering. "
                            "O'zbek tilida javob bering."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Quyidagi Instagram profil statistikasini tahlil qiling:\n{summary}",
                    },
                ],
                max_tokens=600,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI tahlil xatosi: {e}")
            return f"❌ AI tahlil xatosi: {e}"
