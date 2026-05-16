"""
Agro AI — 🧠 MEMORY Telegram handler
Xotira tizimi bilan ishlash.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.memory import memory

logger = logging.getLogger("agro_ai.bot.memory")


@register("mem")
@error_handler
async def handle_memory(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🧠 MEMORY handler."""
    await send_typing(update, context)
    acc = accounts.active

    if action == "stats":
        stats = memory.get_stats(acc.id)
        if stats["total"] == 0:
            text = (
                "🧠 *XOTIRA BO'SH*\n\n"
                "Xotira to'ldirilishi uchun:\n"
                "• 📊 TAHLIL o'tkazing\n"
                "• 🎣 HOOKLAR yarating\n"
                "• ✍️ SSENARIY yarating\n\n"
                "Har bir yaratilgan kontent xotiraga saqlanadi."
            )
        else:
            cats = stats["categories"]
            cat_lines = "\n".join(f"  • {k}: {v} ta" for k, v in cats.items())
            sources = stats.get("sources", {})
            src_lines = "\n".join(f"  • {k}: {v} ta" for k, v in sources.items())
            text = (
                f"🧠 *XOTIRA STATISTIKASI*\n\n"
                f"📊 Jami yozuvlar: *{stats['total']}*\n"
                f"⭐ O'rtacha ball: *{stats['avg_score']}*/10\n"
                f"🏆 Eng yuqori: *{stats['top_score']}*/10\n\n"
                f"📋 *Kategoriyalar:*\n{cat_lines}\n\n"
                f"📌 *Manbalar:*\n{src_lines}"
            )
        await send_message(update, text, keyboard=back_button())
        return

    if action == "hooks":
        top_hooks = memory.get_top_hooks(acc.id, limit=10)
        if not top_hooks:
            text = "🎣 *TOP HOOKLAR*\n\n_(Hali hook saqlanmagan. HOOKLAR bo'limidan yarating.)_"
        else:
            lines = ["🎣 *TOP HOOKLAR (xotiradan)*\n"]
            for i, h in enumerate(top_hooks, 1):
                source_tag = f"[{h.source}]" if h.source != "generated" else ""
                lines.append(f"*{i}.* ⭐{h.score:.0f} {source_tag}\n   _{h.content[:80]}_\n")
            text = "\n".join(lines)
        await send_message(update, text, keyboard=back_button())
        return

    if action == "stories":
        top_stories = memory.get_best_story_structures(acc.id, limit=5)
        if not top_stories:
            text = "🎭 *TOP HIKOYALAR*\n\n_(Hali hikoya saqlanmagan. SSENARIY bo'limidan yarating.)_"
        else:
            lines = ["🎭 *TOP HIKOYA TUZILMALARI*\n"]
            for i, s in enumerate(top_stories, 1):
                lines.append(f"*{i}.* ⭐{s.score:.0f}\n   _{s.content[:100]}_\n")
            text = "\n".join(lines)
        await send_message(update, text, keyboard=back_button())
        return

    if action == "patterns":
        best = memory.get_best_patterns(acc.id, "pattern", limit=10)
        if not best:
            text = "📊 *VIRAL PATTERN'LAR*\n\n_(Hali pattern saqlanmagan.)_"
        else:
            lines = ["📊 *ENG YAXSHI PATTERN'LAR*\n"]
            for i, p in enumerate(best, 1):
                tags = " ".join(f"#{t}" for t in p.tags[:3])
                lines.append(f"*{i}.* ⭐{p.score:.0f} {tags}\n   _{p.content[:80]}_\n")
            text = "\n".join(lines)
        await send_message(update, text, keyboard=back_button())
        return

    if action == "failed":
        failed = memory.get_failed_patterns(acc.id, "hook", limit=5)
        if not failed:
            text = "📉 *MUVAFFAQIYATSIZ PATTERN'LAR*\n\n_(Hali ma'lumot yo'q.)_"
        else:
            lines = ["📉 *ISHLAMAGAN PATTERN'LAR (qochish kerak)*\n"]
            for i, f_entry in enumerate(failed, 1):
                lines.append(f"*{i}.* ⚠️ score={f_entry.score:.0f}\n   _{f_entry.content[:80]}_\n")
            text = "\n".join(lines)
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum xotira buyrug'i.", keyboard=back_button())
