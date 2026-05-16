"""
Agro AI — 📊 TAHLIL handler
Instagram reels tahlili va scraping.
"""

import asyncio
import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import back_button, confirm_keyboard, tahlil_menu
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions
from app.settings import CHROME_PROFILE_DIR, MAX_REELS, TARGET_PROFILE

logger = logging.getLogger("agro_ai.bot.tahlil")


@register("tahlil")
@error_handler
async def handle_tahlil(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📊 TAHLIL bo'limi callback handler."""
    user_id = update.effective_user.id
    session = sessions.get(user_id)

    if action == "yangi":
        if session.is_scraping:
            await send_message(update, "⏳ Tahlil allaqachon davom etmoqda...")
            return
        await send_message(
            update,
            f"🔄 *Yangi tahlil boshlash*\n\n"
            f"📌 Target: *@{TARGET_PROFILE}*\n"
            f"🎬 Max reels: *{MAX_REELS}*\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n\n"
            f"Davom etasizmi?",
            keyboard=confirm_keyboard("tahlil:confirm", "nav:main"),
        )
        return

    if action == "confirm":
        if session.is_scraping:
            await send_message(update, "⏳ Allaqachon ishlayapti...")
            return
        await send_message(update, "🚀 *Tahlil boshlandi!* Biroz kuting...")
        chat_id = update.effective_chat.id
        asyncio.create_task(_run_scrape(user_id, chat_id, context))
        return

    # Data kerak bo'lgan bo'limlar
    if not session.has_data:
        await send_message(
            update,
            "⚠️ *Ma'lumot topilmadi!*\n\n"
            "Avval tahlil o'tkazing:\n"
            "📊 TAHLIL → 🔄 Yangi Tahlil",
            keyboard=tahlil_menu(),
        )
        return

    await send_typing(update, context)
    stats = session.stats

    if action == "top":
        text = _format_top_reels(stats)
    elif action == "viral":
        text = _format_viral(stats)
    elif action == "aktivlik":
        text = _format_aktivlik(stats, session.reels)
    elif action == "kuchsiz":
        text = _format_kuchsiz(stats)
    elif action == "sirlar":
        text = _format_sirlar(stats)
    else:
        text = "❓ Noma'lum tahlil turi."

    await send_message(update, text, keyboard=back_button())


# ════════════════════════════════════════════════════════
# SCRAPING ENGINE (uses production pipeline)
# ════════════════════════════════════════════════════════

async def _run_scrape(user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Background scraping task — uses ScrapingPipeline with retry/recovery."""
    # Race condition himoyasi — faqat bitta scrape bir vaqtda
    lock = sessions.get_lock(user_id)
    if lock.locked():
        await context.bot.send_message(
            chat_id=chat_id, text="⏳ Tahlil hali davom etmoqda. Kuting...", parse_mode="Markdown"
        )
        return

    async with lock:
        session = sessions.get(user_id)
    session.is_scraping = True

    async def status(msg: str) -> None:
        try:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass

    try:
        await status(
            f"🚀 *Scraping pipeline ishga tushmoqda...*\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n"
            f"🎯 Target: @{TARGET_PROFILE}\n"
            f"🔄 Max 3 ta urinish, auto-recovery"
        )

        loop = asyncio.get_event_loop()

        # Status messages from pipeline (sync → async bridge)
        status_messages = []

        def pipeline_status(msg: str) -> None:
            status_messages.append(msg)

        def do_pipeline():
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            from app.scraper.pipeline import ScrapingPipeline
            pipeline = ScrapingPipeline()
            pipeline.set_status_callback(pipeline_status)
            return pipeline.run()

        result = await loop.run_in_executor(None, do_pipeline)

        # Send collected status messages
        if status_messages:
            combined = "\n".join(f"• {m}" for m in status_messages[-5:])
            await status(f"📋 *Pipeline log:*\n{combined}")

        if not result.success:
            error_msg = result.error or "Noma'lum xato"
            await status(
                f"❌ *Scraping muvaffaqiyatsiz*\n\n"
                f"Urinishlar: {result.attempt_count}\n"
                f"Xato: `{error_msg[:200]}`\n"
                f"Vaqt: {result.duration_sec:.0f}s\n\n"
                "💡 *Yechim:*\n"
                "1. Chrome'ni to'liq yoping\n"
                "2. Task Manager → chrome.exe → End Task\n"
                "3. Qayta urinib ko'ring"
            )
            return

        # Success — save to session
        session.profile = result.profile
        session.reels = result.reels
        session.stats = result.stats
        session.recommendations = result.recommendations
        session.ideas = result.ideas

        # Summary
        p = result.stats["profile"]
        ov = result.stats["overview"]
        eng = result.stats["engagement"]
        await status(
            f"✅ *TAHLIL TAYYOR!*\n\n"
            f"👤 @{p['username']} | 👥 {p['followers']:,}\n"
            f"🎬 {ov['total_reels_analyzed']} reel | ⏱ {result.duration_sec:.0f}s\n"
            f"👁 Jami: {ov['total_views']:,} views\n"
            f"📈 O'rtacha ER: {eng['average_er']}%\n"
            f"🔄 Urinishlar: {result.attempt_count}"
        )

        # Export files
        def do_export():
            from reporter import Reporter
            reporter = Reporter(result.profile, result.reels, result.stats)
            return reporter.save_all(result.recommendations, ideas=result.ideas)

        try:
            saved = await loop.run_in_executor(None, do_export)
            for fmt, path in saved.items():
                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        await context.bot.send_document(
                            chat_id=chat_id, document=f,
                            filename=os.path.basename(path),
                            caption=f"📁 {fmt.upper()} — @{TARGET_PROFILE}",
                        )
        except Exception as e:
            logger.error(f"Export xatosi: {e}")

        await context.bot.send_message(
            chat_id=chat_id, text="📊 Tahlil menyusi:", reply_markup=tahlil_menu()
        )

    except Exception as e:
        logger.exception(f"_run_scrape xatosi: {e}")
        await status(f"❌ *Kutilmagan xato:* `{str(e)[:200]}`")
    finally:
        session.is_scraping = False


# ════════════════════════════════════════════════════════
# FORMATTERS
# ════════════════════════════════════════════════════════

def _format_top_reels(stats: dict) -> str:
    reels = stats["top_reels"].get("by_views", [])
    if not reels:
        return "❌ Ma'lumot topilmadi."
    lines = ["🔥 *ENG KUCHLI REELS*\n"]
    for i, r in enumerate(reels, 1):
        cap = (r.get("caption") or "—")[:50]
        lines.append(
            f"*{i}.* 👁 {r['views']:,} | ❤️ {r['likes']:,} | 📈 {r['engagement_rate']}%\n"
            f"   _{cap}_\n"
        )
    return "\n".join(lines)


def _format_viral(stats: dict) -> str:
    v = stats["views"]
    eng = stats["engagement"]
    tiers = stats["performance_tiers"]
    viral_count = tiers.get("viral", {}).get("count", 0)
    return (
        f"📈 *VIRAL TAHLIL*\n\n"
        f"🚀 Viral reels: *{viral_count}* ta\n"
        f"📊 O'rtacha views: *{v['average']:,}*\n"
        f"🔝 Eng yuqori: *{v['max']:,}*\n"
        f"💡 O'rtacha ER: *{eng['average_er']}%*\n"
        f"📊 Baho: {eng['er_benchmark']}\n\n"
        f"🧠 *Viral formula:*\n"
        f"• Kuchli hook (birinchi 3 soniya)\n"
        f"• Emotsional trigger\n"
        f"• Surprise reveal yoki amaliy qiymat\n"
        f"• CTA (savol yoki chaqiriq)"
    )


def _format_aktivlik(stats: dict, reels: list) -> str:
    import re
    from collections import Counter
    hours = Counter()
    for r in reels:
        if hasattr(r, "posted_at") and r.posted_at:
            m = re.search(r"T(\d{2}):", r.posted_at)
            if m:
                hours[int(m.group(1))] += 1
    if hours:
        peak = hours.most_common(1)[0][0]
        dist = "\n".join(f"   {h:02d}:00 — {c} ta" for h, c in sorted(hours.items()))
    else:
        peak = 19
        dist = "   (Vaqt ma'lumoti mavjud emas)"
    return (
        f"👀 *AKTIVLIK TAHLILI*\n\n"
        f"⏰ *Post vaqtlari:*\n{dist}\n\n"
        f"🏆 *Eng faol vaqt:* {peak:02d}:00\n\n"
        f"💡 Birinchi 30 daqiqadagi engagement muhim."
    )


def _format_kuchsiz(stats: dict) -> str:
    reels = stats["top_reels"].get("worst_by_views", [])
    if not reels:
        return "❌ Ma'lumot topilmadi."
    lines = ["📉 *KUCHSIZ KONTENT*\n"]
    for i, r in enumerate(reels, 1):
        lines.append(f"*{i}.* 👁 {r['views']:,} | 📈 {r['engagement_rate']}%\n")
    lines.append("\n💡 Hook va thumbnail'larni yaxshilang.")
    return "\n".join(lines)


def _format_sirlar(stats: dict) -> str:
    v = stats["views"]
    tiers = stats["performance_tiers"]
    viral_count = tiers.get("viral", {}).get("count", 0)
    total = stats["overview"]["total_reels_analyzed"]
    return (
        f"🧠 *VIRAL SIRLAR*\n\n"
        f"📊 Viral: {viral_count}/{total} ta reel\n"
        f"📈 O'rtacha: {v['average']:,} views\n\n"
        f"🔑 *5 ta sir:*\n\n"
        f"*1.* 🎣 Hook — birinchi 3 soniya hamma narsa\n"
        f"*2.* 😱 Emotsiya — qo'rquv, hayrat, umid\n"
        f"*3.* 🤔 Curiosity — savol ber, javobni oxirida\n"
        f"*4.* ✅ Natija — before/after, raqamlar\n"
        f"*5.* 📅 Izchillik — haftada 4-5 ta reel"
    )
