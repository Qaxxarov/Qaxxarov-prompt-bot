"""
Agro AI — Multi-Account Tizimi
Bir nechta Instagram brand/akkauntni boshqarish.
To'liq CRUD: qo'shish, tahrirlash, o'chirish, almashtirish.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import ACCOUNTS_FILE, CHROME_PROFILE_DIR, CHROME_USER_DATA_DIR, TARGET_PROFILE

logger = logging.getLogger("agro_ai.accounts")


@dataclass
class Account:
    """Bitta Instagram brand/akkaunt."""
    id: str
    instagram: str
    niche: str = ""
    chrome_profile: str = "Profile 3"
    ai_personality: str = "Professional Instagram content strategist"
    target_audience: str = ""
    language: str = "uz"
    languages: List[str] = field(default_factory=lambda: ["uz"])
    active: bool = True
    hashtags: List[str] = field(default_factory=list)
    posting_times: List[str] = field(default_factory=lambda: ["19:00", "20:00"])
    content_mix: Dict[str, int] = field(default_factory=lambda: {
        "educational": 30,
        "entertainment": 30,
        "sales": 20,
        "trend": 20,
    })
    # v3.0 yangi fieldlar
    competitors: List[str] = field(default_factory=list)
    posting_frequency: int = 1  # kuniga nechta post
    ai_tone: str = "professional"  # professional, casual, fun

    @property
    def username(self) -> str:
        return self.instagram.lstrip("@")

    def get_system_prompt(self) -> str:
        """AI uchun account-specific batafsil system prompt."""
        return (
            f"Siz {self.instagram} Instagram akkauntining professional AI content strategist "
            f"va ssenariy yozuvchisisiz.\n\n"
            f"═══ BREND HAQIDA ═══\n"
            f"Akkaunt: {self.instagram}\n"
            f"Niche: {self.niche}\n"
            f"Joylashuv: Samarqand, O'zbekiston\n"
            f"Hozirgi bosqich: Auditoriya yig'ish, keyin urug'lik va AI xizmatlar sotish\n"
            f"Yo'nalish: Qishloq xo'jaligi + AI texnologiyalar\n\n"
            f"═══ BRENDNING ASOSIY PERSONAJI ═══\n"
            f"Face brand — maymun-fermer personaj (AI generated):\n"
            f"- Doim fermer kiyimida: somon shlyapa, kletchatka ko'ylak, jeans kombinezon\n"
            f"- Personaj har bir videoda ishtirok etadi\n"
            f"- U sodda, do'stona, hazilkash — xalqqa yaqin fermer obrazi\n"
            f"- Personajning ismi va harakatlari ssenariyda aniq ko'rsatilishi kerak\n"
            f"- Har bir kadrda personajning pozasi, yuz ifodasi, harakati aniq yozilsin\n\n"
            f"═══ AUDITORIYA ═══\n"
            f"Asosiy: {self.target_audience}\n"
            f"- Uy hovlisida ekadiganlar (eng katta segment)\n"
            f"- Bog'dorlar va dala fermerlar\n"
            f"- Issiqxona egalari\n"
            f"- Dehqonchilik bilan shug'ullanadigan oddiy aholi\n"
            f"- Shahar atrofida yashab, hovlisida pomidor, bodring ekadiganlar\n"
            f"Muhim: FAQAT fermerlar emas — oddiy uy xo'jaligi ham!\n\n"
            f"═══ KONTENT STRATEGIYA ═══\n"
            f"Muvaffaqiyatli mavzular (isbot qilingan):\n"
            f"- Uy sharoitida pomidor parvarishi — 1.3 MLN ko'rish\n"
            f"- Bodring parvarishi — 132K ko'rish\n"
            f"- Sabab: oddiy, sodda, uy sharoitida — har kim qila oladigan maslahatlar\n\n"
            f"Kontent qoidalari:\n"
            f"1. Faqat pomidor/bodring emas — har xil mavzular: qalampir, baqlajon, sabzi, "
            f"piyoz, gul, mevalar, ko'chatlar, tuproq tayyorlash, kasalliklar, o'g'itlar, asboblar\n"
            f"2. Har doim AMALIY foyda — ko'rgan odam darhol qo'llay olsin\n"
            f"3. Oddiy til — ilmiy terminlar ishlatma, fermer tilida gapir\n"
            f"4. Uy sharoitiga mos — balkon, hovli, kichik yer uchun ham\n"
            f"5. Mavsumga mos — hozirgi oyda nima ekiladi, nima parvarishlanadi\n"
            f"6. Hayratlanarli faktlar bilan boshlash\n\n"
            f"Kontent aralashmasi:\n"
            f"- 40% ta'limiy (parvarish, maslahat, sir)\n"
            f"- 25% ko'ngilochar (qiziqarli faktlar, xatolar, tajribalar)\n"
            f"- 20% trend (viral formatlar, challenge)\n"
            f"- 15% sotuv (mahsulot, xizmat taqdimoti)\n\n"
            f"═══ HOOK QOIDALARI ═══\n"
            f"Yaxshi hook namunalari:\n"
            f"- \"Bu xatoni 90% fermerlar qiladi!\"\n"
            f"- \"Pomidoringiz sarqayaptimi? Sababi BU\"\n"
            f"- \"1 sotixdan 50 kg bodring — qanday?\"\n"
            f"- \"Hech kim bilmaydigan 3 ta sir\"\n"
            f"Yomon hook (BUNDAY QILMA): \"Assalomu alaykum, bugun sizlarga...\"\n\n"
            f"═══ TIL VA USLUB ═══\n"
            f"- O'zbek tilida (sodda, xalq tili)\n"
            f"- Qisqa gaplar\n"
            f"- \"Siz\" emas, \"Sen\" — do'stona\n"
            f"- Hazil aralash lekin ortiqcha emas\n"
            f"- Emoji: 2-3 ta, ortiqcha emas\n"
            f"- Ilmiy term ishlatma — \"fotosintez\" emas, \"o'simlik quyosh yeydi\"\n\n"
            f"═══ VIZUAL STIL ═══\n"
            f"- Yorqin, tabiiy ranglar\n"
            f"- Yaqin plan (close-up) ko'p ishlatilsin\n"
            f"- Tez montaj (har kadr 2-4 sekund)\n"
            f"- Matn overlay: kaltta, katta shriftda, kontrastli rangda\n"
            f"- Before/After format yaxshi ishlaydi"
        )


# Saqlash uchun barcha fieldlar
_ACCOUNT_FIELDS = [
    "id", "instagram", "niche", "chrome_profile", "ai_personality",
    "target_audience", "language", "languages", "active", "hashtags",
    "posting_times", "content_mix", "competitors", "posting_frequency", "ai_tone",
]


class AccountManager:
    """Multi-account boshqaruvchi. To'liq CRUD."""

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._active_id: str = ""
        self._load()

    def _load(self) -> None:
        """accounts.json dan yuklash yoki default yaratish."""
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for acc_data in data.get("accounts", []):
                    # Backward compatibility: yangi fieldlar yo'q bo'lsa default
                    acc_data.setdefault("languages", [acc_data.get("language", "uz")])
                    acc_data.setdefault("competitors", [])
                    acc_data.setdefault("posting_frequency", 1)
                    acc_data.setdefault("ai_tone", "professional")
                    # Faqat Account fieldlariga mos kalitlarni olish
                    filtered = {k: v for k, v in acc_data.items() if k in _ACCOUNT_FIELDS}
                    acc = Account(**filtered)
                    self._accounts[acc.id] = acc
                self._active_id = data.get("default_account", "")
                logger.info(f"✅ {len(self._accounts)} ta akkaunt yuklandi")
            except Exception as e:
                logger.error(f"accounts.json yuklashda xato: {e}")
                self._create_default()
        else:
            self._create_default()

    def _create_default(self) -> None:
        """Default akkaunt yaratish."""
        default = Account(
            id="agro_uruglar",
            instagram=f"@{TARGET_PROFILE}",
            niche="O'zbekiston qishloq xo'jaligi — urug'lar, parvarish, hosil",
            chrome_profile=CHROME_PROFILE_DIR,
            ai_personality="Professional agro ekspert va Instagram strategist",
            target_audience="Fermerlar, issiqxona egalari, urug' xaridorlari",
            hashtags=["#agro", "#urug", "#hosil", "#fermer", "#qishloqxojaligi"],
            posting_times=["19:00", "20:00", "07:00"],
            competitors=["agro_seeds_uz", "fermer_market"],
            posting_frequency=2,
            ai_tone="professional",
        )
        self._accounts[default.id] = default
        self._active_id = default.id
        self.save()
        logger.info("📁 Default akkaunt yaratildi")

    def save(self) -> None:
        """accounts.json ga saqlash — barcha fieldlar bilan."""
        data = {
            "default_account": self._active_id,
            "accounts": [],
        }
        for acc in self._accounts.values():
            acc_dict = {}
            for f in _ACCOUNT_FIELDS:
                acc_dict[f] = getattr(acc, f, None)
            data["accounts"].append(acc_dict)

        ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @property
    def active(self) -> Account:
        """Joriy faol akkaunt."""
        if self._active_id and self._active_id in self._accounts:
            return self._accounts[self._active_id]
        if self._accounts:
            return next(iter(self._accounts.values()))
        return Account(id="default", instagram=f"@{TARGET_PROFILE}")

    @property
    def all_accounts(self) -> List[Account]:
        return list(self._accounts.values())

    @property
    def active_accounts(self) -> List[Account]:
        """Faqat aktiv akkauntlar."""
        return [a for a in self._accounts.values() if a.active]

    @property
    def count(self) -> int:
        return len(self._accounts)

    def switch(self, account_id: str) -> bool:
        """Akkauntni almashtirish."""
        if account_id in self._accounts:
            self._active_id = account_id
            self.save()
            logger.info(f"🔄 Akkaunt almashtirildi: {self._accounts[account_id].instagram}")
            return True
        return False

    def add(self, account: Account) -> None:
        """Yangi akkaunt qo'shish."""
        self._accounts[account.id] = account
        self.save()
        logger.info(f"➕ Yangi akkaunt: {account.instagram}")

    def remove(self, account_id: str) -> bool:
        """Akkauntni o'chirish."""
        if account_id in self._accounts and len(self._accounts) > 1:
            del self._accounts[account_id]
            if self._active_id == account_id:
                self._active_id = next(iter(self._accounts))
            self.save()
            return True
        return False

    def get(self, account_id: str) -> Optional[Account]:
        return self._accounts.get(account_id)

    def update(self, account_id: str, **kwargs) -> bool:
        """Akkaunt ma'lumotlarini yangilash."""
        acc = self._accounts.get(account_id)
        if not acc:
            return False
        for key, value in kwargs.items():
            if hasattr(acc, key):
                setattr(acc, key, value)
        self.save()
        logger.info(f"✏️ Akkaunt yangilandi: {acc.instagram} ({list(kwargs.keys())})")
        return True

    def format_account_short(self, acc: Account) -> str:
        """Akkauntni qisqa formatda."""
        active_mark = "✅" if acc.id == self._active_id else "⬜"
        return f"{active_mark} *{acc.instagram}* — {acc.niche[:30]}"

    def format_account_full(self, acc: Account) -> str:
        """Akkauntni to'liq formatda."""
        active_mark = "✅ FAOL" if acc.id == self._active_id else "⬜"
        tags = " ".join(acc.hashtags[:5]) if acc.hashtags else "—"
        comps = ", ".join(f"@{c}" for c in acc.competitors[:3]) if acc.competitors else "—"
        return (
            f"{active_mark}\n"
            f"🌿 *{acc.instagram}*\n"
            f"📁 Chrome: `{acc.chrome_profile}`\n"
            f"🎯 Niche: {acc.niche}\n"
            f"👥 Auditoriya: {acc.target_audience}\n"
            f"#️⃣ Hashtags: {tags}\n"
            f"⏰ Post vaqtlari: {', '.join(acc.posting_times)}\n"
            f"📊 Kunlik post: {acc.posting_frequency}\n"
            f"🎭 AI tone: {acc.ai_tone}\n"
            f"🕵️ Raqobatchilar: {comps}\n"
            f"🌐 Tillar: {', '.join(acc.languages)}"
        )


# Global instance
accounts = AccountManager()
