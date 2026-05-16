"""
Agro AI v2.0 — Telegram Bot Entry Point (Modular)
Yangi handler tizimi bilan ishlaydi.
"""

import logging
import os
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Loyiha ildizini path'ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.bot.keyboards import (
    admin_menu, audience_menu, export_menu, goyalar_menu, hooklar_menu,
    konkurent_menu, main_menu, memory_menu, ops_menu, osish_menu,
    pipeline_menu, reja_menu, sotuv_menu, sozlamalar_menu, ssenariy_menu,
    tahlil_menu, trendlar_menu, veo_menu, viral_score_menu,
    media_menu, abtest_menu_kb, compmon_menu_kb, product_menu_kb,
    alert_menu_kb, post_menu_kb, translate_menu_kb, dm_menu_kb, users_menu_kb,
    multi_account_menu_kb, acc_manage_menu_kb,
)
from app.bot.middleware import auth_required, error_handler
from app.bot.router import route_callback
from app.bot.session import sessions
from app.settings import TELEGRAM_BOT_TOKEN, ADMIN_IDS

# ── Handler modullarni import qilish (register dekoratori ishlaydi) ──
from app.bot.handlers import start, tahlil, goyalar, ssenariy, ai_sections, admin  # noqa: F401
from app.bot.handlers import memory_handler, competitor_handler, ops_handler  # noqa: F401
from app.bot.handlers import trend_handler, pipeline_handler, coach_handler  # noqa: F401
from app.bot.handlers import media_handler, competitor_monitor, abtest_handler, product_handler  # noqa: F401
from app.bot.handlers import alert_handler, post_handler, user_handler  # noqa: F401
from app.bot.handlers import translate_handler, dm_handler  # noqa: F401
from app.bot.handlers import account_manager, multi_account  # noqa: F401

logger = logging.getLogger("agro_ai.bot.main")


# ════════════════════════════════════════════════════════
# MENYU TEXT HANDLER
# ════════════════════════════════════════════════════════

@auth_required
@error_handler
async def handle_menu_text(update: Update, context) -> None:
    """ReplyKeyboard tugmalarini inline menyularga yo'naltirish."""
    text = update.message.text.strip()

    # Yangi funksiyalar uchun maxsus text handler'lar
    from app.bot.handlers.competitor_monitor import handle_competitor_text
    from app.bot.handlers.abtest_handler import handle_abtest_text
    from app.bot.handlers.product_handler import handle_product_text
    from app.bot.handlers.post_handler import handle_post_text
    from app.bot.handlers.user_handler import handle_user_add_text
    from app.bot.handlers.translate_handler import handle_translate_text
    from app.bot.handlers.dm_handler import handle_dm_text
    from app.bot.handlers.account_manager import handle_account_text
    from app.bot.handlers.multi_account import handle_multi_content_text

    if await handle_competitor_text(update, context):
        return
    if await handle_abtest_text(update, context):
        return
    if await handle_product_text(update, context):
        return
    if await handle_post_text(update, context):
        return
    if await handle_user_add_text(update, context):
        return
    if await handle_account_text(update, context):
        return
    if await handle_multi_content_text(update, context):
        return
    if await handle_translate_text(update, context):
        return
    if await handle_dm_text(update, context):
        return

    menu_map = {
        "📊 TAHLIL":         ("📊 *TAHLIL*\n\nBo'limni tanlang:", tahlil_menu),
        "💡 G'OYALAR":       ("💡 *KONTENT G'OYALAR*\n\nTanlang:", goyalar_menu),
        "🎣 HOOKLAR":        ("🎣 *HOOKLAR*\n\nHook turini tanlang:", hooklar_menu),
        "✍️ SSENARIY":       ("✍️ *SSENARIY*\n\nTanlang:", ssenariy_menu),
        "🎞 VEO PROMPTLAR":  ("🎞 *VEO PROMPTLAR*\n\nSahna tanlang:", veo_menu),
        "🎬 PIPELINE":       ("🎬 *CONTENT PIPELINE*\n\nMavzu tanlang — to'liq paket yaratiladi:", pipeline_menu),
        "📅 REJA":           ("📅 *KONTENT REJA*\n\nTanlang:", reja_menu),
        "📡 TRENDLAR":       ("📡 *TRENDLAR*\n\nTanlang:", trendlar_menu),
        "📦 SOTUV AI":       ("📦 *SOTUV AI*\n\nTanlang:", sotuv_menu),
        "🧠 AUDIENCE AI":    ("🧠 *AUDIENCE AI*\n\nTanlang:", audience_menu),
        "🏆 VIRAL SCORE":    ("🏆 *VIRAL SCORE*\n\nTanlang:", viral_score_menu),
        "📈 O'SISH":         ("📈 *O'SISH ANALIZI*\n\nTanlang:", osish_menu),
        "🎯 KONKURENT":      ("🎯 *KONKURENT TAHLILI*\n\nTanlang:", konkurent_menu),
        "📋 OPS MANAGER":    ("📋 *OPS MANAGER*\n\nTanlang:", ops_menu),
        "📸 MEDIA AI":       ("📸 *MEDIA AI*\n\nRasm/video yuboring yoki tanlang:", media_menu),
        "🧪 A/B TEST":       ("🧪 *A/B TEST*\n\nTanlang:", abtest_menu_kb),
        "🕵️ MONITORING":     ("🕵️ *COMPETITOR MONITORING*\n\nTanlang:", compmon_menu_kb),
        "🛒 MAHSULOTLAR":    ("🛒 *MAHSULOTLAR*\n\nTanlang:", product_menu_kb),
        "🔔 ALERTLAR":       ("🔔 *PROAKTIV ALERTLAR*\n\nTanlang:", alert_menu_kb),
        "📮 POST NAVBAT":    ("📮 *POST NAVBATI*\n\nTanlang:", post_menu_kb),
        "🌐 TARJIMA":        ("🌐 *MULTI-LANGUAGE*\n\nTanlang:", translate_menu_kb),
        "💬 DM JAVOB":       ("💬 *DM AVTOMATIK JAVOB*\n\nTanlang:", dm_menu_kb),
        "📊 MULTI-ACCOUNT":  ("📊 *MULTI-ACCOUNT*\n\nTanlang:", multi_account_menu_kb),
        "🔄 AKKAUNTLAR":     ("🔄 *AKKAUNT BOSHQARUVI*\n\nTanlang:", acc_manage_menu_kb),
        "👥 FOYDALANUVCHILAR": ("👥 *FOYDALANUVCHILAR*\n\nTanlang:", users_menu_kb),
        "🧠 XOTIRA":         ("🧠 *XOTIRA TIZIMI*\n\nTanlang:", memory_menu),
        "📤 EXPORT":         ("📤 *EXPORT*\n\nFormat tanlang:", export_menu),
        "⚙️ SOZLAMALAR":     ("⚙️ *SOZLAMALAR*\n\nTanlang:", sozlamalar_menu),
        "👑 ADMIN":          ("👑 *ADMIN PANEL*\n\nTanlang:", admin_menu),
    }

    if text in menu_map:
        title, kb_fn = menu_map[text]
        await update.message.reply_text(
            title, parse_mode="Markdown", reply_markup=kb_fn()
        )
    else:
        await update.message.reply_text("Menyudan tanlang 👇", reply_markup=main_menu())


