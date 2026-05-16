"""
Agro AI — Sales AI Engine
Mahsulot katalogi asosida sotuv kontent yaratish.
Real narx, stok, mavsum ma'lumotlari bilan.
"""

import logging
from typing import Dict, List, Optional

from app.accounts import Account
from app.ai.base import BaseAIEngine
from app.memory.manager import memory
from app.products.catalog import Product, catalog

logger = logging.getLogger("agro_ai.ai.sales")


class SalesEngine(BaseAIEngine):
    """
    Sotuv AI Engine.
    Mahsulot katalogidan real ma'lumot bilan kontent yaratadi.
    """

    engine_name: str = "sales"
    default_max_tokens: int = 1000
    default_temperature: float = 0.85

    def __init__(self, account: Account):
        super().__init__(account)

    async def generate_sales_post(self, product_id: str) -> str:
        """Bitta mahsulot uchun sotuv post yaratish."""
        product = catalog.get_product(product_id)
        if not product:
            return "❌ Mahsulot topilmadi."

        if product.stock <= 0:
            return f"⚠️ {product.name} stokda yo'q."

        context = self._build_product_context(product)
        learning = memory.get_learning_context(self.account.id, "sales", limit=3)
        avoid = memory.avoid_repetition_context(self.account.id, "sales", limit=5)

        prompt = (
            f"Mahsulot: {product.name}\n"
            f"Narx: {product.price:,} {product.currency}\n"
            f"Tavsif: {product.description}\n"
            f"Mavsum: {product.best_season}\n"
            f"Stok: {product.stock} dona\n\n"
            f"Shu mahsulot uchun Instagram SOTUV POST yarat:\n\n"
            f"1. HOOK (1 qator, kuchli, sotuvga undovchi)\n"
            f"2. CAPTION (150-200 so'z):\n"
            f"   - Muammo → Yechim formati\n"
            f"   - Real narx va stok ko'rsat\n"
            f"   - Urgency (cheklangan stok)\n"
            f"   - CTA (buyurtma berish)\n"
            f"3. HASHTAGS (10 ta — sotuv + niche)\n"
            f"4. STORY IDEA (sotuv uchun)\n\n"
            f"O'zbek tilida, emoji bilan, professional."
        )

        if learning:
            prompt += f"\n\n{learning}"
        if avoid:
            prompt += f"\n\n{avoid}"

        result = await self.generate(prompt, context=context, max_tokens=1000)

        # Memory'ga saqlash
        memory.save_memory(
            account_id=self.account.id,
            category="sales",
            content=result[:200],
            tags=["sales", product.category, product.id],
            score=6.0,
            source="generated",
            metadata={"product_id": product.id, "product_name": product.name},
        )

        return f"📦 *SOTUV POST: {product.name}*\n💰 {product.price:,} {product.currency}\n\n{result}"

    async def generate_catalog_post(self) -> str:
        """Barcha stokdagi mahsulotlar uchun umumiy sotuv post."""
        products = catalog.get_in_stock()
        if not products:
            return "⚠️ Stokda mahsulot yo'q."

        product_list = "\n".join(
            f"- {p.name}: {p.price:,} {p.currency} (stok: {p.stock})"
            for p in products[:10]
        )

        prompt = (
            f"Mahsulotlar ro'yxati:\n{product_list}\n\n"
            f"Shu mahsulotlar uchun UMUMIY KATALOG POST yarat:\n"
            f"- Hook (diqqat tortuvchi)\n"
            f"- Har bir mahsulotni qisqa taqdim et\n"
            f"- Narxlar va stok\n"
            f"- CTA (buyurtma berish usuli)\n"
            f"- 10 ta hashtag\n\n"
            f"O'zbek tilida, emoji bilan."
        )

        result = await self.generate(prompt, max_tokens=1200)
        return f"📦 *KATALOG POST*\n\n{result}"

    async def generate_seasonal_post(self, season: str) -> str:
        """Mavsumga mos mahsulotlar uchun post."""
        products = catalog.get_by_season(season)
        if not products:
            return f"⚠️ '{season}' mavsumiga mos mahsulot topilmadi."

        product_list = "\n".join(
            f"- {p.name}: {p.price:,} {p.currency} | {p.description[:50]}"
            for p in products
        )

        prompt = (
            f"Mavsum: {season}\n"
            f"Mavsumga mos mahsulotlar:\n{product_list}\n\n"
            f"Shu mavsum uchun MAVSUMIY SOTUV POST yarat:\n"
            f"- Hook (mavsumga bog'liq, urgency)\n"
            f"- Caption (nima uchun hozir sotib olish kerak)\n"
            f"- Har bir mahsulotni tavsiya et\n"
            f"- CTA\n"
            f"- 10 ta hashtag\n\n"
            f"O'zbek tilida, professional."
        )

        result = await self.generate(prompt, max_tokens=1000)
        return f"🌱 *MAVSUMIY POST: {season.upper()}*\n\n{result}"

    async def generate_promo_post(self, product_id: str, discount_pct: int = 10) -> str:
        """Chegirma/aksiya post yaratish."""
        product = catalog.get_product(product_id)
        if not product:
            return "❌ Mahsulot topilmadi."

        old_price = product.price
        new_price = int(old_price * (100 - discount_pct) / 100)

        prompt = (
            f"AKSIYA POST yarat:\n"
            f"Mahsulot: {product.name}\n"
            f"Eski narx: {old_price:,} {product.currency}\n"
            f"Yangi narx: {new_price:,} {product.currency} ({discount_pct}% chegirma)\n"
            f"Stok: {product.stock} dona\n\n"
            f"Format:\n"
            f"- URGENCY hook (cheklangan vaqt/stok)\n"
            f"- Eski vs yangi narx ko'rsat\n"
            f"- Nima uchun bu mahsulot kerak\n"
            f"- CTA (tez buyurtma)\n"
            f"- 10 ta hashtag\n\n"
            f"O'zbek tilida, emoji bilan, FOMO yaratuvchi."
        )

        result = await self.generate(prompt, max_tokens=800)
        return (
            f"🔥 *AKSIYA: {product.name}*\n"
            f"~~{old_price:,}~~ → *{new_price:,} {product.currency}* (-{discount_pct}%)\n\n"
            f"{result}"
        )

    def _build_product_context(self, product: Product) -> Dict:
        """Mahsulot konteksti."""
        ctx = self.build_context()
        ctx.update({
            "product_name": product.name,
            "product_price": f"{product.price:,} {product.currency}",
            "product_stock": product.stock,
            "product_season": product.best_season,
            "product_category": product.category,
        })
        return ctx
