"""
Agro AI — 🕵️ KONKURENT AI Telegram handler
Raqobatchi tahlili va intelligence.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions
from app.competitors.engine import CompetitorEngine
from app.competitors.models import competitor_db

logger = logging.getLogger("agro_ai.bot.competitor")


@register("konk")
@error_handler
async def handle_konkurent(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🕵️ KONKURENT AI handler."""
    await send_typing(update, context)
    acc = accounts.active
    engine = CompetitorEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    if action == "analyze":
        # Loading
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Konkurent tahlili* tayyorlanmoqda...",
                parse_mode="Markdown",
            )

        # Bazadagi raqobatchilar
        competitors = competitor_db.get_all(acc.id)
        if competitors:
            comp_names = ", ".join(f"@{c.username}" for c in competitors[:3])
            result = await engine.analyze_competitor(
                username=competitors[0].username, stats=stats
            )
            text = f"🕵️ *KONKURENT TAHLILI*\n\n📌 Bazada: {comp_names}\n\n{result}"
        else:
            result = await engine.generate(
                "Qishloq xo'jaligi niche'ida Instagram konkurentlarni tahlil qilish strategiyasi.\n"
                "1. Qanday konkurent topish\n"
                "2. Nimaga e'tibor berish\n"
                "3. Qanday ma'lumot yig'ish\n"
                "4. Qanday tahlil qilish\n"
                "5. Qanday foydalanish",
                max_tokens=800,
            )
            text = f"🕵️ *KONKURENT TAHLILI*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "compare":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Solishtirish* tayyorlanmoqda...",
                parse_mode="Markdown",
            )

        competitors = competitor_db.get_all(acc.id)
        if competitors and len(competitors) >= 2:
            usernames = [c.username for c in competitors[:3]]
            result = await engine.compare_competitors(usernames, stats=stats)
        else:
            result = await engine.generate(
                "Konkurent solishtirish shabloni yarat.\n"
                "Qaysi metrikalar muhim? Qanday jadval tuzish kerak?\n"
                "Agro niche uchun moslashtirilgan.",
                max_tokens=800,
            )
        text = f"📊 *KONKURENT SOLISHTIRISH*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "learn":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Insight'lar* tayyorlanmoqda...",
                parse_mode="Markdown",
            )

        result = await engine.generate_insights(stats=stats)
        text = f"💡 *KONKURENTLARDAN O'RGANISH*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "advantage":
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "⏳ *Ustunlik tahlili* tayyorlanmoqda...",
                parse_mode="Markdown",
            )

        result = await engine.generate(
            "Bizning akkaunt uchun konkurentlardan ustunlik topish:\n\n"
            "1. NICHE DIFFERENTIATION — qayerda boshqacha bo'lishimiz mumkin?\n"
            "2. CONTENT GAP — konkurentlar qilmayotgan nima bor?\n"
            "3. AUDIENCE GAP — kim xizmat ko'rmayapti?\n"
            "4. FORMAT GAP — qaysi format ishlatilmayapti?\n"
            "5. VOICE GAP — qanday ohang yo'q?\n\n"
            "Har biri uchun aniq amaliy tavsiya.",
            context=engine.build_context(stats),
            max_tokens=900,
        )
        text = f"🎯 *USTUNLIK TOPISH*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "hooks":
        # Raqobatchilarning top hooklari
        all_hooks = competitor_db.get_all_hooks(acc.id)
        if all_hooks:
            lines = ["🎣 *KONKURENT HOOKLARI*\n"]
            for i, h in enumerate(all_hooks[:15], 1):
                lines.append(f"*{i}.* _{h[:80]}_")
            text = "\n".join(lines)
        else:
            text = (
                "🎣 *KONKURENT HOOKLARI*\n\n"
                "_(Hali konkurent hooklari saqlanmagan.\n"
                "Konkurent reellarini tahlil qilgandan keyin bu yerda ko'rinadi.)_"
            )
        await send_message(update, text, keyboard=back_button())
        return

    if action == "patterns":
        all_patterns = competitor_db.get_all_patterns(acc.id)
        if all_patterns:
            lines = ["📊 *KONKURENT VIRAL PATTERN'LARI*\n"]
            for i, p in enumerate(all_patterns[:10], 1):
                lines.append(f"*{i}.* {p}")
            text = "\n".join(lines)
        else:
            text = "📊 *VIRAL PATTERN'LAR*\n\n_(Hali ma'lumot yo'q.)_"
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum konkurent buyrug'i.", keyboard=back_button())
