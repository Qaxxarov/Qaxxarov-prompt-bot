"""
Agro AI — 📡 TREND RADAR Telegram handler
Real-time trend detection and adaptation.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.trends import TrendRadarEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions

logger = logging.getLogger("agro_ai.bot.trend_radar")


@register("trend")
@error_handler
async def handle_trendlar(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📡 TREND RADAR handler — TrendRadarEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = TrendRadarEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    titles = {
        "mavzu": "📈 TREND MAVZULAR",
        "audio": "🎵 TREND AUDIO",
        "format": "🎬 TREND FORMATLAR",
        "hook": "⚡ HOOK TRENDLARI",
        "predict": "🔮 TREND BASHORAT",
        "daily": "📋 KUNLIK TREND HISOBOT",
        "adapt": "🎯 TREND MOSLASHTIRISH",
    }

    if action not in titles:
        await send_message(update, "❓ Noma'lum trend turi.", keyboard=back_button())
        return

    # Loading
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *{titles[action]}* tayyorlanmoqda...",
            parse_mode="Markdown",
        )

    if action == "mavzu":
        result = await engine.detect_trends(stats=stats)
    elif action == "hook":
        result = await engine.analyze_hook_trends(stats=stats)
    elif action == "predict":
        result = await engine.predict_trends(stats=stats)
    elif action == "daily":
        result = await engine.daily_trend_report(stats=stats)
    elif action == "adapt":
        result = await engine.get_trend_adaptation("POV format", stats=stats)
    elif action == "audio":
        result = await engine.generate(
            "Instagram Reels uchun trending audio strategiyasi:\n"
            "1. Qanday trending audio topish\n"
            "2. Qaysi janrlar agro uchun mos\n"
            "3. Audio + kontent moslashtirish\n"
            "4. Trending audio timing (qachon ishlatish)\n"
            "5. 5 ta hozirgi trending audio tavsiyasi",
            max_tokens=700,
        )
    elif action == "format":
        result = await engine.generate(
            "2025 yilning eng trending reel formatlari:\n"
            "Har biri: nomi, tavsifi, agro misol, momentum (1-10).\n"
            "8 ta format. Eng kuchlilaridan boshlang.",
            max_tokens=800,
        )
    else:
        result = "❓"

    text = f"📡 *{titles[action]}*\n\n{result}"
    await send_message(update, text, keyboard=back_button())
