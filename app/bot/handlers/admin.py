"""
Agro AI — 👑 ADMIN + ⚙️ SOZLAMALAR + 📤 EXPORT + AKKAUNT CRUD
Multi-account boshqaruvi: qo'shish, tahrirlash, o'chirish, almashtirish.
"""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.accounts import Account, accounts
from app.bot.keyboards import (
    account_switch_keyboard, admin_menu, back_button, export_menu, sozlamalar_menu,
)
from app.bot.middleware import admin_only, error_handler, send_message, send_typing
from app.bot.router import register
from app.bot.session import sessions
from app.settings import (
    ADMIN_IDS, AI_ENABLED, CHROME_PROFILE_DIR, CHROME_USER_DATA_DIR,
    EXPORT_DIR, MAX_REELS, OPENAI_MODEL, TARGET_PROFILE, validate,
)

logger = logging.getLogger("agro_ai.bot.admin")


# ════════════════════════════════════════════════════════
# ⚙️ SOZLAMALAR
# ════════════════════════════════════════════════════════

@register("soz")
@error_handler
async def handle_sozlamalar(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """⚙️ SOZLAMALAR handler."""

    if action == "switch":
        all_accs = accounts.all_accounts
        if len(all_accs) <= 1:
            await send_message(update, "ℹ️ Faqat bitta akkaunt mavjud.", keyboard=back_button())
            return
        await send_message(
            update,
            "🔄 *Akkaunt almashtirish*\n\nTanlang:",
            keyboard=account_switch_keyboard(all_accs),
        )
        return

    if action == "list":
        all_accs = accounts.all_accounts
        lines = ["📋 *AKKAUNTLAR RO'YXATI*\n"]
        for acc in all_accs:
            lines.append(accounts.format_account_short(acc))
        await send_message(update, "\n".join(lines), keyboard=back_button())
        return

    if action == "chrome":
        await send_typing(update, context)
        profile_path = os.path.join(CHROME_USER_DATA_DIR, CHROME_PROFILE_DIR)
        exists = os.path.isdir(profile_path)
        text = (
            f"🔍 *CHROME DIAGNOSTIKA*\n\n"
            f"📁 User Data: `{CHROME_USER_DATA_DIR}`\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n"
            f"✅ Mavjud: {'Ha' if exists else 'YOQ ❌'}\n\n"
            f"🎯 Target: @{TARGET_PROFILE}\n"
            f"🎬 Max reels: {MAX_REELS}\n"
        )
        await send_message(update, text, keyboard=back_button())
        return

    if action == "status":
        issues = validate()
        ai_status = f"✅ {OPENAI_MODEL}" if AI_ENABLED else "❌ off"
        text = (
            f"📊 *TIZIM HOLATI*\n\n"
            f"🌿 Akkaunt: *{accounts.active.instagram}*\n"
            f"📁 Profil: `{CHROME_PROFILE_DIR}`\n"
            f"🤖 AI: {ai_status}\n"
            f"👑 Adminlar: {len(ADMIN_IDS)} ta\n"
            f"🎬 Max reels: {MAX_REELS}\n"
            f"📋 Akkauntlar: {accounts.count} ta\n\n"
        )
        if issues:
            text += "⚠️ *Muammolar:*\n" + "\n".join(f"• {i}" for i in issues)
        else:
            text += "✅ Barcha tekshiruvlar o'tdi."
        await send_message(update, text, keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum sozlama.", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 🔄 ACCOUNT SWITCH (callback: "switch:account_id")
# ════════════════════════════════════════════════════════

@register("switch")
@error_handler
async def handle_switch(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """Akkaunt almashtirish — 1 tugma bilan."""
    account_id = action
    if accounts.switch(account_id):
        acc = accounts.active
        await send_message(
            update,
            f"✅ *Akkaunt almashtirildi!*\n\n"
            f"🌿 {acc.instagram}\n"
            f"🎯 {acc.niche[:50]}\n"
            f"📁 {acc.chrome_profile}",
            keyboard=back_button(),
        )
    else:
        await send_message(update, "❌ Akkaunt topilmadi.", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 👑 ADMIN PANEL
# ════════════════════════════════════════════════════════

@register("admin")
@error_handler
async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """👑 ADMIN handler."""
    user_id = update.effective_user.id
    if not ADMIN_IDS or user_id != ADMIN_IDS[0]:
        await send_message(update, "👑 Bu bo'lim faqat admin uchun.", keyboard=back_button())
        return

    if action == "stats":
        all_sessions = sessions.all_sessions()
        active = sessions.active_count
        text = (
            f"📊 *ADMIN STATISTIKA*\n\n"
            f"👥 Jami sessiyalar: {len(all_sessions)}\n"
            f"✅ Faol: {active}\n"
            f"🌿 Akkauntlar: {accounts.count}\n"
            f"📁 Hisobotlar: {len(os.listdir(str(EXPORT_DIR)))} ta\n"
        )
        await send_message(update, text, keyboard=back_button())
        return

    if action == "users":
        all_sessions = sessions.all_sessions()
        if not all_sessions:
            await send_message(update, "👥 Hech kim botdan foydalanmagan.", keyboard=back_button())
            return
        lines = ["👥 *FOYDALANUVCHILAR*\n"]
        for uid, sess in all_sessions.items():
            status = "✅" if sess.has_data else "⬜"
            lines.append(f"{status} `{uid}`")
        await send_message(update, "\n".join(lines), keyboard=back_button())
        return

    if action == "logs":
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs", "app.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                last_20 = "".join(lines[-20:])
                await send_message(update, f"📋 *LOGLAR*\n\n```\n{last_20[:3000]}\n```", keyboard=back_button())
            except Exception as e:
                await send_message(update, f"❌ Xato: {e}", keyboard=back_button())
        else:
            await send_message(update, "📋 Log topilmadi.", keyboard=back_button())
        return

    if action == "restart":
        await send_message(update, "🔄 _(Hali tayyor emas)_", keyboard=back_button())
        return

    if action == "add_acc":
        # account_manager.py ga yo'naltirish
        from app.bot.handlers.account_manager import handle_accmgr
        await handle_accmgr(update, context, "new")
        return

    if action == "del_acc":
        from app.bot.handlers.account_manager import handle_accmgr
        await handle_accmgr(update, context, "delete")
        return

    await send_message(update, "❓ Noma'lum buyruq.", keyboard=back_button())


# ════════════════════════════════════════════════════════
# 📤 EXPORT
# ════════════════════════════════════════════════════════

@register("export")
@error_handler
async def handle_export(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    """📤 EXPORT handler."""
    chat_id = update.effective_chat.id
    export_path = str(EXPORT_DIR)
    if not os.path.isdir(export_path):
        await send_message(update, "❌ Hisobot papkasi topilmadi.", keyboard=back_button())
        return

    files = os.listdir(export_path)

    if action == "excel":
        xlsx = sorted([f for f in files if f.endswith(".xlsx")], reverse=True)
        if xlsx:
            path = os.path.join(export_path, xlsx[0])
            with open(path, "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=f,
                    filename=xlsx[0], caption="📊 Excel Hisobot")
        else:
            await send_message(update, "❌ Excel topilmadi.", keyboard=back_button())
        return

    if action == "json":
        jsons = sorted([f for f in files if f.endswith(".json")], reverse=True)
        if jsons:
            path = os.path.join(export_path, jsons[0])
            with open(path, "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=f,
                    filename=jsons[0], caption="📁 JSON Export")
        else:
            await send_message(update, "❌ JSON topilmadi.", keyboard=back_button())
        return

    if action == "pdf":
        session = sessions.get(update.effective_user.id)
        if not session.has_data:
            await send_message(update, "⚠️ Avval tahlil o'tkazing.", keyboard=back_button())
            return

        await send_typing(update, context)
        if update.callback_query:
            await update.callback_query.message.reply_text("📄 *PDF yaratilmoqda...*", parse_mode="Markdown")

        import asyncio
        loop = asyncio.get_event_loop()

        def do_pdf():
            from app.export.pdf_report import PDFReportGenerator
            gen = PDFReportGenerator(accounts.active.id, accounts.active.instagram)
            ideas_dicts = [i.to_dict() for i in session.ideas] if session.ideas else []
            return gen.generate_strategy_report(
                stats=session.stats, recommendations=session.recommendations, ideas=ideas_dicts,
            )

        pdf_path = await loop.run_in_executor(None, do_pdf)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                await context.bot.send_document(chat_id=chat_id, document=f,
                    filename=os.path.basename(pdf_path), caption="📄 PDF Hisobot")
        else:
            await send_message(update, "❌ PDF yaratishda xato.", keyboard=back_button())
        return

    await send_message(update, "❓ Noma'lum export.", keyboard=back_button())
