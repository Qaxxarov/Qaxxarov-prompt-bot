"""
Agro AI — 🕵️ COMPETITOR MONITOR Telegram handler
Raqobatchi real-time monitoring boshqaruvi.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.competitors.monitor import CompetitorMonitor

logger = logging.getLogger("agro_ai.bot.compmon")


def compmon_menu():
    """Competitor Monitor menyusi."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Raqobatchi Qo'shish", callback_data="compmon:add")],
        [InlineKeyboardButton("📋 Ro'yxat", callback_data="compmon:list")],
        [InlineKeyboardButton("🔔 Alertlar", callback_data="compmon:alerts")],
        [InlineKeyboardButton("📊 Monitoring Holati", callback_data="compmon:status")],
        [InlineKeyboardButton("🔄 Hozir Skanerlash", callback_data="compmon:scan")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data="compmon:remove")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("compmon")
@error_handler
async def handle_compmon(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🕵️ COMPETITOR MONITOR handler."""
    await send_typing(update, context)
    acc = accounts.active
    monitor = CompetitorMonitor(acc.id)

    if action == "add":
        text = (
            "➕ *RAQOBATCHI QO'SHISH*\n\n"
            "Raqobatchi username'ini yuboring:\n"
            "Masalan: `@competitor_name`\n\n"
            "Yoki quyidagi formatda:\n"
            "`/addcomp username`"
        )
        # Set state for next message
        context.user_data["awaiting_competitor"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "list":
        competitors = monitor.get_all()
        if competitors:
            lines = ["📋 *RAQOBATCHILAR RO'YXATI*\n"]
            for i, comp in enumerate(competitors, 1):
                username = comp.get("username", "")
                followers = comp.get("followers", 0)
                avg_views = comp.get("avg_views", 0)
                lines.append(
                    f"*{i}.* @{username}\n"
                    f"   👥 {followers:,} | 👁 {avg_views:,} avg views"
                )
            text = "\n".join(lines)
        else:
            text = (
                "📋 *RAQOBATCHILAR*\n\n"
                "_(Hali raqobatchi qo'shilmagan.)_\n\n"
                "➕ Qo'shish uchun tugmani bosing."
            )
        await send_message(update, text, keyboard=compmon_menu())
        return

    if action == "alerts":
        alerts = monitor.get_recent_alerts(10)
        if alerts:
            lines = ["🔔 *OXIRGI ALERTLAR*\n"]
            for a in reversed(alerts):
                msg = a.get("message", "")
                lines.append(f"• {msg}")
            text = "\n".join(lines)
        else:
            text = "🔔 *ALERTLAR*\n\n_(Hali alert yo'q.)_"
        await send_message(update, text, keyboard=compmon_menu())
        return

    if action == "status":
        summary = monitor.get_summary()
        await send_message(update, summary, keyboard=compmon_menu())
        return

    if action == "scan":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Skanerlash* boshlandi...", parse_mode="Markdown"
            )

        alerts = await monitor.scan_all()
        if alerts:
            lines = ["✅ *SKAN TUGADI*\n\n🔔 Yangi alertlar:\n"]
            for a in alerts:
                lines.append(f"• {a.message}")
            text = "\n".join(lines)
        else:
            text = "✅ *SKAN TUGADI*\n\nYangi o'zgarish topilmadi."
        await send_message(update, text, keyboard=compmon_menu())
        return

    if action == "remove":
        competitors = monitor.get_all()
        if competitors:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            buttons = []
            for comp in competitors:
                username = comp.get("username", "")
                buttons.append([InlineKeyboardButton(
                    f"🗑 @{username}", callback_data=f"compmon:del_{username}"
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, "🗑 *O'chirish uchun tanlang:*", keyboard=kb)
        else:
            await send_message(update, "_(Ro'yxat bo'sh.)_", keyboard=compmon_menu())
        return

    # Delete specific competitor
    if action.startswith("del_"):
        username = action[4:]
        if monitor.remove_competitor(username):
            text = f"✅ @{username} o'chirildi."
        else:
            text = f"❌ @{username} topilmadi."
        await send_message(update, text, keyboard=compmon_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=compmon_menu())


async def handle_competitor_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Foydalanuvchi competitor username yuborganda.
    Returns True if handled, False otherwise.
    """
    if not context.user_data.get("awaiting_competitor"):
        return False

    text = update.message.text.strip()
    username = text.lstrip("@").replace("/addcomp ", "").strip()

    if not username or len(username) < 2:
        await update.message.reply_text("❌ Username noto'g'ri. Qayta yuboring.")
        return True

    acc = accounts.active
    monitor = CompetitorMonitor(acc.id)

    if monitor.add_competitor(username):
        await update.message.reply_text(
            f"✅ @{username} monitoring ro'yxatiga qo'shildi!\n\n"
            f"Har 6 soatda avtomatik skanerlanadi.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(f"⚠️ @{username} allaqachon ro'yxatda.")

    context.user_data["awaiting_competitor"] = False
    return True
