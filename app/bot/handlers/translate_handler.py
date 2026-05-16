"""
Agro AI — 🌐 TARJIMA Telegram handler
Multi-language kontent yaratish va tarjima.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register

logger = logging.getLogger("agro_ai.bot.translate")


@register("translate")
@error_handler
async def handle_translate(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🌐 TARJIMA handler."""
    await send_typing(update, context)
    acc = accounts.active

    from app.ai.translator import ContentTranslator
    translator = ContentTranslator(acc)

    if action == "uz_ru":
        text = (
            "🇺🇿→🇷🇺 *O'ZBEKCHADAN RUSCHAGA*\n\n"
            "Tarjima qilmoqchi bo'lgan matnni yuboring.\n"
            "(Caption, hook, yoki to'liq post)"
        )
        context.user_data["awaiting_translate"] = "ru"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "ru_uz":
        text = (
            "🇷🇺→🇺🇿 *RUSCHADAN O'ZBEKCHAGA*\n\n"
            "Tarjima qilmoqchi bo'lgan matnni yuboring.\n"
            "(Caption, hook, yoki to'liq post)"
        )
        context.user_data["awaiting_translate"] = "uz"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "bilingual":
        text = (
            "🌐 *IKKI TILDA YARATISH*\n\n"
            "Mavzuni yuboring — AI ikkala tilda kontent yaratadi.\n\n"
            "Masalan: `Pomidor parvarishi haqida reel`"
        )
        context.user_data["awaiting_bilingual"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "hooks":
        text = (
            "🎣 *HOOK TARJIMA*\n\n"
            "Hook'larni yuboring (har biri yangi qatorda).\n"
            "AI ikkala tilda versiya yaratadi."
        )
        context.user_data["awaiting_hook_translate"] = True
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=back_button())


async def handle_translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Tarjima uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    from app.ai.translator import ContentTranslator
    from app.bot.keyboards import back_button

    # Oddiy tarjima
    target_lang = context.user_data.get("awaiting_translate")
    if target_lang:
        text = update.message.text.strip()
        context.user_data["awaiting_translate"] = None

        await update.message.reply_text("⏳ *Tarjima qilinmoqda...*", parse_mode="Markdown")

        acc = accounts.active
        translator = ContentTranslator(acc)
        result = await translator.translate(text, target_lang=target_lang)

        lang_name = "🇷🇺 Ruscha" if target_lang == "ru" else "🇺🇿 O'zbekcha"
        await send_message(update, f"🌐 *TARJIMA ({lang_name})*\n\n{result}", keyboard=back_button())
        return True

    # Bilingual
    if context.user_data.get("awaiting_bilingual"):
        topic = update.message.text.strip()
        context.user_data["awaiting_bilingual"] = False

        await update.message.reply_text("⏳ *Ikki tilda yaratilmoqda...*", parse_mode="Markdown")

        acc = accounts.active
        translator = ContentTranslator(acc)
        result = await translator.generate_bilingual(topic)

        await send_message(update, result, keyboard=back_button())
        return True

    # Hook tarjima
    if context.user_data.get("awaiting_hook_translate"):
        text = update.message.text.strip()
        context.user_data["awaiting_hook_translate"] = False

        hooks = [h.strip() for h in text.split("\n") if h.strip()]

        await update.message.reply_text("⏳ *Hook'lar tarjima qilinmoqda...*", parse_mode="Markdown")

        acc = accounts.active
        translator = ContentTranslator(acc)
        result = await translator.translate_hooks(hooks, target_lang="ru")

        await send_message(update, f"🎣 *HOOK TARJIMA*\n\n{result}", keyboard=back_button())
        return True

    return False
