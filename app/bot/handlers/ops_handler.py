"""
Agro AI — 📋 OPS MANAGER Telegram handler
Morning briefing, evening report, discipline, monitoring.
"""

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.ops.discipline import DisciplineTracker
from app.ops.manager import OpsManager
from app.ops.monitor import InstagramMonitor

logger = logging.getLogger("agro_ai.bot.ops")


@register("ops")
@error_handler
async def handle_ops(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📋 OPS MANAGER handler."""
    await send_typing(update, context)
    acc = accounts.active
    ops = OpsManager(acc.id)

    if action == "status":
        text = ops.quick_status()
        await send_message(update, text, keyboard=back_button())
        return

    if action == "morning":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "🌅 *Ertalabki brifing* tayyorlanmoqda...",
                parse_mode="Markdown",
            )
        text = await ops.morning_briefing()
        await send_message(update, text, keyboard=back_button())
        return

    if action == "evening":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "🌙 *Kechki hisobot* tayyorlanmoqda...\n"
                "_(Yangi skan qilinmoqda)_",
                parse_mode="Markdown",
            )

        # Background scan
        loop = asyncio.get_event_loop()
        monitor = InstagramMonitor(acc.id)

        try:
            await loop.run_in_executor(None, monitor.scan_now)
        except Exception as e:
            logger.error(f"Skan xatosi: {e}")

        # Refresh ops with new data
        ops = OpsManager(acc.id)
        text = await ops.evening_report()
        await send_message(update, text, keyboard=back_button())
        return

    if action == "discipline":
        monitor = InstagramMonitor(acc.id)
        state = monitor.state
        history = monitor.get_history(7)
        tracker = DisciplineTracker()
        text = tracker.format_discipline_report(state, history)
        await send_message(update, text, keyboard=back_button())
        return

    if action == "weekly":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "📅 *Haftalik hisobot* tayyorlanmoqda...",
                parse_mode="Markdown",
            )
        text = await ops.weekly_report()
        await send_message(update, text, keyboard=back_button())
        return

    if action == "scan":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "🔄 *Yangi skan boshlandi...*\n"
                f"📁 Profil: `{accounts.active.chrome_profile}`\n"
                "_(Chrome yopiq bo'lishi kerak)_",
                parse_mode="Markdown",
            )

        loop = asyncio.get_event_loop()
        monitor = InstagramMonitor(acc.id)

        try:
            state = await loop.run_in_executor(None, monitor.scan_now)
            posted = "✅ Ha" if state.posted_today else "❌ Yo'q"
            text = (
                f"✅ *Skan tugadi!*\n\n"
                f"👥 Followers: {state.followers:,}\n"
                f"👁 O'rtacha: {state.avg_views:,}\n"
                f"📈 ER: {state.avg_er}%\n"
                f"📅 Bugun post: {posted}\n"
                f"🔥 Streak: {state.posting_streak} kun"
            )
        except Exception as e:
            text = f"❌ *Skan xatosi:* `{str(e)[:200]}`"

        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum ops buyrug'i.", keyboard=back_button())
