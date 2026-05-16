"""
Agro AI — /start, /help, /status, /reset handlers
"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.bot.keyboards import main_menu
from app.bot.middleware import auth_required, error_handler
from app.bot.session import sessions
from app.settings import AI_ENABLED, CHROME_PROFILE_DIR, OPENAI_MODEL

logger = logging.getLogger("agro_ai.bot.start")


@auth_required
@error_handler
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name or "Foydalanuvchi"
    acc = accounts.active
    text = (
        f"🌿 *Assalomu alaykum, {name}!*\n\n"
        f"Men *{acc.instagram}* uchun AI Instagram strategistiman.\n\n"
        "📊 Reels tahlili va viral analitika\n"
        "💡 AI kontent g'oyalari\n"
        "🎣 Viral hook yaratish\n"
        "✍️ Ssenariy va kadrlar rejasi\n"
        "🎞 Veo video promptlar\n"
        "📅 Kontent reja va strategiya\n"
        "📡 Trend radar va bashorat\n"
        "🧠 Auditoriya psixologiyasi\n"
        "🏆 Viral score tahlili\n"
        "📦 Sotuv AI va marketing\n"
        "📤 Excel/JSON/PDF eksport\n\n"
        "Menyudan tanlang 👇"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu())


@auth_required
@error_handler
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 *YORDAM — Agro AI v2.0*\n\n"
        "*Buyruqlar:*\n"
        "/start — Botni ishga tushirish\n"
        "/help — Yordam\n"
        "/status — Tizim holati\n"
        "/reset — Sessiyani tozalash\n"
        "/profil — Chrome diagnostika\n\n"
        "*Menyu bo'limlari (15 ta):*\n"
        "📊 TAHLIL — Instagram reels tahlili\n"
        "💡 G'OYALAR — Viral kontent g'oyalari\n"
        "🎣 HOOKLAR — Viral hook yaratish\n"
        "✍️ SSENARIY — Reel ssenariy va kadrlar\n"
        "🎞 VEO — Video prompt yaratish\n"
        "📅 REJA — Kontent reja va strategiya\n"
        "📡 TRENDLAR — Trend radar\n"
        "📦 SOTUV AI — Sotuv strategiyasi\n"
        "🧠 AUDIENCE — Auditoriya tahlili\n"
        "🏆 VIRAL SCORE — Viral ball tahlili\n"
        "📈 O'SISH — O'sish analizi\n"
        "🎯 KONKURENT — Raqobatchi tahlili\n"
        "📤 EXPORT — Fayllarni yuklab olish\n"
        "⚙️ SOZLAMALAR — Akkaunt va tizim\n"
        "👑 ADMIN — Admin panel"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu())


@auth_required
@error_handler
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = sessions.get(update.effective_user.id)
    acc = accounts.active
    ai_status = f"✅ {OPENAI_MODEL}" if AI_ENABLED else "❌ off"

    if session.has_data:
        p = session.stats["profile"]
        text = (
            f"✅ *Tizim Holati*\n\n"
            f"🌿 Akkaunt: *{acc.instagram}*\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n"
            f"🤖 AI: {ai_status}\n\n"
            f"📊 *Sessiya:*\n"
            f"👤 Tahlil: @{p['username']}\n"
            f"🎬 Reels: {len(session.reels)} ta\n"
            f"💡 G'oyalar: {len(session.ideas)} ta\n"
            f"👁 Views: {session.stats['overview']['total_views']:,}"
        )
    else:
        text = (
            f"⚙️ *Tizim Holati*\n\n"
            f"🌿 Akkaunt: *{acc.instagram}*\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n"
            f"🤖 AI: {ai_status}\n\n"
            f"📊 Sessiya: _(ma'lumot yo'q)_\n"
            f"📊 TAHLIL bo'limidan yangi tahlil boshlang."
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu())


@auth_required
@error_handler
async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sessions.reset(update.effective_user.id)
    await update.message.reply_text("🔄 Sessiya tozalandi.", reply_markup=main_menu())


@auth_required
@error_handler
async def cmd_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open Telegram Mini App dashboard."""
    from app.settings import WEBAPP_URL
    if not WEBAPP_URL:
        await update.message.reply_text(
            "⚠️ *Mini App sozlanmagan*\n\n"
            "`.env` faylida `WEBAPP_URL` ni o'rnating.\n"
            "Masalan: `WEBAPP_URL=https://your-domain.com`\n\n"
            "Lokal test uchun ngrok ishlating:\n"
            "`ngrok http 8000`",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
        return

    from app.bot.keyboards import webapp_keyboard
    await update.message.reply_text(
        "🌐 *Agro AI Dashboard*\n\n"
        "Quyidagi tugmani bosib Mini App'ni oching.\n"
        "Dashboard Telegram ichida ishlaydi!",
        parse_mode="Markdown",
        reply_markup=webapp_keyboard(WEBAPP_URL),
    )
