"""
Agro AI — 📦 MAHSULOT Telegram handler
Mahsulot katalogi boshqaruvi va sotuv kontent yaratish.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.products.catalog import catalog

logger = logging.getLogger("agro_ai.bot.product")


def product_menu() -> InlineKeyboardMarkup:
    """Mahsulot menyusi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Mahsulot Qo'shish", callback_data="product:add")],
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="product:list")],
        [InlineKeyboardButton("💰 Narx Yangilash", callback_data="product:price")],
        [InlineKeyboardButton("📝 Sotuv Post Yaratish", callback_data="product:sales_post")],
        [InlineKeyboardButton("📦 Katalog Post", callback_data="product:catalog_post")],
        [InlineKeyboardButton("🌱 Mavsumiy Post", callback_data="product:seasonal")],
        [InlineKeyboardButton("🔥 Aksiya Post", callback_data="product:promo")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("product")
@error_handler
async def handle_product(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📦 MAHSULOT handler."""
    await send_typing(update, context)
    acc = accounts.active

    if action == "add":
        text = (
            "➕ *MAHSULOT QO'SHISH*\n\n"
            "Quyidagi formatda yuboring:\n\n"
            "`id | nom | kategoriya | narx | stok | tavsif | mavsum`\n\n"
            "Masalan:\n"
            "`yangi_pomidor | Pomidor Premium F1 | urug'lar | 35000 | 200 | "
            "Eng yangi gibrid pomidor | mart-aprel`"
        )
        context.user_data["awaiting_product_add"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "list":
        products = catalog.get_all()
        if products:
            text = f"📋 *MAHSULOTLAR RO'YXATI* ({len(products)} ta)\n\n"
            text += catalog.format_list(products)
        else:
            text = "📋 *MAHSULOTLAR*\n\n_(Ro'yxat bo'sh.)_"
        await send_message(update, text, keyboard=product_menu())
        return

    if action == "price":
        products = catalog.get_all()
        if products:
            buttons = []
            for p in products[:10]:
                buttons.append([InlineKeyboardButton(
                    f"💰 {p.name} ({p.price:,})",
                    callback_data=f"product:setprice_{p.id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "💰 *NARX YANGILASH*\n\nMahsulotni tanlang:", keyboard=kb)
        else:
            await send_message(update, "_(Mahsulot yo'q.)_", keyboard=product_menu())
        return

    if action == "sales_post":
        products = catalog.get_in_stock()
        if products:
            buttons = []
            for p in products[:10]:
                buttons.append([InlineKeyboardButton(
                    f"📝 {p.name}",
                    callback_data=f"product:gen_{p.id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "📝 *SOTUV POST*\n\nMahsulotni tanlang:", keyboard=kb)
        else:
            await send_message(update, "⚠️ Stokda mahsulot yo'q.", keyboard=product_menu())
        return

    if action == "catalog_post":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Katalog post* yaratilmoqda...", parse_mode="Markdown"
            )
        from app.ai.sales import SalesEngine
        engine = SalesEngine(acc)
        result = await engine.generate_catalog_post()
        await send_message(update, result, keyboard=product_menu())
        return

    if action == "seasonal":
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        seasons = ["mart-aprel", "may-iyun", "iyul-avgust", "sentyabr-oktyabr", "noyabr-fevral"]
        buttons = [[InlineKeyboardButton(f"🌱 {s}", callback_data=f"product:season_{s}")] for s in seasons]
        buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, "🌱 *MAVSUMIY POST*\n\nMavsumni tanlang:", keyboard=kb)
        return

    if action == "promo":
        products = catalog.get_in_stock()
        if products:
            buttons = []
            for p in products[:10]:
                buttons.append([InlineKeyboardButton(
                    f"🔥 {p.name} ({p.price:,})",
                    callback_data=f"product:promo_{p.id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "🔥 *AKSIYA POST*\n\nMahsulotni tanlang:", keyboard=kb)
        else:
            await send_message(update, "⚠️ Stokda mahsulot yo'q.", keyboard=product_menu())
        return

    # Generate sales post for specific product
    if action.startswith("gen_"):
        product_id = action[4:]
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Sotuv post* yaratilmoqda...", parse_mode="Markdown"
            )
        from app.ai.sales import SalesEngine
        engine = SalesEngine(acc)
        result = await engine.generate_sales_post(product_id)
        await send_message(update, result, keyboard=product_menu())
        return

    # Seasonal post
    if action.startswith("season_"):
        season = action[7:]
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Mavsumiy post* yaratilmoqda...", parse_mode="Markdown"
            )
        from app.ai.sales import SalesEngine
        engine = SalesEngine(acc)
        result = await engine.generate_seasonal_post(season)
        await send_message(update, result, keyboard=product_menu())
        return

    # Promo post
    if action.startswith("promo_"):
        product_id = action[6:]
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Aksiya post* yaratilmoqda...", parse_mode="Markdown"
            )
        from app.ai.sales import SalesEngine
        engine = SalesEngine(acc)
        result = await engine.generate_promo_post(product_id, discount_pct=15)
        await send_message(update, result, keyboard=product_menu())
        return

    # Set price for specific product
    if action.startswith("setprice_"):
        product_id = action[9:]
        product = catalog.get_product(product_id)
        if product:
            text = (
                f"💰 *NARX YANGILASH: {product.name}*\n\n"
                f"Hozirgi narx: {product.price:,} {product.currency}\n\n"
                f"Yangi narxni yuboring (faqat raqam):"
            )
            context.user_data["awaiting_price_update"] = product_id
        else:
            text = "❌ Mahsulot topilmadi."
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=product_menu())


async def handle_product_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Mahsulot uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    # Mahsulot qo'shish
    if context.user_data.get("awaiting_product_add"):
        text = update.message.text.strip()
        parts = [p.strip() for p in text.split("|")]

        if len(parts) < 4:
            await update.message.reply_text(
                "❌ Format noto'g'ri.\n"
                "`id | nom | kategoriya | narx | stok | tavsif | mavsum`",
                parse_mode="Markdown",
            )
            return True

        try:
            product_id = parts[0].replace(" ", "_").lower()
            name = parts[1]
            category = parts[2]
            price = int(parts[3])
            stock = int(parts[4]) if len(parts) > 4 else 0
            description = parts[5] if len(parts) > 5 else ""
            best_season = parts[6] if len(parts) > 6 else ""

            catalog.add_product(
                product_id=product_id,
                name=name,
                category=category,
                price=price,
                stock=stock,
                description=description,
                best_season=best_season,
            )
            context.user_data["awaiting_product_add"] = False
            await update.message.reply_text(
                f"✅ *{name}* qo'shildi!\n💰 {price:,} UZS | 📦 Stok: {stock}",
                parse_mode="Markdown",
            )
        except (ValueError, IndexError) as e:
            await update.message.reply_text(f"❌ Xato: {e}\nQayta urinib ko'ring.")
        return True

    # Narx yangilash
    if context.user_data.get("awaiting_price_update"):
        product_id = context.user_data["awaiting_price_update"]
        text = update.message.text.strip()

        try:
            new_price = int(text.replace(" ", "").replace(",", ""))
            if catalog.update_price(product_id, new_price):
                product = catalog.get_product(product_id)
                context.user_data["awaiting_price_update"] = None
                await update.message.reply_text(
                    f"✅ *{product.name}* narxi yangilandi: {new_price:,} UZS",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text("❌ Mahsulot topilmadi.")
        except ValueError:
            await update.message.reply_text("❌ Faqat raqam yuboring.")
        return True

    return False
