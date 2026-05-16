"""
Agro AI — 📮 POST SCHEDULER Telegram handler
Post navbati boshqaruvi.
"""

import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.posting.scheduler import post_scheduler

logger = logging.getLogger("agro_ai.bot.post")


def post_menu() -> InlineKeyboardMarkup:
    """Post scheduler menyusi."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Navbatga Qo'shish", callback_data="post:add")],
        [InlineKeyboardButton("📋 Navbatni Ko'rish", callback_data="post:queue")],
        [InlineKeyboardButton("📅 Bugun", callback_data="post:today")],
        [InlineKeyboardButton("📮 Hozir Post Qil", callback_data="post:now")],
        [InlineKeyboardButton("📜 Tarix", callback_data="post:history")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("post")
@error_handler
async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📮 POST SCHEDULER handler."""
    await send_typing(update, context)
    acc = accounts.active

    if action == "add":
        text = (
            "➕ *NAVBATGA QO'SHISH*\n\n"
            "Quyidagi formatda yuboring:\n\n"
            "`vaqt | caption | hashtag1,hashtag2`\n\n"
            "Masalan:\n"
            "`2025-06-15T19:00 | Pomidor parvarishi haqida 5 sir! 🍅 | pomidor,agro,hosil`\n\n"
            "Yoki faqat caption yuboring — vaqt bugun 19:00 bo'ladi."
        )
        context.user_data["awaiting_post_add"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "queue":
        queue_text = post_scheduler.format_queue()
        text = f"📋 *POST NAVBATI*\n\n{queue_text}"

        pending = post_scheduler.get_pending()
        if pending:
            buttons = []
            for p in pending[:5]:
                buttons.append([InlineKeyboardButton(
                    f"❌ Bekor: {p.caption[:20]}...",
                    callback_data=f"post:cancel_{p.id}",
                )])
            buttons.append([InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")])
            kb = InlineKeyboardMarkup(buttons)
            await send_message(update, text, keyboard=kb)
        else:
            await send_message(update, text, keyboard=post_menu())
        return

    if action == "today":
        today_text = post_scheduler.format_today()
        text = f"📅 *BUGUNGI POSTLAR*\n\n{today_text}"
        await send_message(update, text, keyboard=post_menu())
        return

    if action == "now":
        # Eng yaqin pending postni publish qilish (reminder)
        due = post_scheduler.get_due_posts()
        if not due:
            pending = post_scheduler.get_pending()
            if pending:
                due = [pending[0]]
            else:
                await send_message(update, "_(Navbatda post yo'q.)_", keyboard=post_menu())
                return

        post = due[0]
        from app.posting.publisher import InstagramPublisher
        publisher = InstagramPublisher()
        result = publisher._prepare_reminder(post.caption, post.media_path, post.hashtags)

        # Post qilinganini belgilash tugmasi
        buttons = [
            [InlineKeyboardButton("✅ Post qildim!", callback_data=f"post:done_{post.id}")],
            [InlineKeyboardButton("❌ Keyinroq", callback_data="post:queue")],
        ]
        kb = InlineKeyboardMarkup(buttons)
        await send_message(update, result["message"], keyboard=kb)
        return

    if action == "history":
        history = post_scheduler.get_history(10)
        if history:
            lines = ["📜 *POST TARIXI*\n"]
            for p in history:
                status_emoji = "✅" if p.status == "published" else "❌"
                dt = datetime.fromtimestamp(p.published_at) if p.published_at else None
                time_str = dt.strftime("%d.%m %H:%M") if dt else "?"
                lines.append(f"{status_emoji} [{time_str}] {p.caption[:40]}...")
            text = "\n".join(lines)
        else:
            text = "📜 *TARIX*\n\n_(Hali post tarixi yo'q.)_"
        await send_message(update, text, keyboard=post_menu())
        return

    # Cancel post
    if action.startswith("cancel_"):
        post_id = action[7:]
        if post_scheduler.cancel_post(post_id):
            await send_message(update, "✅ Post bekor qilindi.", keyboard=post_menu())
        else:
            await send_message(update, "❌ Post topilmadi yoki allaqachon publish qilingan.", keyboard=post_menu())
        return

    # Mark as done
    if action.startswith("done_"):
        post_id = action[5:]
        if post_scheduler.mark_published(post_id):
            await send_message(update, "✅ Ajoyib! Post muvaffaqiyatli qilindi! 🎉", keyboard=post_menu())
        else:
            await send_message(update, "❌ Post topilmadi.", keyboard=post_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=post_menu())


async def handle_post_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Post qo'shish uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    if not context.user_data.get("awaiting_post_add"):
        return False

    text = update.message.text.strip()
    acc = accounts.active

    # Parse: vaqt | caption | hashtags
    parts = [p.strip() for p in text.split("|")]

    if len(parts) >= 2:
        scheduled_time = parts[0]
        caption = parts[1]
        hashtags = [h.strip().lstrip("#") for h in parts[2].split(",")] if len(parts) > 2 else []
    else:
        # Faqat caption — bugun 19:00
        caption = text
        scheduled_time = datetime.now().strftime("%Y-%m-%dT19:00:00")
        hashtags = []

    # Validate time format
    try:
        if "T" not in scheduled_time:
            scheduled_time = scheduled_time + "T19:00:00"
        datetime.fromisoformat(scheduled_time)
    except ValueError:
        scheduled_time = datetime.now().strftime("%Y-%m-%dT19:00:00")

    context.user_data["awaiting_post_add"] = False

    post = post_scheduler.add_to_queue(
        caption=caption,
        scheduled_time=scheduled_time,
        account_id=acc.id,
        hashtags=hashtags,
    )

    dt = post.scheduled_datetime
    time_str = dt.strftime("%d.%m.%Y %H:%M") if dt else "?"

    await update.message.reply_text(
        f"✅ *Post navbatga qo'shildi!*\n\n"
        f"⏰ Vaqt: {time_str}\n"
        f"📝 Caption: {caption[:50]}...\n"
        f"🆔 ID: `{post.id}`",
        parse_mode="Markdown",
    )
    return True
