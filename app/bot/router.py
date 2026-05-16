"""
Agro AI — Callback Router
Markaziy callback dispatcher.
Callback format: "section:action" (masalan "tahlil:viral", "hook:fear")
"""

import logging
from typing import Callable, Dict, Tuple

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import main_menu
from app.bot.middleware import auth_required, error_handler, send_message

logger = logging.getLogger("agro_ai.bot.router")

# Handler registry: {"section": handler_function}
_handlers: Dict[str, Callable] = {}


def register(section: str):
    """Handler modulni ro'yxatga olish dekoratori."""
    def decorator(func: Callable):
        _handlers[section] = func
        return func
    return decorator


@auth_required
@error_handler
async def route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Barcha inline callback'larni tegishli handler'ga yo'naltirish.
    Format: "section:action"
    """
    query = update.callback_query
    await query.answer()
    data = query.data

    # Navigation
    if data == "nav:main":
        await query.message.reply_text(
            "🏠 *Asosiy menyu*\n\nBo'limni tanlang:",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
        return

    # Parse section:action
    if ":" not in data:
        logger.warning(f"Noto'g'ri callback format: {data}")
        await send_message(update, "❓ Noma'lum buyruq.")
        return

    section, action = data.split(":", 1)

    # Find handler
    handler = _handlers.get(section)
    if handler:
        await handler(update, context, action)
    else:
        logger.warning(f"Handler topilmadi: section={section}, action={action}")
        await send_message(update, f"⚠️ `{section}` bo'limi hali tayyor emas.")


def get_registered_sections() -> list:
    """Ro'yxatga olingan bo'limlar."""
    return list(_handlers.keys())
