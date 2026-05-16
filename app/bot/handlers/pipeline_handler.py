"""
Agro AI — 🎬 PIPELINE Telegram handler
Full content pipeline — one command, complete reel package.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.pipeline import ContentPipelineEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions

logger = logging.getLogger("agro_ai.bot.pipeline")


@register("pipe")
@error_handler
async def handle_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🎬 CONTENT PIPELINE handler."""
    await send_typing(update, context)
    acc = accounts.active
    engine = ContentPipelineEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    topics = {
        "urug": "Urug' saqlash va parvarish qilish usullari",
        "hosil": "Hosil ko'paytirish sirlari",
        "issiqxona": "Issiqxona texnologiyalari va boshqaruvi",
        "kasallik": "O'simlik kasalliklari va davolash",
        "tuproq": "Tuproq tayyorlash va unumdorlik",
        "quick": "Bugungi eng yaxshi mavzu",
    }

    if action not in topics:
        await send_message(update, "❓ Noma'lum pipeline turi.", keyboard=back_button())
        return

    topic = topics[action]

    # Loading
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *TO'LIQ KONTENT PAKETI* yaratilmoqda...\n"
            f"📌 Mavzu: _{topic}_\n\n"
            "_(Bu 15-30 soniya olishi mumkin)_",
            parse_mode="Markdown",
        )

    if action == "quick":
        # Tezkor — bitta AI chaqiruv
        result = await engine.quick_package(topic, stats=stats)
        text = f"🎬 *TEZKOR KONTENT PAKETI*\n\n{result}"
    else:
        # To'liq pipeline — barcha engine'lar
        pkg = await engine.generate_full_package(
            topic=topic,
            goal="viral + engagement + sotuv",
            stats=stats,
        )
        text = engine.format_package(pkg)

    await send_message(update, text, keyboard=back_button())
