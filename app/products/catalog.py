"""
Agro AI — Mahsulot Katalogi
Mahsulot bazasini boshqarish: qo'shish, o'chirish, narx yangilash.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import DATA_DIR

logger = logging.getLogger("agro_ai.products.catalog")

PRODUCTS_FILE = DATA_DIR / "products.json"


@dataclass
class Product:
    """Bitta mahsulot."""
    id: str = ""
    name: str = ""
    category: str = ""
    price: int = 0
    currency: str = "UZS"
    stock: int = 0
    description: str = ""
    best_season: str = ""
    image_url: str = ""
    tags: List[str] = field(default_factory=list)
    active: bool = True
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = time.time()


class ProductCatalog:
    """
    Mahsulot katalogi boshqaruvchisi.
    JSON-based persistent storage.
    """

    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._load()

    def _load(self) -> None:
        """products.json dan yuklash."""
        if PRODUCTS_FILE.exists():
            try:
                with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for p_data in data.get("products", []):
                    product = Product(**p_data)
                    self._products[product.id] = product
                logger.info(f"📦 {len(self._products)} ta mahsulot yuklandi")
            except Exception as e:
                logger.error(f"Products yuklashda xato: {e}")
                self._create_defaults()
        else:
            self._create_defaults()

    def _create_defaults(self) -> None:
        """Default mahsulotlar yaratish."""
        defaults = [
            Product(
                id="tomato_bella_f1",
                name="Pomidor Bella F1",
                category="urug'lar",
                price=25000,
                currency="UZS",
                stock=500,
                description="Yuqori hosildor gibrid pomidor. 120-130 kun vegetatsiya davri.",
                best_season="mart-aprel",
                tags=["pomidor", "gibrid", "hosildor"],
            ),
            Product(
                id="bodring_ajax_f1",
                name="Bodring Ajax F1",
                category="urug'lar",
                price=30000,
                currency="UZS",
                stock=300,
                description="Erta pishar, kasalliklarga chidamli bodring.",
                best_season="aprel-may",
                tags=["bodring", "gibrid", "erta"],
            ),
            Product(
                id="qalampir_california",
                name="Qalampir California Wonder",
                category="urug'lar",
                price=20000,
                currency="UZS",
                stock=400,
                description="Katta mevalik, shirin qalampir. Issiqxona va ochiq yerda.",
                best_season="fevral-mart",
                tags=["qalampir", "shirin", "issiqxona"],
            ),
            Product(
                id="sabzi_nantes",
                name="Sabzi Nantes",
                category="urug'lar",
                price=15000,
                currency="UZS",
                stock=600,
                description="Klassik shirin sabzi. Barcha tuproqlarda yaxshi o'sadi.",
                best_season="mart-aprel",
                tags=["sabzi", "klassik", "universal"],
            ),
            Product(
                id="issiqxona_paket",
                name="Issiqxona Starter Paket",
                category="paketlar",
                price=150000,
                currency="UZS",
                stock=50,
                description="5 turdagi urug' + parvarish qo'llanma + video darslar.",
                best_season="yil davomida",
                tags=["paket", "issiqxona", "starter"],
            ),
        ]
        for p in defaults:
            self._products[p.id] = p
        self._save()
        logger.info("📦 Default mahsulotlar yaratildi")

    def _save(self) -> None:
        """products.json ga saqlash."""
        try:
            data = {"products": [asdict(p) for p in self._products.values()]}
            PRODUCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Products saqlashda xato: {e}")

    # ─────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────

    def add_product(
        self,
        product_id: str,
        name: str,
        category: str,
        price: int,
        stock: int = 0,
        description: str = "",
        best_season: str = "",
        tags: List[str] = None,
    ) -> Product:
        """Yangi mahsulot qo'shish."""
        product = Product(
            id=product_id,
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description,
            best_season=best_season,
            tags=tags or [],
        )
        self._products[product.id] = product
        self._save()
        logger.info(f"➕ Mahsulot qo'shildi: {name}")
        return product

    def remove_product(self, product_id: str) -> bool:
        """Mahsulotni o'chirish."""
        if product_id in self._products:
            del self._products[product_id]
            self._save()
            return True
        return False

    def update_price(self, product_id: str, new_price: int) -> bool:
        """Narxni yangilash."""
        if product_id in self._products:
            self._products[product_id].price = new_price
            self._products[product_id].updated_at = time.time()
            self._save()
            return True
        return False

    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Stokni yangilash."""
        if product_id in self._products:
            self._products[product_id].stock = new_stock
            self._products[product_id].updated_at = time.time()
            self._save()
            return True
        return False

    def get_product(self, product_id: str) -> Optional[Product]:
        """Mahsulotni ID bo'yicha olish."""
        return self._products.get(product_id)

    def get_all(self, active_only: bool = True) -> List[Product]:
        """Barcha mahsulotlar."""
        products = list(self._products.values())
        if active_only:
            products = [p for p in products if p.active]
        return products

    def get_by_category(self, category: str) -> List[Product]:
        """Kategoriya bo'yicha."""
        return [p for p in self._products.values() if p.category == category and p.active]

    def get_in_stock(self) -> List[Product]:
        """Stokda bor mahsulotlar."""
        return [p for p in self._products.values() if p.stock > 0 and p.active]

    def get_by_season(self, season: str) -> List[Product]:
        """Mavsumga mos mahsulotlar."""
        season = season.lower()
        return [
            p for p in self._products.values()
            if season in p.best_season.lower() and p.active
        ]

    def search(self, query: str) -> List[Product]:
        """Mahsulot qidirish."""
        query = query.lower()
        results = []
        for p in self._products.values():
            if (query in p.name.lower() or
                query in p.description.lower() or
                query in p.category.lower() or
                any(query in t for t in p.tags)):
                results.append(p)
        return results

    # ─────────────────────────────────────────────────────
    # FORMATTING
    # ─────────────────────────────────────────────────────

    def format_product(self, product: Product) -> str:
        """Mahsulotni chiroyli formatda."""
        stock_emoji = "✅" if product.stock > 0 else "❌"
        return (
            f"📦 *{product.name}*\n"
            f"📂 Kategoriya: {product.category}\n"
            f"💰 Narx: {product.price:,} {product.currency}\n"
            f"{stock_emoji} Stok: {product.stock} dona\n"
            f"📝 {product.description}\n"
            f"🌱 Mavsum: {product.best_season}"
        )

    def format_list(self, products: List[Product] = None) -> str:
        """Mahsulotlar ro'yxati."""
        if products is None:
            products = self.get_all()

        if not products:
            return "_(Mahsulot topilmadi.)_"

        lines = []
        for i, p in enumerate(products, 1):
            stock_emoji = "✅" if p.stock > 0 else "❌"
            lines.append(
                f"*{i}.* {p.name} — {p.price:,} {p.currency} {stock_emoji}"
            )
        return "\n".join(lines)

    def get_for_ai_context(self) -> str:
        """AI uchun mahsulot konteksti."""
        products = self.get_in_stock()
        if not products:
            return ""

        lines = ["MAHSULOT KATALOGI (stokda bor):"]
        for p in products:
            lines.append(
                f"- {p.name} | {p.price:,} {p.currency} | "
                f"Stok: {p.stock} | Mavsum: {p.best_season} | {p.description[:50]}"
            )
        return "\n".join(lines)


# Global instance
catalog = ProductCatalog()
