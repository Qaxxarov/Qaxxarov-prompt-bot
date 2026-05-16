"""
Agro AI — AI-powered handlers:
📅 REJA, 📡 TRENDLAR, 📦 SOTUV AI, 🧠 AUDIENCE AI,
🏆 VIRAL SCORE, 📈 O'SISH, 🎯 KONKURENT

Uses real AI engines: AudienceEngine, ViralScoreEngine.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.accounts import accounts
from app.ai.audience import AudienceEngine
from app.ai.base import BaseAIEngine
from app.ai.viral_score import ViralScoreEngine
from app.bot.keyboards import back_button
from app.bot.middleware import error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions

logger = logging.getLogger("agro_ai.bot.ai_sections")


# ════════════════════════════════════════════════════════
# 📅 REJA
# ════════════════════════════════════════════════════════

@register("reja")
@error_handler
async def handle_reja(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    await send_typing(update, context)
    engine = BaseAIEngine(accounts.active)
    session = sessions.get(update.effective_user.id)
    ctx = engine.build_context(session.stats) if session.has_data else None

    tasks = {
        "7kun": "7 kunlik kontent reja tuz. Har kun: mavzu, format, hook, vaqt. Jadvalli.",
        "30kun": (
            "30 kunlik kontent strategiya tuz. 4 hafta:\n"
            "1-hafta: Ishonch | 2-hafta: Qiymat | 3-hafta: Viral | 4-hafta: Sotuv"
        ),
        "vaqt": (
            "Instagram uchun eng yaxshi post vaqtlarini tavsiya qil.\n"
            "O'zbekiston vaqti (UTC+5). Hafta kunlari bo'yicha. Fermer auditoriyasi uchun."
        ),
        "strategiya": (
            "30 kunlik viral strategiya tuz:\n"
            "- Kontent mix (% ta'lim, sotuv, entertainment, trend)\n"
            "- Hashtag strategiyasi\n- Engagement taktikalari\n- O'sish maqsadlari"
        ),
    }

    task = tasks.get(action, "Kontent reja tuz.")
    titles = {"7kun": "📆 7 KUNLIK REJA", "30kun": "📆 30 KUNLIK REJA",
              "vaqt": "⏰ ENG YAXSHI VAQT", "strategiya": "🧠 VIRAL STRATEGIYA"}

    result = await engine.generate(task, context=ctx, max_tokens=1200)
    await send_message(update, f"📅 *{titles.get(action, 'REJA')}*\n\n{result}", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 📡 TRENDLAR
# ════════════════════════════════════════════════════════

@register("trend")
@error_handler
async def handle_trendlar(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    await send_typing(update, context)
    engine = BaseAIEngine(accounts.active)

    tasks = {
        "mavzu": "Qishloq xo'jaligi bo'yicha 10 ta trending mavzu. Har biri qisqa tavsif bilan.",
        "audio": "Instagram Reels uchun trending audio strategiyasi. Qanday topish, qaysi janrlar mos.",
        "format": "2025 yilning 8 ta eng trending reel formati. Har biri: nomi, tavsifi, agro uchun misol.",
        "hook": "15 ta viral hook formula. Kategoriyalar: qo'rquv, hayrat, qiziqish, foyda.",
        "predict": "Keyingi 30 kunda qishloq xo'jaligi kontentida qaysi trendlar paydo bo'ladi? Bashorat qil.",
    }

    task = tasks.get(action, "Trend tahlil qil.")
    titles = {"mavzu": "📈 TREND MAVZULAR", "audio": "🎵 TREND AUDIO",
              "format": "🎬 TREND FORMATLAR", "hook": "⚡ VIRAL HOOKLAR", "predict": "🔮 TREND BASHORAT"}

    result = await engine.generate(task, max_tokens=800)
    await send_message(update, f"📡 *{titles.get(action, 'TRENDLAR')}*\n\n{result}", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 📦 SOTUV AI
# ════════════════════════════════════════════════════════

@register("sotuv")
@error_handler
async def handle_sotuv(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    await send_typing(update, context)
    engine = BaseAIEngine(accounts.active)
    session = sessions.get(update.effective_user.id)
    ctx = engine.build_context(session.stats) if session.has_data else None

    tasks = {
        "urug": "Urug' mahsulotlari uchun 5 ta sotuv g'oyasi. Har biri: mahsulot, auditoriya, xabar, kanal.",
        "strategiya": "Instagram orqali sotuv strategiyasi. Funnel: Awareness → Interest → Desire → Action.",
        "reklama": "3 ta reklama kontent g'oyasi. Format, hook, xabar, CTA. Fermerlar uchun.",
        "marketing": "Agro marketing strategiyasi: mavsum, narx, hamkorlik, referral, community.",
        "funnel": "Instagram sales funnel tuz. 5 bosqich, har biri uchun kontent turi va CTA.",
    }

    task = tasks.get(action, "Sotuv strategiyasi tuz.")
    titles = {"urug": "🌱 URUG' SOTUV", "strategiya": "💰 SOTUV STRATEGIYA",
              "reklama": "🎯 REKLAMA", "marketing": "📢 AGRO MARKETING", "funnel": "🔄 SALES FUNNEL"}

    result = await engine.generate(task, context=ctx, max_tokens=800)
    await send_message(update, f"📦 *{titles.get(action, 'SOTUV AI')}*\n\n{result}", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 🧠 AUDIENCE AI — AudienceEngine
# ════════════════════════════════════════════════════════

@register("aud")
@error_handler
async def handle_audience(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🧠 AUDIENCE AI — AudienceEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = AudienceEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    titles = {"profil": "👥 AUDITORIYA PROFILI", "psych": "🧠 PSIXOLOGIK TAHLIL",
              "comments": "💬 COMMENT TAHLIL", "pattern": "📊 ENGAGEMENT PATTERN"}

    if action not in titles:
        await send_message(update, "❓ Noma'lum tahlil turi.", keyboard=back_button())
        return

    # Loading
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *{titles[action]}* tayyorlanmoqda...",
            parse_mode="Markdown",
        )

    # Route to AudienceEngine methods
    if action == "profil":
        result = await engine.analyze_audience(stats=stats)
    elif action == "psych":
        result = await engine.get_emotional_triggers(stats=stats)
    elif action == "comments":
        ctx = engine.build_context(stats)
        result = await engine.generate(
            "Comment tahlil strategiyasi:\n"
            "1. Eng ko'p beriladigan savollar (10 ta)\n"
            "2. Har biriga ideal javob namunasi\n"
            "3. Comment'larni engagement'ga aylantirish usullari\n"
            "4. Salbiy comment'larga javob strategiyasi",
            context=ctx, max_tokens=900,
        )
    elif action == "pattern":
        result = await engine.suggest_engagement_tactics(stats=stats)
    else:
        result = "❓ Noma'lum."

    text = f"🧠 *{titles[action]}*\n\n{result}"
    await send_message(update, text, keyboard=back_button())


# ════════════════════════════════════════════════════════
# 🏆 VIRAL SCORE — ViralScoreEngine
# ════════════════════════════════════════════════════════

@register("vscore")
@error_handler
async def handle_viral_score(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """🏆 VIRAL SCORE — ViralScoreEngine bilan ishlaydi."""
    await send_typing(update, context)
    acc = accounts.active
    engine = ViralScoreEngine(acc)
    session = sessions.get(update.effective_user.id)
    stats = session.stats if session.has_data else None

    titles = {"current": "📊 JORIY SCORE", "predict": "🔮 BASHORAT",
              "retention": "📈 RETENTION", "top": "🏅 TOP PERFORMERS"}

    if action not in titles:
        await send_message(update, "❓ Noma'lum score turi.", keyboard=back_button())
        return

    # Loading
    if update.callback_query:
        await update.callback_query.message.reply_text(
            f"⏳ *{titles[action]}* hisoblanmoqda...",
            parse_mode="Markdown",
        )

    if action == "current":
        if session.has_data:
            # Real score hisoblash (sinxron — AI kerak emas)
            score_data = engine.compute_score(stats)
            text = engine.format_score_message(score_data)
        else:
            text = (
                "⚠️ *Score hisoblash uchun ma'lumot kerak*\n\n"
                "Avval tahlil o'tkazing:\n"
                "📊 TAHLIL → 🔄 Yangi Tahlil\n\n"
                "Score tarkibi:\n"
                "• 💡 Engagement Rate (25 ball)\n"
                "• 🚀 Viral Ratio (20 ball)\n"
                "• 📊 View Consistency (15 ball)\n"
                "• 📈 Growth Trend (15 ball)\n"
                "• 📝 Content Quality (15 ball)\n"
                "• 📅 Posting Frequency (10 ball)"
            )
        await send_message(update, text, keyboard=back_button())
        return

    if action == "predict":
        result = await engine.predict_viral_potential(
            hook="Qishloq xo'jaligi kontenti",
            stats=stats,
        )
        text = f"🔮 *VIRAL BASHORAT*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "retention":
        # Use HookEngine for retention hooks
        from app.ai.hooks import HookEngine
        hook_engine = HookEngine(acc)
        result = await hook_engine.generate_retention_hooks(stats=stats)
        text = f"📈 *RETENTION OSHIRISH*\n\n{result}"
        await send_message(update, text, keyboard=back_button())
        return

    if action == "top":
        if session.has_data:
            tiers = stats["performance_tiers"]
            viral_reels = tiers.get("viral", {}).get("reels", [])
            if viral_reels:
                lines = ["🏅 *TOP PERFORMERS*\n"]
                for i, r in enumerate(viral_reels[:5], 1):
                    lines.append(f"*{i}.* 👁 {r['views']:,} | 📈 ER: {r['er']}%\n   🔗 {r['url']}\n")
                text = "\n".join(lines)
            else:
                text = "⚠️ Viral reels topilmadi. Ko'proq reel tahlil qiling."
        else:
            text = "⚠️ Avval tahlil o'tkazing."
        await send_message(update, text, keyboard=back_button())
        return


# ════════════════════════════════════════════════════════
# 📈 O'SISH
# ════════════════════════════════════════════════════════

@register("osish")
@error_handler
async def handle_osish(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    await send_typing(update, context)
    engine = BaseAIEngine(accounts.active)
    session = sessions.get(update.effective_user.id)
    ctx = engine.build_context(session.stats) if session.has_data else None

    tasks = {
        "stats": "O'sish statistikasini tahlil qil. Followers, reach, engagement trendlari.",
        "goals": "30 kunlik o'sish maqsadlari belgilab ber. Realistik va o'lchanadigan.",
        "tips": "10 ta amaliy o'sish tavsiyasi. Hoziroq qo'llash mumkin bo'lgan.",
        "weekly": "Haftalik o'sish hisoboti shabloni yarat. Qaysi metrikalarni kuzatish kerak?",
    }

    task = tasks.get(action, "O'sish tahlili.")
    titles = {"stats": "📊 O'SISH STATISTIKA", "goals": "🎯 MAQSADLAR",
              "tips": "💡 O'SISH TAVSIYALAR", "weekly": "📅 HAFTALIK HISOBOT"}

    result = await engine.generate(task, context=ctx)
    title = titles.get(action, "O'SISH")
    await send_message(update, f"📈 *{title}*\n\n{result}", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 🎯 KONKURENT
# ════════════════════════════════════════════════════════

@register("konk")
@error_handler
async def handle_konkurent(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    await send_typing(update, context)
    engine = BaseAIEngine(accounts.active)

    tasks = {
        "analyze": (
            "Qishloq xo'jaligi niche'ida Instagram konkurentlarni tahlil qilish strategiyasi.\n"
            "Nimaga e'tibor berish kerak? Qanday ma'lumot yig'ish?"
        ),
        "compare": "Konkurent bilan solishtirish shabloni yarat. Qaysi metrikalar muhim?",
        "learn": "Muvaffaqiyatli agro-akkauntlardan nimani o'rganish mumkin? 7 ta dars.",
        "advantage": "Konkurentlardan ustunlik topish strategiyasi. Niche differentiation.",
    }

    task = tasks.get(action, "Konkurent tahlili.")
    titles = {"analyze": "🔍 KONKURENT TAHLIL", "compare": "📊 SOLISHTIRISH",
              "learn": "💡 O'RGANISH", "advantage": "🎯 USTUNLIK"}

    result = await engine.generate(task, max_tokens=800)
    await send_message(update, f"🎯 *{titles.get(action, 'KONKURENT')}*\n\n{result}", keyboard=back_button())
