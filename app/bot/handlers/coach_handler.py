"""
Agro AI — 🎯 COACH + 🏷 HASHTAG + 📊 HOOK SCORER handlers
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.coach import CreatorCoachEngine
from app.ai.hashtags import HashtagEngine
from app.ai.hook_scorer import HookScorerEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions
from app.ops.monitor import InstagramMonitor

logger = logging.getLogger("agro_ai.bot.coach")


@register("coach")
@error_handler
async def handle_coach(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🎯 CREATOR COACH handler."""
    await send_typing(update, context)
    acc = accounts.active
    engine = CreatorCoachEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    if action == "missions":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "🎯 *Kunlik vazifalar* yaratilmoqda...", parse_mode="Markdown"
            )
        result = await engine.daily_missions(stats=stats)
        await send_message(update, f"🎯 *BUGUNGI VAZIFALAR*\n\n{result}", keyboard=back_button())
        return

    if action == "motivate":
        monitor = InstagramMonitor(acc.id)
        state = monitor.state
        result = await engine.motivational_push(
            streak=state.posting_streak, posted_today=state.posted_today
        )
        await send_message(update, f"💪 *MOTIVATSIYA*\n\n{result}", keyboard=back_button())
        return

    if action == "weekly":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "📋 *Haftalik coaching*...", parse_mode="Markdown"
            )
        monitor = InstagramMonitor(acc.id)
        from app.ops.discipline import DisciplineTracker
        disc = DisciplineTracker().compute_discipline_score(monitor.state, monitor.get_history(7))
        result = await engine.weekly_coaching(stats=stats, discipline_score=disc["score"])
        await send_message(update, f"📋 *HAFTALIK COACHING*\n\n{result}", keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum coach buyrug'i.", keyboard=back_button())


@register("hashtag")
@error_handler
async def handle_hashtag(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🏷 HASHTAG handler."""
    await send_typing(update, context)
    acc = accounts.active
    engine = HashtagEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    if action == "generate":
        result = await engine.generate_set("qishloq xo'jaligi va urug'lar", stats=stats)
        await send_message(update, f"🏷 *HASHTAG SETI*\n\n{result}", keyboard=back_button())
        return

    if action == "trending":
        result = await engine.trending_hashtags()
        await send_message(update, f"📈 *TRENDING HASHTAGLAR*\n\n{result}", keyboard=back_button())
        return

    if action == "quick":
        tags = engine.get_quick_set()
        text = f"🏷 *TEZKOR HASHTAG SETI*\n\n{' '.join(tags)}\n\n_(Nusxa oling va ishlating)_"
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum hashtag buyrug'i.", keyboard=back_button())


@register("hscore")
@error_handler
async def handle_hook_score(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📊 HOOK SCORER handler."""
    await send_typing(update, context)
    acc = accounts.active
    engine = HookScorerEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    if action == "score":
        # Demo hook scoring
        result = await engine.score_hook(
            "Bu xatoni qilsangiz — hosil yo'qoladi!", stats=stats
        )
        await send_message(update, f"📊 *HOOK SCORE*\n\n{result}", keyboard=back_button())
        return

    if action == "compare":
        hooks = [
            "Bu xatoni qilsangiz — hosil yo'qoladi!",
            "Hech kim bilmagan urug' siri...",
            "1 kg urug'dan 50 kg hosil — mumkinmi?",
        ]
        result = await engine.compare_hooks(hooks, stats=stats)
        await send_message(update, f"📊 *HOOK SOLISHTIRISH*\n\n{result}", keyboard=back_button())
        return

    if action == "optimize":
        result = await engine.optimize_hook("Bu xatoni qilsangiz hosil yo'qoladi")
        await send_message(update, f"✨ *HOOK OPTIMIZATSIYA*\n\n{result}", keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum scorer buyrug'i.", keyboard=back_button())
