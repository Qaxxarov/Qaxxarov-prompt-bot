"""
Agro AI — 💬 DM AUTO-REPLY Telegram handler
FAQ bazasi boshqaruvi va test.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.dm.auto_reply import dm_auto_reply

logger = logging.getLogger("agro_ai.bot.dm")


@register("dm")
@error_handler
async def handle_dm(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """💬 DM AUTO-REPLY handler."""
    await send_typing(update, context)

    if action == "list":
        text = f"📋 *FAQ RO'YXATI*\n\n{dm_auto_reply.format_list()}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "add":
        text = (
            "➕ *FAQ QO'SHISH*\n\n"
            "Quyidagi formatda yuboring:\n\n"
            "`keywords | javob | kategoriya`\n\n"
            "Masalan:\n"
            "`narx,qancha,price | Narxlar: pomidor 25000, bodring 30000 | pricing`\n\n"
            "Keywords vergul bilan ajratiladi."
        )
        context.user_data["awaiting_faq_add"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "test":
        text = (
            "🧪 *FAQ TEST*\n\n"
            "Xabar yuboring — bot qanday javob berishini ko'ring.\n"
            "(FAQ matching + AI fallback)"
        )
        context.user_data["awaiting_faq_test"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "stats":
        faqs = dm_auto_reply.get_all()
        total = len(faqs)
        total_uses = sum(f.use_count for f in faqs)
        top = sorted(faqs, key=lambda f: f.use_count, reverse=True)[:3]

        lines = [
            f"📊 *DM STATISTIKA*\n",
            f"📋 Jami FAQ: {total}",
            f"📨 Jami ishlatilgan: {total_uses} marta\n",
            f"🏆 *Top FAQ:*",
        ]
        for i, f in enumerate(top, 1):
            lines.append(f"  {i}. [{f.category}] — {f.use_count} marta")

        text = "\n".join(lines)
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=back_button())


async def handle_dm_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    DM handler uchun matn qabul qilish.
    Returns True if handled, False otherwise.
    """
    # FAQ qo'shish
    if context.user_data.get("awaiting_faq_add"):
        text = update.message.text.strip()
        parts = [p.strip() for p in text.split("|")]

        if len(parts) < 2:
            await update.message.reply_text(
                "❌ Format: `keywords | javob | kategoriya`",
                parse_mode="Markdown",
            )
            return True

        keywords = [k.strip() for k in parts[0].split(",")]
        response = parts[1]
        category = parts[2] if len(parts) > 2 else "general"

        context.user_data["awaiting_faq_add"] = False

        faq = dm_auto_reply.add_faq(keywords, response, category)
        await update.message.reply_text(
            f"✅ FAQ qo'shildi!\n\n"
            f"🔑 Keywords: {', '.join(keywords)}\n"
            f"📂 Kategoriya: {category}",
            parse_mode="Markdown",
        )
        return True

    # FAQ test
    if context.user_data.get("awaiting_faq_test"):
        text = update.message.text.strip()
        context.user_data["awaiting_faq_test"] = False

        # FAQ matching
        faq = dm_auto_reply.find_response(text)
        if faq:
            result = (
                f"✅ *FAQ TOPILDI*\n\n"
                f"📂 Kategoriya: {faq.category}\n"
                f"🔑 Keywords: {', '.join(faq.keywords[:3])}\n\n"
                f"📨 *Javob:*\n{faq.response}"
            )
        else:
            # AI fallback
            ai_response = await dm_auto_reply.get_ai_response(text)
            result = (
                f"🤖 *AI FALLBACK*\n"
                f"_(FAQ'da javob topilmadi — AI javob yaratdi)_\n\n"
                f"📨 *Javob:*\n{ai_response}"
            )

        await send_message(update, result, keyboard=back_button())
        return True

    return False
