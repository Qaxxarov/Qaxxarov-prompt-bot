"""
Agro AI — 💡 G'OYALAR + 🎣 HOOKLAR handlers
Real AI engines: HookEngine for hooks, BaseAIEngine for ideas.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.base import BaseAIEngine
from app.ai.hooks import HookEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions

logger = logging.getLogger("agro_ai.bot.goyalar")


@register("goya")
@error_handler
async def handle_goyalar(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """💡 G'OYALAR handler — AI-powered kontent g'oyalari."""
    await send_typing(update, context)
    acc = accounts.active
    engine = BaseAIEngine(acc)
    session = sessions.get(update.effective_user.id)
    ctx = engine.build_context(session.stats) if session.has_data else None

    tasks = {
        "viral": (
            "5 ta viral reel g'oyasi yarat.\n"
            "Har biri uchun:\n"
            "• Sarlavha (emoji bilan)\n"
            "• Hook (birinchi 3 soniya matni)\n"
            "• Kontent tavsifi (2-3 jumla)\n"
            "• Viral sabab (nima uchun ishlaydi)\n"
            "• Taxminiy ER\n\n"
            "Qishloq xo'jaligi, urug', hosil mavzularida.\n"
            "Emotsional, amaliy, cinematic."
        ),
        "story": (
            "5 ta emotsional story kontent g'oyasi yarat.\n"
            "Har biri:\n"
            "• Mavzu (emoji bilan)\n"
            "• Hook (birinchi gap)\n"
            "• Hikoya qisqacha (3 jumla)\n"
            "• Emotsional trigger\n"
            "• Format (reel/story/carousel)\n\n"
            "Fermer hayoti, qiyinchilik, muvaffaqiyat mavzularida."
        ),
        "trend": (
            "5 ta trend format g'oyasi yarat.\n"
            "Har biri:\n"
            "• Format nomi (POV/Before-After/GRWM/Day-in-life/Trending audio)\n"
            "• Hook\n"
            "• Qanday moslashtiriladi (agro uchun)\n"
            "• Nima uchun trending\n\n"
            "Qishloq xo'jaligi uchun moslashtirilgan."
        ),
        "shok": (
            "5 ta SHOK kontent g'oyasi yarat.\n"
            "Har biri:\n"
            "• Shok hook (hayratlanarli)\n"
            "• Kontent tavsifi\n"
            "• Nima uchun viral (psixologik sabab)\n\n"
            "Hayratlanarli faktlar, kutilmagan natijalar, miflarni buzish."
        ),
        "agro": (
            "5 ta agro-specific kontent g'oyasi yarat.\n"
            "Har biri:\n"
            "• Mavzu (urug'/parvarish/hosil/issiqxona/kasallik)\n"
            "• Hook\n"
            "• Amaliy qiymat (fermer nima o'rganadi)\n"
            "• Format tavsiyasi\n\n"
            "Juda amaliy va foydali. Real natijalar bilan."
        ),
    }

    task = tasks.get(action)
    if not task:
        await send_message(update, "❓ Noma'lum g'oya turi.", keyboard=back_button())
        return

    titles = {
        "viral": "🎬 VIRAL G'OYALAR",
        "story": "📖 STORY KONTENT",
        "trend": "⚡ TREND G'OYALAR",
        "shok": "😱 SHOK KONTENT",
        "agro": "🌾 AGRO G'OYALAR",
    }

    # Loading message
    if update.callback_query:
        title_text = titles.get(action, "G'OYALAR")
        await update.callback_query.message.reply_text(
            f"⏳ *{title_text}* yaratilmoqda...",
            parse_mode="Markdown",
        )

    result = await engine.generate(task, context=ctx, max_tokens=1000)
    title = titles.get(action, "G'OYALAR")
    text = f"💡 *{title}*\n\n{result}"
    await send_message(update, text, keyboard=back_button())


@register("hook")
@error_handler
async def handle_hooklar(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🎣 HOOKLAR handler — HookEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = HookEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    titles = {
        "viral": "🔥 VIRAL HOOKLAR",
        "fear": "😱 QO'RQUV HOOKLAR",
        "curiosity": "🤔 QIZIQISH HOOKLAR",
        "benefit": "💰 FOYDA HOOKLAR",
        "niche": "🎯 NICHE HOOKLAR",
    }

    if action not in titles:
        await send_message(update, "❓ Noma'lum hook turi.", keyboard=back_button())
        return

    # Loading message
    if update.callback_query:
        cat_info = engine.CATEGORIES.get(action, {})
        emoji = cat_info.get("emoji", "🎣")
        await update.callback_query.message.reply_text(
            f"⏳ {emoji} *{titles[action]}* yaratilmoqda...\n"
            f"_(Psixologik asos: {cat_info.get('psychology', 'viral pattern')[:60]}...)_",
            parse_mode="Markdown",
        )

    # Map action to HookEngine category
    category_map = {
        "viral": "viral",
        "fear": "fear",
        "curiosity": "curiosity",
        "benefit": "benefit",
        "niche": "viral",  # niche uses viral with agro context
    }

    category = category_map.get(action, "viral")
    result = await engine.generate_hooks(category=category, count=10, stats=stats)

    text = f"🎣 *{titles[action]}*\n\n{result}"
    await send_message(update, text, keyboard=back_button())
