"""
Agro AI — Bot Middleware
Auth, error handling, logging, typing indicators.
UserManager asosida ishlaydi.
"""

import logging
from functools import wraps
from typing import Callable, List

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from app.settings import ADMIN_IDS

logger = logging.getLogger("agro_ai.bot.middleware")


def _get_user_manager():
    """Lazy import to avoid circular imports."""
    from app.users.manager import user_manager
    return user_manager


def auth_required(func: Callable):
    """Faqat ruxsat berilgan foydalanuvchilar uchun (UserManager orqali)."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        um = _get_user_manager()
        if not um.is_allowed(user_id):
            if update.callback_query:
                await update.callback_query.answer("❌ Ruxsat yo'q", show_alert=True)
            else:
                await update.message.reply_text("❌ Sizga ruxsat berilmagan.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def admin_only(func: Callable):
    """Faqat admin uchun (UserManager orqali)."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        um = _get_user_manager()
        if not um.is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("👑 Faqat admin uchun", show_alert=True)
            else:
                await update.message.reply_text("👑 Bu bo'lim faqat admin uchun.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def manager_required(func: Callable):
    """Manager yoki admin uchun."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        um = _get_user_manager()
        if not um.is_manager_or_above(user_id):
            if update.callback_query:
                await update.callback_query.answer("📋 Manager yoki admin uchun", show_alert=True)
            else:
                await update.message.reply_text("📋 Bu bo'lim manager yoki admin uchun.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Typing indikatori yuborish."""
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)


async def send_message(
    update: Update,
    text: str,
    keyboard=None,
    parse_mode: str = ParseMode.MARKDOWN,
) -> None:
    """Xabar yuborish — callback yoki oddiy message uchun universal."""
    # 4096 belgi limiti
    chunks = _chunk(text)
    for i, chunk in enumerate(chunks):
        kb = keyboard if i == len(chunks) - 1 else None
        if update.callback_query:
            await update.callback_query.message.reply_text(
                chunk, parse_mode=parse_mode, reply_markup=kb
            )
        else:
            await update.message.reply_text(
                chunk, parse_mode=parse_mode, reply_markup=kb
            )


def _chunk(text: str, max_len: int = 4000) -> List[str]:
    """Matnni Telegram limitiga moslashtirish."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def error_handler(func: Callable):
    """Handler xatolarini ushlash va foydalanuvchiga xabar berish."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Handler xatosi ({func.__name__}): {e}")
            err_msg = f"❌ Xato yuz berdi: `{type(e).__name__}`\n\nQayta urinib ko'ring."
            try:
                if update.callback_query:
                    await update.callback_query.message.reply_text(
                        err_msg, parse_mode=ParseMode.MARKDOWN
                    )
                elif update.message:
                    await update.message.reply_text(
                        err_msg, parse_mode=ParseMode.MARKDOWN
                    )
            except Exception:
                pass
    return wrapper
