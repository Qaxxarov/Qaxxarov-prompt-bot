"""
Agro AI — 📊 MULTI-ACCOUNT Handler
Barcha akkauntlarni bir vaqtda tahlil qilish va parallel kontent yaratish.
"""

import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register

logger = logging.getLogger("agro_ai.bot.multi_account")


def multi_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Barchasini Tahlil Qil", callback_data="multi:analyze_all")],
        [InlineKeyboardButton("📋 Barcha Akkauntlar Uchun Kontent", callback_data="multi:content_all")],
        [InlineKeyboardButton("📈 Umumiy Holat", callback_data="multi:status")],
        [InlineKeyboardButton("🏠 Asosiy Menyu", callback_data="nav:main")],
    ])


@register("multi")
@error_handler
async def handle_multi(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📊 MULTI-ACCOUNT handler."""
    await send_typing(update, context)

    if action == "analyze_all":
        all_accs = accounts.active_accounts
        if len(all_accs) < 2:
            await send_message(update, "ℹ️ Faqat 1 ta akkaunt bor. Kamida 2 ta kerak.", keyboard=multi_menu())
            return

        total = len(all_accs)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                f"📊 *BARCHASI TAHLIL QILINMOQDA*\n\n"
                f"🔄 {total} ta akkaunt ketma-ket tahlil qilinadi...",
                parse_mode="Markdown",
            )

        results = []
        for i, acc in enumerate(all_accs, 1):
            # Progress xabar
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⏳ {i}/{total} *{acc.instagram}* tahlil qilinmoqda...",
                    parse_mode="Markdown",
                )
            except Exception:
                pass

            # Scrape attempt
            result = await _analyze_single_account(acc)
            results.append((acc, result))

        # Umumiy summary
        lines = [f"✅ *TAHLIL TUGADI* ({total} ta akkaunt)\n"]
        for acc, result in results:
            lines.append(f"{'✅' if result['success'] else '❌'} *{acc.instagram}*")
            if result["success"]:
                lines.append(f"   👥 {result.get('followers', '?')} | 👁 {result.get('avg_views', '?')} avg")
            else:
                lines.append(f"   ⚠️ {result.get('error', 'Xato')}")
            lines.append("")

        await send_message(update, "\n".join(lines), keyboard=multi_menu())
        return

    if action == "content_all":
        text = (
            "📋 *BARCHA AKKAUNTLAR UCHUN KONTENT*\n\n"
            "Mavzuni yuboring — har bir akkauntga mos kontent yaratiladi.\n\n"
            "Masalan: `Yoz mavsumi`"
        )
        context.user_data["awaiting_multi_content"] = True
        await send_message(update, text, keyboard=back_button())
        return

    if action == "status":
        all_accs = accounts.all_accounts
        lines = ["📈 *UMUMIY HOLAT*\n"]
        lines.append(f"📋 Jami akkauntlar: {len(all_accs)}")
        lines.append(f"✅ Faol akkaunt: *{accounts.active.instagram}*\n")
        for acc in all_accs:
            active_mark = "🟢" if acc.id == accounts.active.id else "⚪"
            lines.append(f"{active_mark} *{acc.instagram}*")
            lines.append(f"   🎯 {acc.niche[:35]}")
            lines.append(f"   📊 {acc.posting_frequency} post/kun | 🎭 {acc.ai_tone}")
        await send_message(update, "\n".join(lines), keyboard=multi_menu())
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=multi_menu())


async def _analyze_single_account(acc) -> dict:
    """Bitta akkauntni tahlil qilish."""
    try:
        from app.ops.monitor import InstagramMonitor
        monitor = InstagramMonitor(acc.id)
        state = monitor.get_state()
        if state and hasattr(state, "followers") and state.followers > 0:
            return {
                "success": True,
                "followers": state.followers,
                "avg_views": state.avg_views,
                "avg_er": state.avg_er,
            }
        # Scrape attempt (background)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, monitor.scan_now)
        if result:
            return {
                "success": True,
                "followers": getattr(result, "followers", 0),
                "avg_views": getattr(result, "avg_views", 0),
                "avg_er": getattr(result, "avg_er", 0),
            }
        return {"success": False, "error": "Ma'lumot olinmadi"}
    except Exception as e:
        logger.error(f"Analyze error ({acc.instagram}): {e}")
        return {"success": False, "error": str(e)[:50]}


async def handle_multi_content_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Barcha akkauntlar uchun kontent yaratish."""
    if not context.user_data.get("awaiting_multi_content"):
        return False

    topic = update.message.text.strip()
    if len(topic) < 3:
        await update.message.reply_text("❌ Mavzu juda qisqa.")
        return True

    context.user_data["awaiting_multi_content"] = False
    all_accs = accounts.active_accounts

    await update.message.reply_text(
        f"⏳ *{len(all_accs)} ta akkaunt uchun kontent yaratilmoqda...*\n"
        f"Mavzu: {topic}",
        parse_mode="Markdown",
    )

    from app.ai.base import BaseAIEngine

    results = []
    for acc in all_accs:
        engine = BaseAIEngine(acc)
        prompt = (
            f"Mavzu: {topic}\n\n"
            f"Shu mavzuda {acc.instagram} akkauntiga mos Instagram kontent yarat:\n"
            f"- 1 ta hook\n- Qisqa caption (3-4 gap)\n- 5 ta hashtag\n\n"
            f"Niche: {acc.niche}\nAuditoriya: {acc.target_audience}"
        )
        result = await engine.generate(prompt, max_tokens=400)
        results.append((acc, result))

    # Format
    lines = [f"📋 *PARALLEL KONTENT: {topic}*\n"]
    for acc, content in results:
        lines.append(f"━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"🌿 *{acc.instagram}* ({acc.niche[:25]})")
        lines.append(content[:400])
        lines.append("")

    await send_message(update, "\n".join(lines), keyboard=back_button())
    return True