# ════════════════════════════════════════════════════════
# BOT SETUP
# ════════════════════════════════════════════════════════

def create_app() -> Application:
    """Telegram Application yaratish."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    from app.bot.handlers.start import cmd_start, cmd_help, cmd_status, cmd_reset, cmd_webapp
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("webapp", cmd_webapp))
    app.add_handler(CommandHandler("dashboard", cmd_webapp))

    # All inline callbacks → router
    app.add_handler(CallbackQueryHandler(route_callback))

    # Media handler (photo/video → content pack)
    from app.bot.handlers.media_handler import handle_media
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    # All text → menu handler (with special text handlers for new features)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_text))

    # Scheduled jobs (morning/evening/daily/weekly)
    try:
        from app.ops.scheduler import OpsScheduler
        scheduler = OpsScheduler()
        scheduler.register_jobs(app)
    except Exception as e:
        logger.warning(f"⚠️ Scheduler xatosi (davom etilmoqda): {e}")

    # Auto PDF reports (weekly/monthly)
    try:
        from app.ops.auto_report import AutoReportScheduler
        auto_report = AutoReportScheduler()
        auto_report.register_jobs(app)
    except Exception as e:
        logger.warning(f"⚠️ Auto Report xatosi (davom etilmoqda): {e}")

    # Competitor monitoring (har 6 soatda)
    try:
        from app.competitors.monitor import CompetitorMonitor
        from app.accounts import accounts as acc_mgr
        from datetime import time as dt_time

        acc = acc_mgr.active
        comp_monitor = CompetitorMonitor(acc.id)

        async def _competitor_scan_job(ctx):
            alerts = await comp_monitor.scan_all()
            if alerts:
                chat_id = ADMIN_IDS[0] if ADMIN_IDS else None
                if chat_id:
                    lines = ["🕵️ *COMPETITOR ALERT*\n"]
                    for a in alerts:
                        lines.append(f"• {a.message}")
                    text = "\n".join(lines)
                    await ctx.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

        jq = app.job_queue
        # Har 6 soatda competitor scan
        jq.run_repeating(_competitor_scan_job, interval=6 * 3600, first=300, name="competitor_scan")
        logger.info("✅ Competitor monitoring job ro'yxatga olindi (har 6 soat)")
    except Exception as e:
        logger.warning(f"⚠️ Competitor monitor xatosi (davom etilmoqda): {e}")

    # Watchdog (health monitoring)
    try:
        from app.ops.watchdog import watchdog
        watchdog.register_jobs(app)
    except Exception as e:
        logger.warning(f"⚠️ Watchdog xatosi (davom etilmoqda): {e}")

    return app


def run_bot() -> None:
    """Botni ishga tushirish."""
    from app.bot.router import get_registered_sections

    app = create_app()

    sections = get_registered_sections()
    logger.info(f"✅ {len(sections)} ta handler ro'yxatga olindi: {sections}")

    print("\n" + "═" * 50)
    print("  🌿 AGRO AI v2.0 — Telegram Bot")
    print(f"  📋 Handler'lar: {len(sections)} ta bo'lim")
    print("  Telegram'da /start yozing")
    print("  To'xtatish: Ctrl+C")
    print("═" * 50 + "\n")

    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()
