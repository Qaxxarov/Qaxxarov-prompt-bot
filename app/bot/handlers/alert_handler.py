"""
Agro AI — 🔔 ALERT Telegram handler
Proaktiv alert sozlamalari va tarixi.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.ops.alerts import AlertManager

logger = logging.getLogger("agro_ai.bot.alert")


def alert_menu() -> InlineKeyboardMarkup:
    """Alert menyusi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Alert Sozlamalari", callback_data="alert:settings")],
        [InlineKeyboardButton("📜 Alert Tarixi", callback_data="alert:history")],
        [InlineKeyboardButton("🟢 Barchasini Yoqish", callback_data="alert:enable_all")],
        [InlineKeyboardButton("🔴 Barchasini O'chirish", callback_data="alert:disable_all")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("alert")
@error_handler
async def handle_alert(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🔔 ALERT handler."""
    await send_typing(update, context)
    acc = accounts.active
    alert_mgr = AlertManager(acc.id)

    if action == "settings":
        text = alert_mgr.format_settings()
        # Toggle tugmalari
        settings = alert_mgr.get_settings()
        buttons = [
            [InlineKeyboardButton(
                f"{'✅' if settings.follower_milestone else '❌'} Follower milestone",
                callback_data="alert:toggle_follower_milestone",
            )],
            [InlineKeyboardButton(
                f"{'✅' if settings.viral_reel else '❌'} Viral reel",
                callback_data="alert:toggle_viral_reel",
            )],
            [InlineKeyboardButton(
                f"{'✅' if settings.er_drop else '❌'} ER tushishi",
                callback_data="alert:toggle_er_drop",
            )],
            [InlineKeyboardButton(
                f"{'✅' if settings.er_spike else '❌'} ER o'sishi",
                callback_data="alert:toggle_er_spike",
            )],
            [InlineKeyboardButton(
                f"{'✅' if settings.no_post else '❌'} Post qilinmagan",
                callback_data="alert:toggle_no_post",
            )],
            [InlineKeyboardButton(
                f"{'✅' if settings.best_time else '❌'} Post vaqti eslatma",
                callback_data="alert:toggle_best_time",
            )],
            [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
        ]
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, text, keyboard=kb)
        return

    if action == "history":
        text = alert_mgr.format_history(limit=15)
        await send_message(update, text, keyboard=alert_menu())
        return

    if action == "enable_all":
        alert_mgr.toggle_all(True)
        await send_message(update, "✅ Barcha alertlar yoqildi!", keyboard=alert_menu())
        return

    if action == "disable_all":
        alert_mgr.toggle_all(False)
        await send_message(update, "🔴 Barcha alertlar o'chirildi.", keyboard=alert_menu())
        return

    # Toggle specific alert type
    if action.startswith("toggle_"):
        alert_type = action[7:]
        new_state = alert_mgr.toggle_alert(alert_type)
        emoji = "✅" if new_state else "❌"
        state_text = "yoqildi" if new_state else "o'chirildi"
        await send_message(
            update,
            f"{emoji} `{alert_type}` {state_text}.",
            keyboard=alert_menu(),
        )
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=alert_menu())
